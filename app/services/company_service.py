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
        if language in company_info["company_name"].keys():
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
            - results (CompanyResponse): 추가된 회사 정보
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

        # 최종 결과
        company_infos: Dict[Dict[str, Any]] = await company_repository.get_company_info_by_company_id(
            company_id=target_compnay_id,
        )

        # 결과
        if not results["company_name"] and language in company_infos["company_name"].keys():
            results["company_name"] = company_infos["company_name"][language]
            
        for tag_item in company_infos["tags"]:
            if (
                language in tag_item.keys()
                and tag_item.get(language) not in results["tags"]
            ):
                results["tags"].append(tag_item.get(language))

        return results

    async def delete_tag(
        self,
        company_name: str,
        tag: str,
        language: str,
    ):
        """
        6. 회사 태그 정보 삭제
            - 저장 완료 후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력
        """
        results: Dict[str, Any] = {
            "company_name": "",
            "tags": [],
        }

        company_repository: CompanyRepository = CompanyRepository()

        compnay_id: int = await company_repository.get_company_id_by_company_name(
            company_name=company_name,
        )
        if not compnay_id:
            return None

        # 회사 id와 tag_name을 통해 태그 관계 id 조회
        tag_relation_id: int = await company_repository.get_tag_relation_id(
            company_id=compnay_id,
            tag_name=tag,
        )

        if not tag_relation_id:
            return None

        # 태그 관계 id 사용해 삭제
        await company_repository.delete_tag_info(
            tag_rel_id=tag_relation_id,
        )

        # 최종 결과 반환
        company_infos = await company_repository.get_company_info_by_company_id(
            company_id=compnay_id,
        )

        if not results["company_name"] and language in company_infos["company_name"].keys():
            results["company_name"] = company_infos["company_name"][language]

        print(company_infos["tags"])
        for tag_item in company_infos["tags"]:
            if language in tag_item.keys() and tag_item.get(language) not in results["tags"]:
                results["tags"].append(tag_item.get(language))

        return results