from fastapi import UploadFile
from typing import List, Dict, Any, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.utils import Parser
from app.models import (
    CsvCompnay,
    CompanyID,
    CompanyName,
    CompanyNameRelation,
    Language,
    Tag,
    TagRelation, 
)
from app.utils import get_db, setup_logger

# Logger
logger = setup_logger("Company_Service")

class CompanyService:
    async def _add_new_language(
        self,
        session,
        input_languages: List[str],
        do_commit: bool = True
    ):
        """기존 언어 확인 후 새로운 언어 추가"""
        # 기존 언어 조회
        result = await session.execute(select(Language))
        enrolled_languages = result.all()
        enrolled_languages = [x[0].language_type for x in enrolled_languages]
        
        # 새로운 언어 추가
        new_languages: List[str] = list(set(input_languages) - set(enrolled_languages))
        for lang in new_languages:
            new_language = Language(language_type=lang)
            session.add(new_language)

        if do_commit:
            await session.commit()

    async def _add_company_name(
        self, 
        session, 
        new_companies: Dict[str, str],
        do_commit: bool = True,
    ):
        """
        새로운 회사 추가
        
        Args:
            - session (AsyncSession): 데이터베이스 세션
            - new_companies (Dict[str, str]): 새로운 회사 정보

        Returns:
            - company_id (int): 새로운 회사 ID
        """
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

        if do_commit:
            await session.commit()

        return company_id_obj.id
    

    async def _add_new_tag(
        self,
        session,
        company_id: int,
        new_tag: Dict[str, str],
        do_commit: bool = True,
    ):
        """
        새로운 태그 추가

        Args:
            - session (AsyncSession): 데이터베이스 세션
            - new_tag (Dict[str, str]): 새로운 태그 정보
        """
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
        
        if do_commit:
            await session.commit()
        

    async def add_company_from_csv(
        self,
        file_path: str,
    ):
        """
        업로드된 csv 파일 업로드 처리
        """
        parser: Parser = Parser()
        csv_results: List[CsvCompnay] = await parser.parse_csv_by_file_path(file_path)

        db = get_db()
        try:
            pass 
            # async for session in db:
            #     for csv_item in csv_results:
            #         new_company: Dict[str, Any] = (
            #             company_name={
            #                 "ko": csv_item.company_ko,
            #                 "en": csv_item.company_en,
            #                 "ja": csv_item.company_ja,
            #             },
            #             tags=[
            #                 csv_item.tag_ko,
            #                 csv_item.tag_en,
            #                 csv_item.tag_ja,
            #             ],
            #         )

            #         await self.add_new_company(new_company, "ko")
        
        except Exception as e:
            raise e
        
        finally:
            await db.aclose()
        
        return


    async def get_company_info(
        self,
        company_name: str,
        language: str,
    ):
        """
        회사명을 검색해서 해당 정보 모두 가져옴

        Args:
            - company_name (str): 검색할 회사명
            - language (str): 출력 언어
            
        Returns:
            - results (Dict[str, str]): 회사명과 태그 정보
        """
        results = {
            "company_name": "",
            "tags": [],
        }
        
        db = get_db()
        try:
            async for session in db:
                stmt = select(
                    CompanyName,
                    Tag,
                    Language,
                ).where(
                    CompanyName.name == company_name,
                    Language.language_type == language,
                    CompanyName.language_id == Language.id,
                    Tag.language_id == Language.id,
                )
                
                db_results = await session.execute(stmt)
                rows = db_results.all()

                # 검색 결과가 없음 -> 404 Return
                if not rows:
                    return None

                for row in rows:
                    company_name_obj = row[0]  # CompanyName 객체
                    tag_obj = row[1]  # Tag 객체

                    if not results["company_name"]:
                        results["company_name"] = company_name_obj.name
                    
                    results["tags"].append(tag_obj.tag_name)                    

        except Exception as e:
            logger.error(f"[ERROR] get_company_info: {e}")
            raise e

        finally:
            await db.aclose()
            
        return results

    async def add_new_company(
        self,
        new_company_info: Dict[str, Any],
        language: str,
    ):
        """
        - 새로운 회사 추가
            - 회사 정보에 새로운 언어가 있다면 추가
        
        Args:
            - new_company (Dict[str, Any]): 새로운 회사 정보
            - language (str): 출력 언어

        Returns:
            - results (CompanyAddResponse): 추가된 회사 정보
        """
        results: Dict[str, Any] = {
            "company_name": "",
            "tags": [],
        }
        db = get_db()
        try:
            async for session in db:
                # Company Name
                company_names: Dict[str, str] = new_company_info["company_name"]
                results["company_name"] = company_names[language]

                # 새로운 언어가 있는지 확인 후 추가
                await self._add_new_language(
                    session, 
                    input_languages=list(company_names.keys()), 
                    do_commit=False,
                )

                # 새로운 회사 추가
                new_company_id: int = await self._add_company_name(
                    session,
                    new_companies=company_names,
                    do_commit=False,
                )

                # Tags
                tags: List[Dict[str, Dict]] = new_company_info.get("tags")
                for tag_item in tags:
                    tag_name_obj: Dict[str, str] = tag_item.get("tag_name")
                    
                    # 새로운 언어가 있는지 확인 후 추가
                    await self._add_new_language(
                        session,
                        input_languages=list(tag_name_obj.keys()),
                        do_commit=False,
                    )

                    # 새로운 태그 추가
                    await self._add_new_tag(
                        session,
                        company_id=new_company_id,
                        new_tag=tag_name_obj,
                        do_commit=False,
                    )

                    for lang, tag_name in tag_item.items():
                        if lang == language:
                            results["tags"].append(tag_name)

                # 최종 커밋
                await session.commit()

        except Exception as e:
            logger.error(f"[ERROR] add_new_company: {e}")
            raise e
        
        finally:
            await db.aclose()
        
        return results
    
    async def add_new_tag(
        self,
        compnay_name: str,
        tags: List[Dict[str, str]],
        language: str,
    ):
        """
        5. 회사 태그 정보 추가
        - 저장 완료 후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력
        """
        results: List[str] = []
        db = get_db()
        try:
            async for session in db:
                # 중복 제거 후 하나의 list로 변환 [ (tag_lang, taganame), ... ]
                print(tags)
                new_tags: List[Tuple[str, str]] = self._convert_tag_list(tags)

                print(new_tags)

        except Exception as e:
            logger.error(f"[ERROR] add_new_tag: {e}")
            raise e

        finally:
            await db.aclose()

        return {
            "company_name": compnay_name,
            "tags": results,
        }

    async def delete_tag(
        self,
        compnay_name: str,
        tag: str,
        language: str,
    ):
        pass