# -*- coding: utf-8 -*-
"""
Summarizer Factory 모듈
적절한 Summarizer를 선택하고 생성하는 팩토리 패턴 구현
"""

from typing import Optional, Dict, Type
from enum import Enum

from .summarizers.base import BaseSummarizer
from .summarizers.smol_ai_news import SmolAINewsSummarizer
from .summarizers.weekly_robotics import WeeklyRoboticsSummarizer
from .logger import logger


class NewsSource(Enum):
    """지원하는 뉴스 소스"""
    SMOL_AI_NEWS = "smol_ai_news"
    WEEKLY_ROBOTICS = "weekly_robotics"
    # 향후 추가 예정
    # HACKER_NEWS = "hacker_news"
    # TECH_CRUNCH = "tech_crunch"
    # THE_VERGE = "the_verge"


class SummarizerFactory:
    """Summarizer 생성을 담당하는 팩토리 클래스"""
    
    # 등록된 Summarizer 매핑
    _summarizers: Dict[NewsSource, Type[BaseSummarizer]] = {
        NewsSource.SMOL_AI_NEWS: SmolAINewsSummarizer,
        NewsSource.WEEKLY_ROBOTICS: WeeklyRoboticsSummarizer,
    }
    
    @classmethod
    def create(
        cls,
        source: NewsSource,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseSummarizer:
        """지정된 소스에 맞는 Summarizer 생성
        
        Args:
            source: 뉴스 소스 타입
            api_key: API 키 (선택)
            model: 사용할 모델 (선택)
        
        Returns:
            생성된 Summarizer 인스턴스
        
        Raises:
            ValueError: 지원하지 않는 소스인 경우
        """
        if source not in cls._summarizers:
            raise ValueError(f"지원하지 않는 뉴스 소스: {source.value}")
        
        summarizer_class = cls._summarizers[source]
        logger.info(f"{source.value} Summarizer 생성 중...")
        
        return summarizer_class(api_key=api_key, model=model)
    
    @classmethod
    def create_from_url(
        cls,
        url: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseSummarizer:
        """URL을 분석하여 적절한 Summarizer 생성
        
        Args:
            url: 요약할 콘텐츠 URL
            api_key: API 키 (선택)
            model: 사용할 모델 (선택)
        
        Returns:
            생성된 Summarizer 인스턴스
        
        Raises:
            ValueError: URL을 처리할 수 있는 Summarizer가 없는 경우
        """
        # 각 Summarizer가 URL을 처리할 수 있는지 확인
        for source, summarizer_class in cls._summarizers.items():
            # 임시 인스턴스 생성하여 지원 도메인 확인
            temp_instance = summarizer_class(api_key=api_key, model=model)
            if temp_instance.can_handle(url):
                logger.info(f"URL에 맞는 Summarizer 찾음: {source.value}")
                return temp_instance
        
        # 지원하는 Summarizer가 없는 경우
        supported_domains = []
        for summarizer_class in cls._summarizers.values():
            temp_instance = summarizer_class()
            supported_domains.extend(temp_instance.get_supported_domains())
        
        raise ValueError(
            f"URL을 처리할 수 있는 Summarizer가 없습니다: {url}\n"
            f"지원하는 도메인: {', '.join(supported_domains)}"
        )
    
    @classmethod
    def list_sources(cls) -> list[str]:
        """사용 가능한 뉴스 소스 목록 반환
        
        Returns:
            뉴스 소스 이름 리스트
        """
        return [source.value for source in cls._summarizers.keys()]
    
    @classmethod
    def register(cls, source: NewsSource, summarizer_class: Type[BaseSummarizer]):
        """새로운 Summarizer 등록
        
        Args:
            source: 뉴스 소스 타입
            summarizer_class: Summarizer 클래스
        """
        cls._summarizers[source] = summarizer_class
        logger.info(f"새로운 Summarizer 등록: {source.value}")


# 하위 호환성을 위한 별칭 (기존 코드와의 호환성)
class Summarizer:
    """기존 코드와의 하위 호환성을 위한 래퍼 클래스
    
    Note:
        이 클래스는 더 이상 사용하지 않는 것을 권장합니다.
        대신 SummarizerFactory를 사용하세요.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Smol AI News Summarizer로 기본 초기화"""
        logger.warning(
            "Summarizer 클래스는 더 이상 사용하지 않습니다. "
            "SummarizerFactory를 사용하세요."
        )
        self._summarizer = SummarizerFactory.create(
            NewsSource.SMOL_AI_NEWS,
            api_key=api_key,
            model=model
        )
    
    def generate_markdown(self, issue_url: str, timeframe: Optional[str] = None) -> str:
        """하위 호환성을 위한 메서드"""
        return self._summarizer.summarize(issue_url, timeframe=timeframe)
    
    def generate_with_retry(
        self, 
        issue_url: str, 
        timeframe: Optional[str] = None,
        max_retries: int = 3
    ) -> str:
        """하위 호환성을 위한 메서드"""
        if hasattr(self._summarizer, 'summarize_with_retry'):
            return self._summarizer.summarize_with_retry(
                issue_url, 
                max_retries=max_retries,
                timeframe=timeframe
            )
        else:
            # 기본 재시도 로직
            return self._summarizer.safe_summarize(issue_url, timeframe=timeframe)