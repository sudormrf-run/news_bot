#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
새로운 2단계 워크플로우 퍼블리싱 시스템
1단계: Full content → GitHub Discussions
2단계: Compact summary → Discord/기타 플랫폼
"""

import os
import sys
import argparse
from datetime import datetime
import re
from typing import Dict, Any, Optional

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.summarizer import SummarizerFactory
from src.summarizers.compact import CompactSummarizer
from src.publishers.github import GitHubPublisher
from src.publishers.discord import DiscordPublisher
from src.logger import setup_logger, logger
from src.config import Config
from src.markdown_utils import save_markdown


class PublishWorkflow:
    """2단계 퍼블리싱 워크플로우 관리"""
    
    def __init__(self, debug: bool = False):
        """
        Args:
            debug: 디버그 모드
        """
        self.debug = debug
        setup_logger(level="DEBUG" if debug else "INFO")
        self.results = []
        
    def execute(self, url: str, **options) -> bool:
        """전체 워크플로우 실행
        
        Args:
            url: 뉴스 URL
            **options: 
                - timeframe: 기간 정보
                - title: GitHub Discussion 제목
                - send_github: GitHub 발송 여부
                - send_discord: Discord 발송 여부
                - compact_style: 간결 요약 스타일
                - dry_run: 시뮬레이션 모드
        
        Returns:
            성공 여부
        """
        logger.info("=" * 60)
        logger.info("🚀 2단계 퍼블리싱 워크플로우 시작")
        logger.info(f"📰 URL: {url}")
        logger.info("=" * 60)
        
        # Phase 1: 원본 요약 생성
        logger.info("\n=== Phase 1: 원본 요약 생성 ===")
        full_content, metadata = self._generate_full_summary(url, **options)
        if not full_content:
            return False
        
        # 파일 저장 (Full 버전)
        full_path = self._save_content(full_content, metadata, "full")
        logger.info(f"📄 Full 버전 저장: {full_path}")
        
        # Phase 2: GitHub Discussions 발송 (Full content)
        github_url = None
        if options.get('send_github', True):
            logger.info("\n=== Phase 2: GitHub Discussions 발송 ===")
            github_url = self._publish_to_github(full_content, metadata, **options)
            if github_url:
                logger.info(f"✅ GitHub URL: {github_url}")
                self.results.append(f"GitHub: ✅ {github_url}")
            else:
                logger.warning("⚠️ GitHub 발송 실패 또는 건너뜀")
                self.results.append("GitHub: ❌ 실패")
        
        # Phase 3: 간결한 재요약 생성
        logger.info("\n=== Phase 3: 간결한 재요약 생성 ===")
        compact_content = self._generate_compact_summary(
            full_content, 
            github_url=github_url,
            style=options.get('compact_style', 'discord')
        )
        
        if compact_content:
            # 파일 저장 (Compact 버전)
            compact_path = self._save_content(compact_content, metadata, "compact")
            logger.info(f"📄 Compact 버전 저장: {compact_path}")
        
        # Phase 4: 간결 버전 발송 (Discord 등)
        if options.get('send_discord', True) and compact_content:
            logger.info("\n=== Phase 4: Discord 발송 (간결 버전) ===")
            success = self._publish_to_discord(compact_content, metadata, **options)
            if success:
                logger.info("✅ Discord 발송 성공")
                self.results.append("Discord: ✅ 성공")
            else:
                logger.warning("⚠️ Discord 발송 실패")
                self.results.append("Discord: ❌ 실패")
        
        # 결과 요약
        self._print_summary()
        
        return all("✅" in r for r in self.results)
    
    def _generate_full_summary(self, url: str, **options) -> tuple[str, Dict[str, Any]]:
        """원본 전체 요약 생성"""
        try:
            summarizer = SummarizerFactory.create_from_url(url)
            logger.info(f"✅ 자동 감지된 소스: {summarizer.name}")
            
            if hasattr(summarizer, 'summarize_with_metadata'):
                result = summarizer.summarize_with_metadata(
                    url,
                    timeframe=options.get('timeframe')
                )
                content = result.get('markdown', '')
                metadata = {
                    'headline': result.get('headline', ''),
                    'date': result.get('date', ''),
                    'source': summarizer.name
                }
            else:
                content = summarizer.safe_summarize(
                    url,
                    timeframe=options.get('timeframe')
                )
                metadata = {'source': summarizer.name}
            
            logger.info(f"✅ 요약 생성 완료 ({len(content)}자)")
            return content, metadata
            
        except Exception as e:
            logger.error(f"요약 생성 실패: {str(e)}")
            return None, {}
    
    def _generate_compact_summary(self, full_content: str, 
                                 github_url: Optional[str] = None,
                                 style: str = 'discord') -> Optional[str]:
        """간결한 재요약 생성"""
        try:
            compact = CompactSummarizer()
            
            if not compact.validate_config():
                logger.warning("CompactSummarizer 설정 오류, 건너뜀")
                return None
            
            result = compact.summarize_with_metadata(
                full_content,
                github_url=github_url,
                style=style,
                max_length=2000 if style == 'discord' else 1000
            )
            
            content = result.get('markdown', '')
            logger.info(f"✅ 간결 요약 생성 완료 ({result.get('char_count', 0)}자, {style} 스타일)")
            return content
            
        except Exception as e:
            logger.error(f"간결 요약 생성 실패: {str(e)}")
            return None
    
    def _publish_to_github(self, content: str, metadata: Dict, **options) -> Optional[str]:
        """GitHub Discussions 발송"""
        if options.get('dry_run'):
            logger.info("[DRY-RUN] GitHub 발송 시뮬레이션")
            return "https://github.com/orgs/sudormrf-run/discussions/[DRY-RUN]"
        
        try:
            # 제목 생성
            title = options.get('title')
            if not title:
                if metadata.get('headline') and metadata.get('date'):
                    title = f"[AI News, {metadata['date']}] {metadata['headline']}"
                else:
                    title = f"[AI News, {datetime.now().strftime('%y.%m.%d')}] AI 뉴스 요약"
            
            logger.info(f"📌 제목: {title}")
            
            github = GitHubPublisher(
                repo="sudormrf-run/community",
                category="News"
            )
            
            if not github.validate_config():
                logger.error("GitHub 설정 오류")
                return None
            
            result_data = {}
            if github.publish(content, title=title, **result_data):
                return result_data.get('discussion_url')
            
        except Exception as e:
            logger.error(f"GitHub 발송 오류: {str(e)}")
        
        return None
    
    def _publish_to_discord(self, content: str, metadata: Dict, **options) -> bool:
        """Discord 발송 (간결 버전)"""
        if options.get('dry_run'):
            logger.info("[DRY-RUN] Discord 발송 시뮬레이션")
            return True
        
        try:
            discord = DiscordPublisher()
            
            if not discord.validate_config():
                logger.error("Discord 설정 오류")
                return False
            
            # 간결 버전은 한 메시지로 발송 가능
            return discord.publish(content)
            
        except Exception as e:
            logger.error(f"Discord 발송 오류: {str(e)}")
            return False
    
    def _save_content(self, content: str, metadata: Dict, version: str) -> str:
        """콘텐츠 저장"""
        now = datetime.now()
        year_month = now.strftime("%Y/%m")
        
        # 버전별 파일명
        if version == "full":
            filename = f"full_{now.strftime('%Y%m%d_%H%M%S')}.md"
            subdir = "full"
        else:  # compact
            filename = f"compact_{now.strftime('%Y%m%d_%H%M%S')}.md"
            subdir = "compact"
        
        output_dir = os.path.join("outputs", year_month, subdir)
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        save_markdown(filepath, content)
        
        return filepath
    
    def _print_summary(self):
        """결과 요약 출력"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 워크플로우 실행 결과:")
        for result in self.results:
            logger.info(f"  {result}")
        logger.info("=" * 60)


def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="2단계 워크플로우 퍼블리싱 시스템"
    )
    
    parser.add_argument(
        "url",
        help="뉴스 URL"
    )
    
    parser.add_argument(
        "--timeframe",
        help="기간 정보"
    )
    
    parser.add_argument(
        "--title",
        help="GitHub Discussion 제목"
    )
    
    parser.add_argument(
        "--no-github",
        action="store_true",
        help="GitHub 발송 건너뛰기"
    )
    
    parser.add_argument(
        "--no-discord",
        action="store_true",
        help="Discord 발송 건너뛰기"
    )
    
    parser.add_argument(
        "--compact-style",
        default="discord",
        choices=["discord", "twitter", "slack", "general"],
        help="간결 요약 스타일"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="시뮬레이션 모드"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="디버그 모드"
    )
    
    return parser.parse_args()


def main():
    """메인 함수"""
    args = parse_arguments()
    
    # 설정 검증
    try:
        Config.validate()
    except ValueError as e:
        print(f"설정 오류: {e}")
        return 1
    
    # 워크플로우 실행
    workflow = PublishWorkflow(debug=args.debug)
    
    success = workflow.execute(
        args.url,
        timeframe=args.timeframe,
        title=args.title,
        send_github=not args.no_github,
        send_discord=not args.no_discord,
        compact_style=args.compact_style,
        dry_run=args.dry_run
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())