from typing import List, Dict, Any

from app.repositories import CompanyRepository
from app.utils import setup_logger

# Logger
logger = setup_logger("Company_Service")

class CompanyService:
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
        
        company_repository: CompanyRepository = CompanyRepository()

        # 회사아이디 조회
        company_id: int = await company_repository.get_company_id_by_company_name(
            company_name=company_name,
        )

        if not company_id:
            return None

        # 회사 아이디를 통해 태그 조회
        company_info = await company_repository.get_company_info_by_company_id(
            company_id=company_id,
        )

        # 결과 반환
        results["company_name"] = company_info["company_name"][language]
        for tag_info in company_info["tags"]:
            if language in tag_info.keys():
                results["tags"].append(tag_info[language])
        
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

        company_repository: CompanyRepository = CompanyRepository()
        company_names: Dict[str, str] = new_company_info["company_name"]
        results["company_name"] = company_names[language]

        # 새로운 언어가 있는지 확인 후 추가
        await company_repository.add_new_language(
            input_languages=list(company_names.keys()), 
        )

        # 새로운 회사 추가
        new_company_id: int = await company_repository.add_new_company(
            new_companies=company_names,
        )

        # Tags
        tags: List[Dict[str, Dict]] = new_company_info["tags"]
        for tag_item in tags:
            tag_name_obj: Dict[str, str] = tag_item["tag_name"]
            
            # 새로운 언어가 있는지 확인 후 추가
            await company_repository.add_new_language(
                input_languages=list(tag_name_obj.keys()),
            )

            # 새로운 태그 추가
            await company_repository.add_new_tag(
                company_id=new_company_id,
                new_tag=tag_name_obj,
            )

            for lang, tag_name in tag_name_obj.items():
                if lang == language:
                    results["tags"].append(tag_name)
        
        return results
    
    async def add_new_tag(
        self,
        company_name: str,
        tags: List[Dict[str, str]],
        language: str,
    ):
        """
        5. 회사 태그 정보 추가
            - 저장 완료 후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력
        """
        logger.debug(f"[DEBUG] add_new_tag: {company_name}, {tags}, {language}")

        results: Dict[str, Any] = {
            "company_name": "",
            "tags": [],
        }

        company_repository: CompanyRepository = CompanyRepository()
        
        # 회사 존재하는 지 확인
        company_infos = await company_repository.get_company_info(
            company_name=company_name,
        )

        if not company_infos:
            return None

        # 해당 회사의 company_id에 태그 추가
        target_compnay_id: int = company_infos[0]["company_id"]
        for tag_item in tags:
            tag_name_obj: Dict[str, str] = tag_item.tag_name
            
            # 새로운 언어가 있는지 확인 후 추가
            await company_repository.add_new_language(
                input_languages=list(tag_name_obj.keys()),
            )

            # 새로운 태그 추가
            await company_repository.add_new_tag(
                company_id=target_compnay_id,
                new_tag=tag_name_obj,
            )

            # compay_id, language에 따른 tag 결과 출력
            tag_infos: List[Dict[str, Any]] = await self._get_tag_info(
                company_id=target_compnay_id,
            )
            for tag_item in tag_infos:
                if tag_item["lang_type"] == language:
                    if not results["company_name"]:
                        results["company_name"] = tag_item["company_name"]
                    results["tags"].append(tag_item["tag_name"])

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

        company_repository: CompanyRepository = CompanyRepository()
        
        compnay_infos: List[Dict[str, Any]] = await company_repository.get_company_info(
            compnay_name,
        )

        if not compnay_infos:
            return None

        # 회사 id를 통해 태그 정보 조회
        target_compnay_id: int = compnay_infos[0]["company_id"]
        tag_infos = await company_repository.get_tag_info(
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
            await company_repository.delete_tag_info(
                tag_id=tag_id,
                tag_rel_id=rel_id,
            )
            logger.debug(f"delete_tag_info: tag_id: {tag_id}, rel_id: {rel_id}")
        

        # 최종 결과 반환
        tag_infos = await company_repository.get_tag_info(
            company_id=target_compnay_id,
        )

        for tag_item in tag_infos:
            if tag_item["lang_type"] == language:
                if not results["company_name"]:
                    results["company_name"] = tag_item["company_name"]
                results["tags"].append(tag_item["tag_name"])
    

        results["tags"] = list(set(results["tags"])) # 중복제거
        return results