# -*- coding: utf-8 -*-
"""
Publisher 베이스 클래스
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from ..logger import logger


class BasePublisher(ABC):
    """모든 Publisher가 상속받는 추상 클래스"""
    
    def __init__(self, name: str):
        """
        Args:
            name: Publisher 이름
        """
        self.name = name
        logger.debug(f"{self.name} Publisher 초기화")
    
    @abstractmethod
    def publish(self, content: str, **kwargs) -> bool:
        """콘텐츠 발송
        
        Args:
            content: 발송할 콘텐츠
            **kwargs: 추가 파라미터
        
        Returns:
            발송 성공 여부
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """설정 유효성 검사
        
        Returns:
            설정 유효 여부
        """
        pass
    
    def pre_publish(self, content: str) -> str:
        """발송 전 처리 (옵션)
        
        Args:
            content: 원본 콘텐츠
        
        Returns:
            처리된 콘텐츠
        """
        return content
    
    def post_publish(self, success: bool, **kwargs) -> None:
        """발송 후 처리 (옵션)
        
        Args:
            success: 발송 성공 여부
            **kwargs: 추가 정보
        """
        if success:
            logger.info(f"{self.name} 발송 성공")
        else:
            logger.error(f"{self.name} 발송 실패")
    
    def safe_publish(self, content: str, **kwargs) -> bool:
        """에러 처리가 포함된 안전한 발송
        
        Args:
            content: 발송할 콘텐츠
            **kwargs: 추가 파라미터
        
        Returns:
            발송 성공 여부
        """
        try:
            # 설정 검증
            if not self.validate_config():
                logger.error(f"{self.name}: 설정이 유효하지 않음")
                return False
            
            # 전처리
            processed_content = self.pre_publish(content)
            
            # 발송
            logger.info(f"{self.name} 발송 시작...")
            success = self.publish(processed_content, **kwargs)
            
            # 후처리
            self.post_publish(success, **kwargs)
            
            return success
            
        except Exception as e:
            logger.error(f"{self.name} 발송 중 오류: {str(e)}", exc_info=True)
            self.post_publish(False, error=str(e))
            return False


class PublisherResult:
    """Publisher 실행 결과"""
    
    def __init__(
        self,
        publisher_name: str,
        success: bool,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            publisher_name: Publisher 이름
            success: 성공 여부
            message: 결과 메시지
            data: 추가 데이터
        """
        self.publisher_name = publisher_name
        self.success = success
        self.message = message or ("성공" if success else "실패")
        self.data = data or {}
    
    def __str__(self) -> str:
        return f"[{self.publisher_name}] {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "publisher": self.publisher_name,
            "success": self.success,
            "message": self.message,
            "data": self.data
        }