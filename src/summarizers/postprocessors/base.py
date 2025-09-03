# -*- coding: utf-8 -*-
"""
PostProcessor 베이스 클래스
"""

from abc import ABC, abstractmethod
from typing import Optional
from openai import OpenAI

from ...config import Config
from ...logger import logger


class BasePostProcessor(ABC):
    """모든 PostProcessor가 상속받는 추상 클래스"""
    
    def __init__(self, name: str, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Args:
            name: PostProcessor 이름
            api_key: API 키
            model: 사용할 모델
        """
        self.name = name
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or "gpt-5"
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, timeout=6000.0)
        
        logger.debug(f"{self.name} PostProcessor 초기화 (모델: {self.model})")
    
    @abstractmethod
    def process(self, markdown: str) -> str:
        """마크다운 텍스트 후처리
        
        Args:
            markdown: 원본 마크다운 텍스트
        
        Returns:
            처리된 마크다운 텍스트
        """
        pass
    
    def safe_process(self, markdown: str) -> str:
        """에러 처리가 포함된 안전한 후처리
        
        Args:
            markdown: 원본 마크다운 텍스트
        
        Returns:
            처리된 마크다운 텍스트 (실패시 원본 반환)
        """
        try:
            if not markdown:
                return markdown
            
            logger.info(f"{self.name} 후처리 시작 (원본 길이: {len(markdown)}자)")
            processed = self.process(markdown)
            
            if processed:
                logger.info(f"{self.name} 후처리 완료 (결과 길이: {len(processed)}자)")
                return processed
            else:
                logger.warning(f"{self.name} 후처리 결과가 비어있음, 원본 반환")
                return markdown
                
        except Exception as e:
            logger.error(f"{self.name} 후처리 중 오류: {str(e)}", exc_info=True)
            return markdown
    
    def _extract_markdown(self, response) -> str:
        """OpenAI API 응답에서 마크다운 텍스트 추출
        
        Args:
            response: OpenAI API 응답 객체
        
        Returns:
            추출된 마크다운 텍스트
        """
        # SDK 버전에 따라 output_text가 없을 수 있으므로 안전 추출
        md = getattr(response, "output_text", None)
        
        if not md:
            chunks = []
            for item in getattr(response, "output", []) or []:
                if getattr(item, "type", "") == "message":
                    for content in getattr(item, "content", []) or []:
                        if getattr(content, "type", "") == "output_text":
                            chunks.append(getattr(content, "text", ""))
            md = "\n".join(chunks).strip()
        
        return md