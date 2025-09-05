#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
뉴스를 GitHub Discussions와 Discord에 동시 발송하는 스크립트
"""

import os
import sys
import argparse
from datetime import datetime
import re

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.summarizer import SummarizerFactory
from src.publishers.github import GitHubPublisher
from src.publishers.discord import DiscordPublisher
from src.logger import setup_logger, logger
from src.config import Config
from src.markdown_utils import save_markdown

def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="뉴스 URL을 요약하고 GitHub와 Discord에 동시 발송"
    )
    
    parser.add_argument(
        "url",
        help="뉴스 URL (예: https://news.smol.ai/issues/25-09-01)"
    )
    
    parser.add_argument(
        "--timeframe",
        help="기간 정보 (예: '2025-08-29 ~ 2025-09-01')"
    )
    
    parser.add_argument(
        "--title",
        help="GitHub Discussion 제목 (기본: 자동 생성)"
    )
    
    parser.add_argument(
        "--save-only",
        action="store_true",
        help="요약만 생성하고 발송하지 않음"
    )
    
    parser.add_argument(
        "--github-only",
        action="store_true",
        help="GitHub Discussions에만 발송"
    )
    
    parser.add_argument(
        "--discord-only",
        action="store_true",
        help="Discord에만 발송"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 발송하지 않고 시뮬레이션"
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
    
    # 로거 초기화
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logger(level=log_level)
    
    logger.info("=" * 60)
    logger.info("🚀 뉴스 요약 및 발송 파이프라인 시작")
    logger.info(f"📰 URL: {args.url}")
    logger.info("=" * 60)
    
    # 설정 검증
    try:
        Config.validate()
    except ValueError as e:
        logger.error(str(e))
        return 1
    
    # 1. 요약 생성
    logger.info("📝 요약 생성 중...")
    
    try:
        # URL에서 Summarizer 자동 감지
        summarizer = SummarizerFactory.create_from_url(args.url)
        logger.info(f"✅ 자동 감지된 소스: {summarizer.name}")
        
        # 메타데이터와 함께 요약 생성
        metadata = {}
        if hasattr(summarizer, 'summarize_with_metadata'):
            result = summarizer.summarize_with_metadata(
                args.url,
                timeframe=args.timeframe
            )
            markdown_content = result.get('markdown', '')
            metadata = {
                'headline': result.get('headline', ''),
                'date': result.get('date', '')
            }
            if metadata.get('headline'):
                logger.info(f"📌 헤드라인: {metadata['headline']}")
        else:
            # 기본 요약
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
    # 날짜 기반 자동 경로 생성
    now = datetime.now()
    year_month = now.strftime("%Y/%m")
    
    # URL에서 날짜 정보 추출 (SmolAI News의 경우)
    date_match = re.search(r'(\d{2})-(\d{2})-(\d{2})', args.url)
    if date_match and 'smol' in args.url.lower():
        filename = f"smol_ai_news_20{date_match.group(1)}{date_match.group(2)}{date_match.group(3)}.md"
    else:
        filename = f"recap_{now.strftime('%Y%m%d_%H%M%S')}.md"
    
    output_dir = os.path.join("outputs", year_month)
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    logger.info(f"💾 파일 저장: {output_path}")
    save_markdown(output_path, markdown_content)
    logger.info(f"✅ 저장 완료: {os.path.abspath(output_path)}")
    
    if args.save_only:
        logger.info("📋 요약만 생성하고 발송하지 않습니다.")
        return 0
    
    # 3. 발송
    results = []
    
    # 타이틀 자동 생성 (GitHub용)
    if not args.title:
        if metadata.get('headline') and metadata.get('date'):
            args.title = f"[AI News, {metadata['date']}] {metadata['headline']}"
            logger.info(f"🏷️ 타이틀 자동 생성: {args.title}")
        else:
            from datetime import datetime
            date_str = datetime.now().strftime("%y.%m.%d")
            args.title = f"[AI News, {date_str}] AI 뉴스 요약"
            logger.info(f"🏷️ 기본 타이틀 사용: {args.title}")
    
    # GitHub Discussions 발송
    if not args.discord_only:
        logger.info("\n📤 GitHub Discussions 게시 중...")
        if args.dry_run:
            logger.info("[DRY-RUN] GitHub 게시 시뮬레이션")
            logger.info(f"  제목: {args.title}")
            logger.info(f"  내용 길이: {len(markdown_content)} 글자")
            results.append("GitHub: [DRY-RUN] 성공")
        else:
            try:
                github = GitHubPublisher(
                    repo="sudormrf-run/community",
                    category="News"
                )
                if github.validate_config():
                    result_data = {}
                    if github.publish(markdown_content, title=args.title, **result_data):
                        url = result_data.get('discussion_url', '')
                        if url:
                            results.append(f"GitHub: ✅ 성공 - {url}")
                            logger.info(f"✅ GitHub Discussion 생성 완료")
                            logger.info(f"🔗 URL: {url}")
                        else:
                            results.append("GitHub: ✅ 성공")
                    else:
                        results.append("GitHub: ❌ 실패")
                        logger.error("❌ GitHub Discussion 게시 실패")
                else:
                    logger.error("❌ GitHub 설정이 올바르지 않습니다")
                    results.append("GitHub: ❌ 설정 오류")
            except Exception as e:
                logger.error(f"GitHub 발송 오류: {str(e)}")
                results.append(f"GitHub: ❌ 오류 - {str(e)[:50]}")
    
    # Discord 발송
    if not args.github_only:
        logger.info("\n📤 Discord 발송 중...")
        if args.dry_run:
            logger.info("[DRY-RUN] Discord 발송 시뮬레이션")
            logger.info(f"  제목: {args.title}")
            logger.info(f"  내용 길이: {len(markdown_content)} 글자")
            results.append("Discord: [DRY-RUN] 성공")
        else:
            try:
                discord = DiscordPublisher()
                if discord.validate_config():
                    # Discord 발송 시 제목을 태그로 추가
                    tag = f"**{args.title}**\n"
                    if discord.publish(markdown_content, tag=tag):
                        results.append("Discord: ✅ 성공")
                        logger.info("✅ Discord 발송 완료")
                    else:
                        results.append("Discord: ❌ 실패")
                        logger.error("❌ Discord 발송 실패")
                else:
                    logger.error("❌ Discord 설정이 올바르지 않습니다")
                    logger.error("DISCORD_WEBHOOK_URL 환경변수를 확인하세요")
                    results.append("Discord: ❌ 설정 오류")
            except Exception as e:
                logger.error(f"Discord 발송 오류: {str(e)}")
                results.append(f"Discord: ❌ 오류 - {str(e)[:50]}")
    
    # 4. 결과 요약
    logger.info("\n" + "=" * 60)
    logger.info("📊 발송 결과:")
    for result in results:
        logger.info(f"  {result}")
    logger.info("=" * 60)
    
    # 모든 발송이 성공했는지 확인
    all_success = all("✅" in r or "DRY-RUN" in r for r in results)
    
    if all_success:
        logger.info("🎉 모든 작업이 성공적으로 완료되었습니다!")
        return 0
    else:
        logger.warning("⚠️ 일부 작업이 실패했습니다.")
        return 1

if __name__ == "__main__":
    exit(main())