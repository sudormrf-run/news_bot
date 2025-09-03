# -*- coding: utf-8 -*-
"""
Discord 에러 알림 모듈
"""

import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional

from .config import Config


class ErrorNotifier:
    """에러 발생 시 Discord로 알림을 보내는 클래스"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Args:
            webhook_url: Discord 웹훅 URL (기본값: Config.ERROR_DISCORD_WEBHOOK_URL)
        """
        self.webhook_url = webhook_url or Config.ERROR_DISCORD_WEBHOOK_URL
    
    def send_error(self, error_info: Dict[str, Any]) -> bool:
        """에러 정보를 Discord로 전송
        
        Args:
            error_info: 에러 정보 딕셔너리
                - level: 로그 레벨
                - module: 모듈명
                - function: 함수명
                - line: 라인 번호
                - message: 에러 메시지
                - timestamp: 발생 시간
                - traceback: 스택 트레이스 (선택)
        
        Returns:
            전송 성공 여부
        """
        if not self.webhook_url:
            return False
        
        try:
            # Discord Embed 형식으로 포맷팅
            embed = self._format_error_embed(error_info)
            
            data = {
                "embeds": [embed],
                "username": "News Bot Error Reporter"
            }
            
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return True
            
        except Exception:
            # 알림 실패 시 조용히 실패
            return False
    
    def _format_error_embed(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """에러 정보를 Discord Embed 형식으로 포맷팅
        
        Args:
            error_info: 에러 정보
        
        Returns:
            Discord Embed 딕셔너리
        """
        # 에러 레벨에 따른 색상
        color_map = {
            'ERROR': 0xFF0000,    # 빨간색
            'CRITICAL': 0x8B0000,  # 진한 빨간색
            'WARNING': 0xFFA500,   # 주황색
        }
        
        level = error_info.get('level', 'ERROR')
        color = color_map.get(level, 0xFF0000)
        
        embed = {
            "title": f"🚨 {level}: {error_info.get('message', 'Unknown Error')}",
            "color": color,
            "timestamp": error_info.get('timestamp', datetime.now().isoformat()),
            "fields": [
                {
                    "name": "📁 Module",
                    "value": f"`{error_info.get('module', 'Unknown')}`",
                    "inline": True
                },
                {
                    "name": "🔧 Function",
                    "value": f"`{error_info.get('function', 'Unknown')}`",
                    "inline": True
                },
                {
                    "name": "📍 Line",
                    "value": str(error_info.get('line', 'Unknown')),
                    "inline": True
                }
            ]
        }
        
        # 트레이스백이 있으면 추가
        if 'traceback' in error_info:
            traceback_text = error_info['traceback']
            # Discord 필드 값은 1024자 제한
            if len(traceback_text) > 1000:
                traceback_text = traceback_text[:997] + "..."
            
            embed["fields"].append({
                "name": "📋 Traceback",
                "value": f"```python\n{traceback_text}\n```",
                "inline": False
            })
        
        return embed
    
    def send_info(self, title: str, message: str, color: int = 0x00FF00) -> bool:
        """일반 정보 알림 전송
        
        Args:
            title: 알림 제목
            message: 알림 메시지
            color: Embed 색상 (기본: 초록색)
        
        Returns:
            전송 성공 여부
        """
        if not self.webhook_url:
            return False
        
        try:
            embed = {
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.now().isoformat()
            }
            
            data = {
                "embeds": [embed],
                "username": "News Bot Notifier"
            }
            
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return True
            
        except Exception:
            return False