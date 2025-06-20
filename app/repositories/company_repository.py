from typing import List, Dict, Any
from sqlalchemy import select, delete

from app.utils import get_db, setup_logger
from app.models import (
    CompanyName,
    CompanyID,
    CompanyNameRelation,
    Tag,
    TagRelation,
    Language,
)

# Logger
logger = setup_logger("Company_Repository")

class CompanyRepository:
    async def get_company_id_by_company_name(
        self,
        company_name: str,
    ):
        """
        회사 이름을 통해 회사 id 조회

        Returns:
            - company_id (int): 회사 id
        """

        company_id: int = 0
        try:
            async for session in get_db():
                # 회사명으로 회사 ID 조회
                stmt = select(
                    CompanyName.company_id,
                ).where(
                    CompanyName.name == company_name,
                )
                db_results = await session.execute(stmt)
                rows = db_results.all()
                for row in rows:
                    company_id = row[0]

        except Exception as e:
            logger.error(f"[ERROR] get_company_id_by_company_name: {e}")
            raise e

        return company_id
    
    async def get_company_info(
        self,
        company_name: str,
    ):
        """
        회사 이름을 통해 정보 가져오기

        Returns:
            [
                {
                    "lang_id": int,
                    "lang_type": string,
                    "company_id": integer,
                    "company_name": string,
                    "rel_id": integer,
                }, ...
            ]
        """
        company_infos: List[Dict[str, str]] = []
        
        try:
            async for session in get_db():
                stmt = select(
                    CompanyName,
                    Language,
                ).join(
                    Language,
                    Language.id == CompanyName.language_id,
                ).where(
                    CompanyName.name == company_name,
                )
                results = await session.execute(stmt)
                rows = results.all()

                for row in rows:
                    company_obj: CompanyName = row[0]
                    language_obj: Language = row[1]

                    company_infos.append({
                        "lang_id": language_obj.id,
                        "lang_type": language_obj.language_type,
                        "company_id": company_obj.company_id,
                        "company_name": company_obj.name,
                        "rel_id": company_obj.rel_id,
                    })

        except Exception as e:
            logger.error(f"[ERROR] get_company_info: {e}")
            raise e
        
        return company_infos

    async def get_company_info_by_company_id(
        self,
        company_id: int,
    ):
        """
        회사 id를 통해 국가별 회사명, 태그 조회
        
        Returns:
        {
            "id": company_id,
            "company_name": {
                "lang_type": compnayname, 
            },
            "tags": [
                {"lang_type": tag_name},
                ...
            ]
        }
        """
        company_infos: Dict[Dict[str, Any]] = {
            "id": company_id,
            "company_name": {},
            "tags": [],
        }

        try:
            async for session in get_db():
                stmt = select(
                    CompanyName,
                    Tag,
                    Language,
                ).join(
                    Tag,
                    Tag.company_id == CompanyName.company_id,
                ).join(
                    Language,
                    Language.id == CompanyName.language_id,
                ).where(
                    CompanyName.company_id == company_id,
                    Language.id == Tag.language_id
                )
                db_results = await session.execute(stmt)
                rows = db_results.all()
                
                for row in rows:
                    company_name_obj: CompanyName = row[0]
                    tag_obj: Tag = row[1]
                    language_obj: Language = row[2]
                    
                    # company_name 추가
                    if language_obj.language_type not in company_infos["company_name"].keys():
                        company_infos["company_name"][language_obj.language_type] = company_name_obj.name
                    
                    # tag 추가
                    tag_info = {
                        language_obj.language_type: tag_obj.tag_name,
                    }
                    if tag_info not in company_infos["tags"]:
                        company_infos["tags"].append(tag_info)

        except Exception as e:
            logger.error(f"[ERROR] get_company_info_by_company_name: {e}")

        return company_infos
    

    async def add_new_language(
        self,
        input_languages: List[str],
    ):
        """
        기존 언어 확인 후 새로운 언어 추가
        """

        try:
            async for session in get_db():
                # 기존 언어 조회
                result = await session.execute(select(Language))
                enrolled_languages = result.all()
                enrolled_languages = [x[0].language_type for x in enrolled_languages]
                
                # 새로운 언어 추가
                new_languages: List[str] = list(set(input_languages) - set(enrolled_languages))
                for lang in new_languages:
                    new_language = Language(language_type=lang)
                    session.add(new_language)

                await session.commit()
            
        except Exception as e:
            logger.error(f"[ERROR] add_new_language: {e}")
            raise e

    async def add_new_company(
        self,
        new_companies: Dict[str, str],
    ):
        """
        새로운 회사 추가
        
        Returns:
            - company_id (int): 새로운 회사 ID
        """

        company_id: int = 0
        try:
            async for session in get_db():
                # tbl_company_ids 테이블에 새로운 회사 ID 추가
                company_id_obj = CompanyID()
                session.add(company_id_obj)
                await session.flush() # id 먼저 받기

                # tbl_company_name_relations 테이블에 새로운 회사 이름 관계 추가
                tbl_company_name_relations = CompanyNameRelation(
                    name_ids=[],
                    company_id=company_id_obj.id,
                )
                session.add(tbl_company_name_relations)
                await session.flush() # id 먼저 받기

                # tbl_company_names 테이블에 새로운 회사 이름 추가
                for lang_type, name in new_companies.items():
                    # Language ID 조회
                    lang_id = await session.execute(
                        select(Language).where(Language.language_type == lang_type)
                    )
                    lang_id = lang_id.scalar_one().id

                    # 새롭게 추가
                    new_company_name = CompanyName(
                        name=name,
                        company_id=company_id_obj.id,
                        language_id=lang_id,
                        rel_id=tbl_company_name_relations.id,
                    )
                    session.add(new_company_name)
                    await session.flush() # id 먼저 받기

                    # 관계 추가
                    tbl_company_name_relations.name_ids.append(new_company_name.id)

                company_id = company_id_obj.id
                await session.commit()

        except Exception as e:
            logger.error(f"[ERROR] add_new_company: {e}")
            raise e

        return company_id
    

    async def add_new_tag(
        self,
        company_id: int,
        new_tag: Dict[str, str],
    ):
        """
        새로운 태그 추가
        """
        try:
            async for session in get_db():
                # tbl_tab_realtions 정보 추가
                tag_relations = TagRelation(
                    tag_ids=[],
                    company_id=company_id,
                )
                session.add(tag_relations)
                await session.flush() # id 먼저 받기

                # 새롭게 추가
                for lang_type, tag_name in new_tag.items():
                    lang_id = await session.execute(
                        select(Language).where(Language.language_type == lang_type)
                    )
                    lang_id = lang_id.scalar_one().id

                    new_tag_obj = Tag(
                        tag_name=tag_name,
                        company_id=company_id,
                        rel_id=tag_relations.id,
                        language_id=lang_id,
                    )
                    session.add(new_tag_obj)
                    await session.flush() # id 먼저 받기
                    
                    # 관계 추가
                    tag_relations.tag_ids.append(new_tag_obj.id)

                await session.commit()
            
        except Exception as e:
            logger.error(f"[ERROR] add_new_tag: {e}")
            raise e
    
    
    async def delete_tag_info(
        self,
        tag_id: int,
        tag_rel_id: int,
    ):
        """
        태그 정보 삭제
            - tag_id, tag_rel_id를 기반으로 삭제
            - tbl_tags, tbl_tag_relations 에서 삭제
        """
        try:
            async for session in get_db():
                # tbl_tags
                stmt = delete(
                    Tag,
                ).where(
                    Tag.rel_id == tag_rel_id,
                )
                await session.execute(stmt)

                # tbl_tag_relations -> tag_ids에서 삭제
                stmt = select(
                    TagRelation,
                ).where(
                    TagRelation.id == tag_rel_id,
                )
                results = await session.execute(stmt)
                tag_relation_obj: TagRelation = results.scalar_one()
                tag_relation_obj.tag_ids.remove(tag_id)

                # 만약 tag_ids가 비어있다면 row 삭제
                if not tag_relation_obj.tag_ids:
                    stmt = delete(
                        TagRelation,
                    ).where(
                        TagRelation.id == tag_rel_id
                    )
                    await session.execute(stmt)

                await session.commit()
            
        except Exception as e:
            logger.error(f"[ERROR] delete_tag_info: {e}")
            raise e


    async def get_tag_info(
        self,
        company_id: int,
    ):
        """
        회사 ID를 통해 태그 정보 가져오기
        
        Returns:
        [
            {
                "company_name": string,
                "company_lang_id": integer,
                "lang_id": integer,
                "lang_type": string,
                "tag_id": integer,
                "tag_name": string,
                "rel_id": integer,
            }
        ]   
        """
        tag_infos: List[Dict[str, Any]] = []
        try:
            async for session in get_db():
                stmt = select(
                    Tag,
                    Language,
                    CompanyName,
                ).join(
                    Language,
                    Language.id == Tag.language_id,
                ).join(
                    CompanyName,
                    CompanyName.company_id == Tag.company_id,
                ).where(
                    Tag.company_id == company_id,
                    CompanyName.company_id == company_id,
                )
                results = await session.execute(stmt)
                rows = results.all()
                
                for row in rows:
                    tag_obj: Tag = row[0]
                    language_obj: Language = row[1]
                    company_name_obj: CompanyName = row[2]
                    
                    tag_infos.append({
                        "company_name": company_name_obj.name,
                        "company_lang_id": company_name_obj.language_id,
                        "lang_id": language_obj.id,
                        "lang_type": language_obj.language_type,
                        "tag_id": tag_obj.id,
                        "tag_name": tag_obj.tag_name,
                        "rel_id": tag_obj.rel_id,
                    })
            
        except Exception as e:
            logger.error(f"[ERROR] get_tag_info: {e}")
            raise e

        return tag_infos