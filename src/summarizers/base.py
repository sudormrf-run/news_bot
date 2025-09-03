# -*- coding: utf-8 -*-
"""
Summarizer 베이스 클래스
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from ..logger import logger


class BaseSummarizer(ABC):
    """모든 Summarizer가 상속받는 추상 클래스"""
    
    def __init__(self, name: str, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Args:
            name: Summarizer 이름
            api_key: API 키
            model: 사용할 모델
        """
        self.name = name
        self.api_key = api_key
        self.model = model
        logger.debug(f"{self.name} Summarizer 초기화")
    
    @abstractmethod
    def summarize(self, url: str, **kwargs) -> str:
        """URL에서 콘텐츠를 요약
        
        Args:
            url: 요약할 콘텐츠 URL
            **kwargs: 추가 파라미터
        
        Returns:
            마크다운 형식의 요약
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """설정 유효성 검사
        
        Returns:
            설정 유효 여부
        """
        pass
    
    @abstractmethod
    def get_supported_domains(self) -> list[str]:
        """지원하는 도메인 목록
        
        Returns:
            도메인 리스트 (예: ['news.smol.ai', 'smol.ai'])
        """
        pass
    
    def can_handle(self, url: str) -> bool:
        """이 Summarizer가 해당 URL을 처리할 수 있는지 확인
        
        Args:
            url: 확인할 URL
        
        Returns:
            처리 가능 여부
        """
        supported_domains = self.get_supported_domains()
        return any(domain in url for domain in supported_domains)
    
    def safe_summarize(self, url: str, **kwargs) -> str:
        """에러 처리가 포함된 안전한 요약
        
        Args:
            url: 요약할 URL
            **kwargs: 추가 파라미터
        
        Returns:
            마크다운 형식의 요약
        
        Raises:
            RuntimeError: 요약 실패 시
        """
        try:
            # 설정 검증
            if not self.validate_config():
                raise ValueError(f"{self.name}: 설정이 유효하지 않음")
            
            # URL 처리 가능 여부 확인
            if not self.can_handle(url):
                raise ValueError(f"{self.name}: 지원하지 않는 URL - {url}")
            
            # 요약 생성
            logger.info(f"{self.name} 요약 시작: {url}")
            summary = self.summarize(url, **kwargs)
            
            if not summary:
                raise RuntimeError("요약 생성 실패: 빈 결과")
            
            logger.info(f"{self.name} 요약 완료 (길이: {len(summary)}자)")
            return summary
            
        except Exception as e:
            logger.error(f"{self.name} 요약 중 오류: {str(e)}", exc_info=True)
            raise RuntimeError(f"{self.name} 요약 실패: {str(e)}")


class SummarizerResult:
    """Summarizer 실행 결과"""
    
    def __init__(
        self,
        summarizer_name: str,
        url: str,
        success: bool,
        summary: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            summarizer_name: Summarizer 이름
            url: 원본 URL
            success: 성공 여부
            summary: 요약 결과
            error: 에러 메시지
            metadata: 추가 메타데이터
        """
        self.summarizer_name = summarizer_name
        self.url = url
        self.success = success
        self.summary = summary or ""
        self.error = error
        self.metadata = metadata or {}
    
    def __str__(self) -> str:
        status = "성공" if self.success else f"실패: {self.error}"
        return f"[{self.summarizer_name}] {self.url} - {status}"
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "summarizer": self.summarizer_name,
            "url": self.url,
            "success": self.success,
            "summary": self.summary,
            "error": self.error,
            "metadata": self.metadata
        }