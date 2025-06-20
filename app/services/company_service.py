from fastapi import UploadFile
from typing import List, Dict, Any

from sqlalchemy import select, delete

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
        
    async def _get_compnay_info(
        self,
        session,
        compnay_name: str,
    ):
        """
        회사 이름을 통해 정보 가져오기
        """
        stmt = select(
            CompanyName,
            Language,
        ).join(
            Language,
            Language.id == CompanyName.language_id,
        ).where(
            CompanyName.name == compnay_name,
        )
        results = await session.execute(stmt)
        rows = results.all()

        """
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
        
        return company_infos
    
    async def _get_tag_info(
        self,
        session,
        company_id: int,
    ):
        """
        회사 ID를 통해 태그 정보 가져오기
        """
        stmt = select(
            Tag,
            Language,
            CompanyName,
        ).join(
            Language,
            Language.id == Tag.language_id,
        ).where(
            Tag.company_id == company_id,
            CompanyName.company_id == company_id,
        )
        results = await session.execute(stmt)
        rows = results.all()

        """
        [
            "compnay_name": string,
            "lang_id": integer,
            "lang_type": string,
            "tag_id": integer,
            "tag_name": string,
            "rel_id": integer,
        ]   
        """
        tag_infos: List[Dict[str, Any]] = []
        for row in rows:
            tag_obj: Tag = row[0]
            language_obj: Language = row[1]
            company_name_obj: CompanyName = row[2]
            
            tag_infos.append({
                "company_name": company_name_obj.name,
                "lang_id": language_obj.id,
                "lang_type": language_obj.language_type,
                "tag_id": tag_obj.id,
                "tag_name": tag_obj.tag_name,
                "rel_id": tag_obj.rel_id,
            })

        return tag_infos
    

    async def _delete_tag_info(
        self,
        session,
        tag_id: int,
        tag_rel_id: int,
        do_commit: bool = True
    ):
        """
        태그 정보 삭제
            - tag_id, tag_rel_id를 기반으로 삭제
            - tbl_tags, tbl_tag_relations 에서 삭제
        """

        # tbl_tags
        stmt = delete(
            Tag,
        ).where(
            Tag.id == tag_id,
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
        logger.debug(f"[DEBUG] add_new_tag: {compnay_name}, {tags}, {language}")

        results: Dict[str, Any] = {
            "company_name": "",
            "tags": [],
        }
        db = get_db()
        try:
            async for session in db:
                # 회사 존재하는 지 확인
                company_infos = await self._get_compnay_info(
                    session,
                    compnay_name,
                )
                
                if not company_infos:
                    return None
                
                # 해당 회사의 company_id에 태그 추가
                target_compnay_id: int = company_infos[0]["company_id"]
                for tag_item in tags:
                    tag_name_obj: Dict[str, str] = tag_item.tag_name
                    
                    # 새로운 언어가 있는지 확인 후 추가
                    await self._add_new_language(
                        session,
                        input_languages=list(tag_name_obj.keys()),
                        do_commit=False,
                    )

                    # 새로운 태그 추가
                    await self._add_new_tag(
                        session,
                        company_id=target_compnay_id,
                        new_tag=tag_name_obj,
                        do_commit=False,
                    )
                
                # 최종 커밋
                await session.commit()

                # compay_id, language에 따른 tag 결과 출력
                tag_infos: List[Dict[str, Any]] = await self._get_tag_info(
                    session,
                    company_id=target_compnay_id,
                )
                for tag_item in tag_infos:
                    if tag_item["lang_type"] == language:
                        if not results["company_name"]:
                            results["company_name"] = tag_item["company_name"]
                        results["tags"].append(tag_item["tag_name"])

        except Exception as e:
            logger.error(f"[ERROR] add_new_tag: {e}")
            raise e

        finally:
            await db.aclose()

        results["tags"] = list(set(results["tags"])) # 중복제거
        return results

    async def delete_tag(
        self,
        compnay_name: str,
        tag: str,
        language: str,
    ):
        """
        6. 회사 태그 정보 삭제
            - 저장 완료 후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력
        """
        logger.debug(f"delete_tag: {compnay_name}, {tag}, {language}")

        results: Dict[str, Any] = {
            "company_name": "",
            "tags": [],
        }

        db = get_db()
        try:
            async for session in db:
                compnay_infos: List[Dict[str, Any]] = await self._get_compnay_info(
                    session,
                    compnay_name,
                )

                if not compnay_infos:
                    return None

                # 회사 id를 통해 태그 정보 조회
                target_compnay_id: int = compnay_infos[0]["company_id"]
                tag_infos = await self._get_tag_info(
                    session,
                    company_id=target_compnay_id,
                )
                delete_tag_ids: List[int] = []
                for tag_item in tag_infos:
                    if tag_item["tag_name"] == tag:
                        delete_tag_ids.append((tag_item["tag_id"], tag_item["rel_id"]))
                delete_tag_ids = list(set(delete_tag_ids))

                # tag_name이 일치하면 tag_id를 기반으로 삭제
                # tag_realtions 도 삭제
                for tag_id, rel_id in delete_tag_ids:
                    await self._delete_tag_info(
                        session,
                        tag_id=tag_id,
                        tag_rel_id=rel_id,
                        do_commit=False,
                    )
                    logger.debug(f"delete_tag_info: tag_id: {tag_id}, rel_id: {rel_id}")
                
                # 최종 커밋
                await session.commit()

                # 최종 결과 반환
                tag_infos = await self._get_tag_info(
                    session,
                    company_id=target_compnay_id,
                )
                for tag_item in tag_infos:
                    if tag_item["lang_type"] == language:
                        if not results["company_name"]:
                            results["company_name"] = tag_item["company_name"]
                        results["tags"].append(tag_item["tag_name"])
    
        except Exception as e:
            logger.error(f"[ERROR] delete_tag: {e}")
        
        finally:
            await db.aclose()

        results["tags"] = list(set(results["tags"])) # 중복제거
        return results