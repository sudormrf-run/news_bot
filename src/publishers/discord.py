# -*- coding: utf-8 -*-
"""
Discord 웹훅 Publisher
"""

import requests
from typing import Optional, List

from .base import BasePublisher
from ..config import Config
from ..logger import logger


class DiscordPublisher(BasePublisher):
    """Discord 웹훅으로 메시지를 발송하는 Publisher"""
    
    MAX_MESSAGE_LENGTH = 1900  # Discord 메시지 최대 길이 (안전 마진)
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Args:
            webhook_url: Discord 웹훅 URL (기본값: Config.DISCORD_WEBHOOK_URL)
        """
        super().__init__("Discord")
        self.webhook_url = webhook_url or Config.DISCORD_WEBHOOK_URL
    
    def validate_config(self) -> bool:
        """설정 유효성 검사"""
        return bool(self.webhook_url)
    
    def publish(self, content: str, **kwargs) -> bool:
        """Discord로 메시지 발송
        
        Args:
            content: 발송할 콘텐츠
            tag: 메시지 태그 (선택)
            username: 봇 이름 (선택)
        
        Returns:
            발송 성공 여부
        """
        if not self.webhook_url:
            logger.error("Discord 웹훅 URL이 설정되지 않음")
            return False
        
        tag = kwargs.get('tag', '')
        username = kwargs.get('username', 'News Bot')
        
        # 긴 메시지를 청크로 분할
        chunks = self._split_message(content, tag)
        
        try:
            for idx, chunk in enumerate(chunks, 1):
                # 여러 청크인 경우 페이지 번호 추가
                if len(chunks) > 1:
                    chunk_suffix = f"\n\n({idx}/{len(chunks)})"
                    if len(chunk) + len(chunk_suffix) <= self.MAX_MESSAGE_LENGTH:
                        chunk += chunk_suffix
                
                # 첫 번째 청크에만 태그 추가
                if idx == 1 and tag:
                    message = f"{tag}\n{chunk}"
                else:
                    message = chunk
                
                data = {
                    "content": message,
                    "username": username
                }
                
                response = requests.post(
                    self.webhook_url,
                    json=data,
                    timeout=30
                )
                response.raise_for_status()
                
                logger.debug(f"Discord 청크 {idx}/{len(chunks)} 발송 완료")
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Discord 발송 실패: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Discord 발송 중 예상치 못한 오류: {str(e)}", exc_info=True)
            return False
    
    def _split_message(self, content: str, tag: str = '') -> List[str]:
        """긴 메시지를 Discord 제한에 맞게 분할
        
        Args:
            content: 원본 메시지
            tag: 첫 청크에 추가할 태그
        
        Returns:
            분할된 메시지 리스트
        """
        # 태그가 있으면 첫 청크 크기 조정
        first_chunk_max = self.MAX_MESSAGE_LENGTH
        if tag:
            first_chunk_max -= len(tag) - 1  # \n 포함
        
        if len(content) <= first_chunk_max:
            return [content]
        
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_length = 0
        
        for line in lines:
            # 단일 라인이 너무 긴 경우
            if len(line) > self.MAX_MESSAGE_LENGTH:
                # 현재 청크 저장
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # 긴 라인을 강제로 분할
                for i in range(0, len(line), self.MAX_MESSAGE_LENGTH):
                    chunks.append(line[i:i+self.MAX_MESSAGE_LENGTH])
                continue
            
            # 현재 청크에 추가 가능한지 확인
            line_length = len(line) + 1  # \n 포함
            max_length = first_chunk_max if not chunks else self.MAX_MESSAGE_LENGTH
            
            if current_length + line_length > max_length:
                # 현재 청크 저장
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = len(line)
            else:
                current_chunk.append(line)
                current_length += line_length
        
        # 마지막 청크 저장
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks or [content[:self.MAX_MESSAGE_LENGTH]]
    
    def send_embed(self, title: str, description: str, color: int = 0x00FF00, **fields) -> bool:
        """Discord Embed 메시지 발송
        
        Args:
            title: Embed 제목
            description: Embed 설명
            color: Embed 색상
            **fields: 추가 필드 (name=value 형식)
        
        Returns:
            발송 성공 여부
        """
        if not self.webhook_url:
            return False
        
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": []
        }
        
        for name, value in fields.items():
            embed["fields"].append({
                "name": name,
                "value": str(value),
                "inline": True
            })
        
        data = {
            "embeds": [embed],
            "username": "News Bot"
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Discord Embed 발송 실패: {str(e)}")
            return False