# -*- coding: utf-8 -*-
"""
환경변수 및 설정 관리 모듈
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """애플리케이션 설정 관리"""
    
    # OpenAI 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Discord 설정
    DISCORD_WEBHOOK_URL: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL")
    ERROR_DISCORD_WEBHOOK_URL: Optional[str] = os.getenv("ERROR_DISCORD_WEBHOOK_URL")
    
    # GitHub 설정
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GH_REPO: Optional[str] = os.getenv("GH_REPO")  # Repository discussions (owner/repo)
    GH_ORG: Optional[str] = os.getenv("GH_ORG")  # Organization discussions
    GH_ORG_REPO: Optional[str] = os.getenv("GH_ORG_REPO", "community")  # Organization의 discussion repository 이름
    GH_DISCUSSION_CATEGORY: Optional[str] = os.getenv("GH_DISCUSSION_CATEGORY")
    
    # Kakao 설정
    KAKAO_BOT_WEBHOOK_URL: Optional[str] = os.getenv("KAKAO_BOT_WEBHOOK_URL")
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    
    @classmethod
    def validate(cls) -> None:
        """필수 설정값 검증"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        if errors:
            raise ValueError(f"설정 오류:\n" + "\n".join(errors))
    
    @classmethod
    def is_discord_enabled(cls) -> bool:
        """Discord 발송 가능 여부"""
        return bool(cls.DISCORD_WEBHOOK_URL)
    
    @classmethod
    def is_github_enabled(cls) -> bool:
        """GitHub Discussions 발송 가능 여부"""
        return all([
            cls.GITHUB_TOKEN,
            cls.GH_REPO or cls.GH_ORG,  # Repository 또는 Organization
            cls.GH_DISCUSSION_CATEGORY
        ])
    
    @classmethod
    def is_kakao_enabled(cls) -> bool:
        """Kakao 발송 가능 여부"""
        return bool(cls.KAKAO_BOT_WEBHOOK_URL)
    
    @classmethod
    def is_error_notification_enabled(cls) -> bool:
        """에러 알림 가능 여부"""
        return bool(cls.ERROR_DISCORD_WEBHOOK_URL)
    
    @classmethod
    def get_enabled_publishers(cls) -> list[str]:
        """활성화된 퍼블리셔 목록"""
        publishers = []
        if cls.is_discord_enabled():
            publishers.append("discord")
        if cls.is_github_enabled():
            publishers.append("github")
        if cls.is_kakao_enabled():
            publishers.append("kakao")
        return publishers