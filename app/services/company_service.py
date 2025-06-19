from fastapi import UploadFile
from typing import List, Dict, Any, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.utils import Parser
from app.models import (
    CsvCompnay,
    CompanyID,
    Language,
    CompanyName,
    Tag,
)
from app.schemas import (
    CompanyInfoResponse,
    CompanyAddRequest,
    TagInfo,
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
        company_id_obj = CompanyID()
        session.add(company_id_obj)
        await session.flush() # ID를 먼저 받아놈
        
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
            )
            session.add(new_company_name)

        if do_commit:
            await session.commit()

        return company_id_obj.id
    
    def _convert_tag_list(
        self,
        tags: List[Dict[str, Dict]]
    ) -> List[Tuple[str, str]]:
        """
        태그 리스트를 중복 제거 후 하나의 list로 변환 [ {tag_lang: taganame}, ... ]
        """
        all_tags: List[Dict[str, str]] = []
        for tag_item in tags:
            tag_name: Dict[str, str] = tag_item["tag_name"]
            for lang, name in tag_name.items():
                if {lang: name} not in all_tags:
                    all_tags.append((lang, name))

        return all_tags

    async def _add_new_tag(
        self,
        session,
        company_id: int,
        new_tag: Tuple[str, str],
        do_commit: bool = True,
    ):
        """
        새로운 태그 추가

        Args:
            - session (AsyncSession): 데이터베이스 세션
            - new_tag (Dict[str, str]): 새로운 태그 정보
        """
        
        # 기존 태그가 검색되면 company_ids에 추가
        lang_type, tag_name = new_tag[0], new_tag[1]
        stmt = select(Tag).join(Language).where(
            Tag.tag_name == tag_name,
            Language.language_type == lang_type,
            # Tag.language_id == Language.id,
        )
        results = await session.execute(stmt)
        tag_obj = results.scalar_one_or_none()

        if tag_obj:
            # company_ids에 존재하지 않는 경우 추가
            if company_id not in tag_obj.company_ids:
                tag_obj.company_ids.append(company_id)
                logger.info(f"Update Tag - lang_type: {lang_type}, tag_name: {tag_name}, company_ids: {tag_obj.company_ids}")

        else:
            # 새롭게 추가
            # Language ID 조회
            lang_id = await session.execute(
                select(Language).where(Language.language_type == lang_type)
            )
            lang_id = lang_id.scalar_one().id

            new_tag_obj = Tag(
                tag_name=tag_name,
                company_ids=[company_id],
                language_id=lang_id,
            )
            session.add(new_tag_obj)
            
            logger.info(f"Add New Tag - lang_type: {lang_type}, tag_name: {tag_name}, company_ids: {new_tag_obj.company_ids}")
        
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
            async for session in db:
                for csv_item in csv_results:
                    new_company: CompanyAddRequest = CompanyAddRequest(
                        company_name={
                            "ko": csv_item.company_ko,
                            "en": csv_item.company_en,
                            "ja": csv_item.company_ja,
                        },
                        tags=[
                            csv_item.tag_ko,
                            csv_item.tag_en,
                            csv_item.tag_ja,
                        ],
                    )

                    await self.add_new_company(new_company, "ko")
        
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
                # 중복 제거 후 하나의 list로 변환 [ (tag_lang, taganame), ... ]
                tags: List[Dict[str, Dict]] = self._convert_tag_list(new_company_info["tags"])
                # 새로운 언어가 있는지 확인 후 추가
                await self._add_new_language(
                    session,
                    input_languages=[x[0] for x in tags],
                    do_commit=False,
                )

                for tag_item in tags:
                    # 새로운 태그 추가
                    await self._add_new_tag(
                        session,
                        company_id=new_company_id,
                        new_tag=tag_item,
                        do_commit=False,
                    )

                    if tag_item[0] == language:
                        results["tags"].append(tag_item[1])

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
        tags: List[TagInfo],
        language: str,
    ):
        pass

    async def delete_tag(
        self,
        compnay_name: str,
        tag: str,
        language: str,
    ):
        pass