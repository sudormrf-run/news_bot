# -*- coding: utf-8 -*-
"""
GitHub Discussions Publisher
"""

import requests
from typing import Optional, Dict, Any

from .base import BasePublisher
from ..config import Config
from ..logger import logger


class GitHubPublisher(BasePublisher):
    """GitHub Discussions에 게시하는 Publisher"""
    
    GRAPHQL_URL = "https://api.github.com/graphql"
    
    def __init__(
        self,
        token: Optional[str] = None,
        repo: Optional[str] = None,
        org: Optional[str] = None,
        category: Optional[str] = None
    ):
        """
        Args:
            token: GitHub Personal Access Token
            repo: 저장소 (owner/name 형식) - Repository discussions용
            org: Organization 이름 - Organization discussions용 (.github repo 사용)
            category: Discussion 카테고리 이름
        """
        super().__init__("GitHub")
        self.token = token or Config.GITHUB_TOKEN
        self.repo = repo or Config.GH_REPO
        self.org = org or Config.GH_ORG
        self.category = category or Config.GH_DISCUSSION_CATEGORY
        
        # Organization 모드인지 Repository 모드인지 확인
        # repo가 직접 지정되면 그걸 사용, org만 있으면 org 모드
        self.is_org_mode = bool(self.org) and not repo
        
        # Organization 모드일 경우 repo 설정
        if self.is_org_mode:
            org_repo = Config.GH_ORG_REPO or "community"
            self.repo = f"{self.org}/{org_repo}"
    
    def validate_config(self) -> bool:
        """설정 유효성 검사"""
        return all([self.token, self.repo or self.org, self.category])
    
    def publish(self, content: str, **kwargs) -> bool:
        """GitHub Discussion 게시
        
        Args:
            content: 마크다운 콘텐츠
            title: Discussion 제목 (필수)
        
        Returns:
            게시 성공 여부
        """
        title = kwargs.get('title')
        if not title:
            logger.error("GitHub Discussion 제목이 없음")
            return False
        
        try:
            url = self._create_discussion(title, content)
            if url:
                logger.info(f"GitHub Discussion 생성 완료: {url}")
                # 결과에 URL 저장
                kwargs['discussion_url'] = url
                return True
            return False
            
        except Exception as e:
            logger.error(f"GitHub Discussion 게시 실패: {str(e)}", exc_info=True)
            return False
    
    def _create_discussion(self, title: str, body: str) -> Optional[str]:
        """Discussion 생성 및 URL 반환
        
        Args:
            title: Discussion 제목
            body: Discussion 본문 (마크다운)
        
        Returns:
            생성된 Discussion URL (실패 시 None)
        """
        if self.is_org_mode:
            # Organization discussions
            org_id, category_id = self._get_org_and_category_ids(self.org)
            if not org_id or not category_id:
                return None
            target_id = org_id
        else:
            # Repository discussions
            if '/' not in self.repo:
                logger.error(f"잘못된 저장소 형식: {self.repo}")
                return None
            
            owner, name = self.repo.split('/', 1)
            repo_id, category_id = self._get_repo_and_category_ids(owner, name)
            if not repo_id or not category_id:
                return None
            target_id = repo_id
        
        # Discussion 생성
        mutation = """
        mutation($targetId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
            createDiscussion(input: {
                repositoryId: $targetId,
                categoryId: $categoryId,
                title: $title,
                body: $body
            }) {
                discussion {
                    url
                }
            }
        }
        """
        
        variables = {
            "targetId": target_id,
            "categoryId": category_id,
            "title": title,
            "body": body
        }
        
        try:
            data = self._graphql_request(mutation, variables)
            return data["createDiscussion"]["discussion"]["url"]
        except Exception as e:
            logger.error(f"Discussion 생성 실패: {str(e)}")
            return None
    
    def _get_org_and_category_ids(self, org_login: str) -> tuple[Optional[str], Optional[str]]:
        """Organization의 .github repository ID와 카테고리 ID 조회
        
        Args:
            org_login: Organization 로그인 이름
        
        Returns:
            (Repository ID, 카테고리 ID) 튜플
        """
        # Organization의 .github repository를 사용
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                id
                discussionCategories(first: 100) {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
        """
        
        # repo에서 owner와 name 분리
        if '/' in self.repo:
            owner, name = self.repo.split('/', 1)
        else:
            owner, name = org_login, Config.GH_ORG_REPO or ".github"
        
        variables = {
            "owner": owner,
            "name": name
        }
        
        try:
            data = self._graphql_request(query, variables)
            repo_id = data["repository"]["id"]
            
            # 카테고리 찾기
            categories = data["repository"]["discussionCategories"]["nodes"]
            category_id = None
            
            for cat in categories:
                if cat["name"] == self.category:
                    category_id = cat["id"]
                    break
            
            if not category_id:
                logger.error(f"Organization repository 카테고리를 찾을 수 없음: {self.category}")
                available = [cat["name"] for cat in categories]
                logger.info(f"사용 가능한 카테고리: {', '.join(available)}")
            
            return repo_id, category_id
            
        except Exception as e:
            logger.error(f"Organization repository/카테고리 정보 조회 실패: {str(e)}")
            return None, None
    
    def _get_repo_and_category_ids(self, owner: str, name: str) -> tuple[Optional[str], Optional[str]]:
        """저장소 ID와 카테고리 ID 조회
        
        Args:
            owner: 저장소 소유자
            name: 저장소 이름
        
        Returns:
            (저장소 ID, 카테고리 ID) 튜플
        """
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                id
                discussionCategories(first: 100) {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
        """
        
        variables = {
            "owner": owner,
            "name": name
        }
        
        try:
            data = self._graphql_request(query, variables)
            repo_id = data["repository"]["id"]
            
            # 카테고리 찾기
            categories = data["repository"]["discussionCategories"]["nodes"]
            category_id = None
            
            for cat in categories:
                if cat["name"] == self.category:
                    category_id = cat["id"]
                    break
            
            if not category_id:
                logger.error(f"카테고리를 찾을 수 없음: {self.category}")
                available = [cat["name"] for cat in categories]
                logger.info(f"사용 가능한 카테고리: {', '.join(available)}")
            
            return repo_id, category_id
            
        except Exception as e:
            logger.error(f"저장소/카테고리 정보 조회 실패: {str(e)}")
            return None, None
    
    def _graphql_request(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """GitHub GraphQL API 요청
        
        Args:
            query: GraphQL 쿼리/뮤테이션
            variables: 변수
        
        Returns:
            응답 데이터
        
        Raises:
            RuntimeError: API 오류 시
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        response = requests.post(
            self.GRAPHQL_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "errors" in result:
            error_messages = [err.get("message", "Unknown error") for err in result["errors"]]
            raise RuntimeError(f"GitHub GraphQL 오류: {'; '.join(error_messages)}")
        
        return result.get("data", {})
    
    def list_discussions(self, limit: int = 10) -> list[Dict[str, Any]]:
        """최근 Discussion 목록 조회
        
        Args:
            limit: 조회할 개수
        
        Returns:
            Discussion 정보 리스트
        """
        if self.is_org_mode:
            # Organization의 .github repository discussions
            query = """
            query($owner: String!, $name: String!, $limit: Int!) {
                repository(owner: $owner, name: $name) {
                    discussions(first: $limit, orderBy: {field: CREATED_AT, direction: DESC}) {
                        nodes {
                            title
                            url
                            createdAt
                            category {
                                name
                            }
                        }
                    }
                }
            }
            """
            
            # repo에서 owner와 name 분리
            if '/' in self.repo:
                owner, name = self.repo.split('/', 1)
            else:
                owner, name = self.org, Config.GH_ORG_REPO or ".github"
            
            variables = {
                "owner": owner,
                "name": name,
                "limit": limit
            }
            
            try:
                data = self._graphql_request(query, variables)
                return data["repository"]["discussions"]["nodes"]
            except Exception as e:
                logger.error(f"Organization repository Discussion 목록 조회 실패: {str(e)}")
                return []
        else:
            # Repository discussions
            if '/' not in self.repo:
                return []
            
            owner, name = self.repo.split('/', 1)
            
            query = """
            query($owner: String!, $name: String!, $limit: Int!) {
                repository(owner: $owner, name: $name) {
                    discussions(first: $limit, orderBy: {field: CREATED_AT, direction: DESC}) {
                        nodes {
                            title
                            url
                            createdAt
                            category {
                                name
                            }
                        }
                    }
                }
            }
            """
            
            variables = {
                "owner": owner,
                "name": name,
                "limit": limit
            }
            
            try:
                data = self._graphql_request(query, variables)
                return data["repository"]["discussions"]["nodes"]
            except Exception as e:
                logger.error(f"Repository Discussion 목록 조회 실패: {str(e)}")
                return []