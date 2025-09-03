# -*- coding: utf-8 -*-
"""
카카오톡 봇 Publisher
"""

import requests
from typing import Optional

from .base import BasePublisher
from ..config import Config
from ..logger import logger
from ..markdown_utils import extract_today_summary


class KakaoPublisher(BasePublisher):
    """카카오톡 봇으로 메시지를 발송하는 Publisher"""
    
    MAX_MESSAGE_LENGTH = 1000  # 카카오톡 메시지 길이 제한
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Args:
            webhook_url: 카카오톡 봇 웹훅 URL (기본값: Config.KAKAO_BOT_WEBHOOK_URL)
        """
        super().__init__("Kakao")
        self.webhook_url = webhook_url or Config.KAKAO_BOT_WEBHOOK_URL
    
    def validate_config(self) -> bool:
        """설정 유효성 검사"""
        return bool(self.webhook_url)
    
    def publish(self, content: str, **kwargs) -> bool:
        """카카오톡 봇으로 메시지 발송
        
        Args:
            content: 전체 마크다운 콘텐츠
            send_full: 전체 내용 발송 여부 (기본: False, '오늘의 요약'만 발송)
        
        Returns:
            발송 성공 여부
        """
        if not self.webhook_url:
            logger.error("카카오톡 봇 웹훅 URL이 설정되지 않음")
            return False
        
        send_full = kwargs.get('send_full', False)
        
        # 발송할 내용 선택
        if send_full:
            text = self._prepare_full_content(content)
            if not text:
                logger.warning("전체 내용이 너무 김, 요약 섹션만 발송")
                text = self._prepare_today_summary(content)
        else:
            text = self._prepare_today_summary(content)
        
        if not text:
            logger.error("발송할 내용이 없음")
            return False
        
        # 카카오톡 봇 웹훅 호출
        try:
            payload = {
                "text": text
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info("카카오톡 봇 발송 완료")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"카카오톡 봇 발송 실패: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"카카오톡 봇 발송 중 예상치 못한 오류: {str(e)}", exc_info=True)
            return False
    
    def _prepare_today_summary(self, content: str) -> Optional[str]:
        """'오늘의 요약' 섹션 추출 및 준비
        
        Args:
            content: 전체 마크다운 콘텐츠
        
        Returns:
            발송할 텍스트 (없으면 None)
        """
        # '오늘의 요약' 섹션 추출
        today_summary = extract_today_summary(content)
        
        if not today_summary:
            logger.info("'오늘의 요약' 섹션을 찾을 수 없음")
            return None
        
        # 마크다운을 간단한 텍스트로 변환
        text = self._simplify_markdown(today_summary)
        
        # 길이 제한
        if len(text) > self.MAX_MESSAGE_LENGTH:
            text = text[:self.MAX_MESSAGE_LENGTH - 3] + "..."
            logger.warning(f"메시지가 {self.MAX_MESSAGE_LENGTH}자를 초과하여 잘림")
        
        return text
    
    def _prepare_full_content(self, content: str) -> Optional[str]:
        """전체 내용 준비
        
        Args:
            content: 전체 마크다운 콘텐츠
        
        Returns:
            발송할 텍스트 (길이 초과 시 None)
        """
        # 마크다운을 간단한 텍스트로 변환
        text = self._simplify_markdown(content)
        
        # 길이 확인
        if len(text) > self.MAX_MESSAGE_LENGTH:
            return None
        
        return text
    
    def _simplify_markdown(self, markdown: str) -> str:
        """마크다운을 카카오톡용 텍스트로 간소화
        
        Args:
            markdown: 마크다운 텍스트
        
        Returns:
            간소화된 텍스트
        """
        import re
        
        text = markdown
        
        # 헤더 간소화 (## Title -> [Title])
        text = re.sub(r'^#{1,6}\s+(.+)$', r'[\1]', text, flags=re.MULTILINE)
        
        # 링크 간소화 ([text](url) -> text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # 굵은 글씨 제거 (**text** -> text)
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        
        # 기울임 제거 (*text* -> text)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        
        # 코드 블록 간소화 (```code``` -> code)
        text = re.sub(r'```[^\n]*\n([^`]+)```', r'\1', text, flags=re.MULTILINE | re.DOTALL)
        
        # 인라인 코드 간소화 (`code` -> code)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # 인용 블록 간소화 (> text -> " text)
        text = re.sub(r'^>\s+', '" ', text, flags=re.MULTILINE)
        
        # 불릿 포인트 유지 (깔끔하게)
        text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.MULTILINE)
        
        # 연속된 빈 줄 제거
        text = re.sub(r'\n\n+', '\n\n', text)
        
        return text.strip()
    
    def send_simple_message(self, message: str) -> bool:
        """단순 텍스트 메시지 발송
        
        Args:
            message: 발송할 메시지
        
        Returns:
            발송 성공 여부
        """
        if not self.webhook_url:
            return False
        
        # 길이 제한
        if len(message) > self.MAX_MESSAGE_LENGTH:
            message = message[:self.MAX_MESSAGE_LENGTH - 3] + "..."
        
        try:
            payload = {
                "text": message
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"카카오톡 단순 메시지 발송 실패: {str(e)}")
            return False