#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AINews 요약 생성 및 배포 파이프라인
메인 CLI 진입점
"""

import os
import sys
import argparse
import textwrap
from typing import List

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.logger import logger, setup_logger
from src.summarizer import SummarizerFactory, NewsSource
from src.markdown_utils import save_markdown
from src.publishers.discord import DiscordPublisher
from src.publishers.github import GitHubPublisher
from src.publishers.kakao import KakaoPublisher


def parse_arguments() -> argparse.Namespace:
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="뉴스 요약 → MD 저장 → (옵션) Discord/GitHub/Kakao 발송",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        예시:
          # 기본 요약 생성 (URL에서 자동 감지)
          python main.py --url https://news.smol.ai/issues/25-09-01-not-much
          
          # 특정 소스 지정
          python main.py --url https://news.smol.ai/issues/25-09-01 --source smol_ai_news
          
          # 기간 정보와 함께 요약
          python main.py --url https://news.smol.ai/issues/25-09-01 --timeframe "2025-08-29 ~ 2025-09-01"
          
          # 모든 채널로 발송
          python main.py --url https://news.smol.ai/issues/25-09-01 --title "AI News 9월 1일" --send-all
        """)
    )
    
    # 필수 인자
    parser.add_argument(
        "--url",
        required=True,
        help="뉴스 URL (예: https://news.smol.ai/issues/25-09-01)"
    )
    
    # 선택 인자
    parser.add_argument(
        "--source",
        choices=[source.value for source in NewsSource],
        help="뉴스 소스 타입 (기본: URL에서 자동 감지)"
    )
    
    parser.add_argument(
        "--timeframe",
        default="",
        help="기간 정보 (예: '2025-08-29 ~ 2025-09-01')"
    )
    
    parser.add_argument(
        "--out",
        default="recap.md",
        help="저장할 마크다운 파일 경로 (기본: recap.md)"
    )
    
    parser.add_argument(
        "--title",
        default="",
        help="GitHub Discussion 제목 (GitHub 발송 시 필수)"
    )
    
    # 발송 옵션
    parser.add_argument(
        "--send-discord",
        action="store_true",
        help="Discord 웹훅으로 발송"
    )
    
    parser.add_argument(
        "--send-github",
        action="store_true",
        help="GitHub Discussions에 게시"
    )
    
    parser.add_argument(
        "--send-kakao",
        action="store_true",
        help="카카오톡 봇으로 '오늘의 요약' 발송"
    )
    
    parser.add_argument(
        "--send-all",
        action="store_true",
        help="활성화된 모든 채널로 발송"
    )
    
    # 디버그 옵션
    parser.add_argument(
        "--debug",
        action="store_true",
        help="디버그 모드 (상세 로그 출력)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 발송하지 않고 시뮬레이션만 수행"
    )
    
    return parser.parse_args()


def main() -> int:
    """메인 함수"""
    try:
        # 인자 파싱
        args = parse_arguments()
        
        # 로거 초기화
        log_level = "DEBUG" if args.debug else "INFO"
        setup_logger(level=log_level)
        
        logger.info("=" * 60)
        logger.info("뉴스 요약 파이프라인 시작")
        logger.info(f"URL: {args.url}")
        if args.source:
            logger.info(f"소스: {args.source}")
        logger.info("=" * 60)
        
        # 설정 검증
        try:
            Config.validate()
        except ValueError as e:
            logger.error(str(e))
            return 1
        
        # 1. 요약 생성
        logger.info("📝 요약 생성 중...")
        
        # Summarizer 선택 및 생성
        try:
            if args.source:
                # 명시적으로 소스가 지정된 경우
                news_source = NewsSource(args.source)
                summarizer = SummarizerFactory.create(news_source)
            else:
                # URL에서 자동 감지
                summarizer = SummarizerFactory.create_from_url(args.url)
                logger.info(f"자동 감지된 소스: {summarizer.name}")
        except ValueError as e:
            logger.error(f"Summarizer 생성 실패: {str(e)}")
            return 1
        
        try:
            # summarize_with_retry 메서드가 있으면 사용, 없으면 safe_summarize 사용
            if hasattr(summarizer, 'summarize_with_retry'):
                markdown_content = summarizer.summarize_with_retry(
                    args.url,
                    max_retries=3,
                    timeframe=args.timeframe
                )
            else:
                markdown_content = summarizer.safe_summarize(
                    args.url,
                    timeframe=args.timeframe
                )
        except Exception as e:
            logger.error(f"요약 생성 실패: {str(e)}")
            return 1
        
        # 2. 파일 저장
        logger.info(f"💾 파일 저장: {args.out}")
        save_markdown(args.out, markdown_content)
        logger.info(f"✅ 저장 완료: {os.path.abspath(args.out)}")
        
        # 3. 발송 옵션 처리
        if args.send_all:
            args.send_discord = Config.is_discord_enabled()
            args.send_github = Config.is_github_enabled()
            args.send_kakao = Config.is_kakao_enabled()
            logger.info(f"전체 발송 모드: {Config.get_enabled_publishers()}")
        
        results = []
        
        # Discord 발송
        if args.send_discord:
            logger.info("📤 Discord 발송 중...")
            if args.dry_run:
                logger.info("[DRY-RUN] Discord 발송 시뮬레이션")
                results.append("Discord: [DRY-RUN] 성공")
            else:
                discord = DiscordPublisher()
                if discord.safe_publish(
                    markdown_content,
                    tag=f"**{args.title}**" if args.title else ""
                ):
                    results.append("Discord: ✅ 성공")
                else:
                    results.append("Discord: ❌ 실패")
        
        # GitHub 발송
        if args.send_github:
            if not args.title:
                logger.error("GitHub 발송에는 --title이 필요합니다")
                results.append("GitHub: ❌ 제목 없음")
            else:
                logger.info("📤 GitHub Discussions 게시 중...")
                if args.dry_run:
                    logger.info("[DRY-RUN] GitHub 게시 시뮬레이션")
                    results.append("GitHub: [DRY-RUN] 성공")
                else:
                    github = GitHubPublisher()
                    if github.safe_publish(markdown_content, title=args.title):
                        results.append("GitHub: ✅ 성공")
                    else:
                        results.append("GitHub: ❌ 실패")
        
        # Kakao 발송
        if args.send_kakao:
            logger.info("📤 카카오톡 발송 중...")
            if args.dry_run:
                logger.info("[DRY-RUN] 카카오톡 발송 시뮬레이션")
                results.append("Kakao: [DRY-RUN] 성공")
            else:
                kakao = KakaoPublisher()
                if kakao.safe_publish(markdown_content):
                    results.append("Kakao: ✅ 성공")
                else:
                    results.append("Kakao: ❌ 실패")
        
        # 결과 요약
        logger.info("=" * 60)
        logger.info("📊 실행 결과:")
        logger.info(f"  - 요약 생성: ✅")
        logger.info(f"  - 파일 저장: ✅ ({args.out})")
        
        if results:
            logger.info("  - 발송 결과:")
            for result in results:
                logger.info(f"    - {result}")
        
        logger.info("=" * 60)
        logger.info("✨ 파이프라인 완료")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n사용자에 의해 중단됨")
        return 130
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())