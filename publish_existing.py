#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기존 마크다운 파일을 GitHub와 Discord에 발송하는 스크립트
"""

import os
import sys
import argparse
from datetime import datetime
import re

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.publishers.github import GitHubPublisher
from src.publishers.discord import DiscordPublisher
from src.logger import setup_logger, logger
from src.config import Config

def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="기존 마크다운 파일을 GitHub와 Discord에 발송"
    )
    
    parser.add_argument(
        "file",
        help="마크다운 파일 경로"
    )
    
    parser.add_argument(
        "--title",
        help="제목 (기본: 파일명에서 자동 생성)"
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
    
    return parser.parse_args()

def generate_title_from_file(filepath: str) -> str:
    """파일명에서 제목 생성"""
    basename = os.path.basename(filepath)
    
    # SmolAI News 형식
    date_match = re.search(r'smol_ai_news_(\d{4})(\d{2})(\d{2})', basename)
    if date_match:
        year = date_match.group(1)[-2:]  # 마지막 2자리
        month = date_match.group(2)
        day = date_match.group(3)
        return f"[AI News, {year}.{month}.{day}] AI 뉴스 요약"
    
    # 일반 형식
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})', basename)
    if date_match:
        year = date_match.group(1)[-2:]
        month = date_match.group(2)
        day = date_match.group(3)
        return f"[AI News, {year}.{month}.{day}] AI 뉴스 요약"
    
    # 기본값
    return f"[AI News, {datetime.now().strftime('%y.%m.%d')}] AI 뉴스 요약"

def main():
    """메인 함수"""
    args = parse_arguments()
    
    # 로거 초기화
    setup_logger(level="INFO")
    
    logger.info("=" * 60)
    logger.info("📤 마크다운 파일 발송")
    logger.info(f"📄 파일: {args.file}")
    logger.info("=" * 60)
    
    # 파일 읽기
    if not os.path.exists(args.file):
        logger.error(f"파일을 찾을 수 없습니다: {args.file}")
        return 1
    
    with open(args.file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    logger.info(f"📋 파일 크기: {len(content)} 글자")
    
    # 제목 생성
    if not args.title:
        args.title = generate_title_from_file(args.file)
        logger.info(f"🏷️ 자동 생성 제목: {args.title}")
    
    results = []
    
    # GitHub Discussions 발송
    if not args.discord_only:
        logger.info("\n📤 GitHub Discussions 게시 중...")
        if args.dry_run:
            logger.info("[DRY-RUN] GitHub 게시 시뮬레이션")
            logger.info(f"  제목: {args.title}")
            results.append("GitHub: [DRY-RUN] 성공")
        else:
            try:
                github = GitHubPublisher(
                    repo="sudormrf-run/community",
                    category="News"
                )
                if github.validate_config():
                    result_data = {}
                    if github.publish(content, title=args.title, **result_data):
                        url = result_data.get('discussion_url', '')
                        if url:
                            logger.info(f"✅ GitHub: {url}")
                            results.append(f"GitHub: ✅ {url}")
                        else:
                            results.append("GitHub: ✅ 성공")
                    else:
                        results.append("GitHub: ❌ 실패")
                else:
                    logger.error("GitHub 설정 오류")
                    results.append("GitHub: ❌ 설정 오류")
            except Exception as e:
                logger.error(f"GitHub 오류: {str(e)}")
                results.append(f"GitHub: ❌ {str(e)[:30]}")
    
    # Discord 발송
    if not args.github_only:
        logger.info("\n📤 Discord 발송 중...")
        if args.dry_run:
            logger.info("[DRY-RUN] Discord 발송 시뮬레이션")
            results.append("Discord: [DRY-RUN] 성공")
        else:
            try:
                discord = DiscordPublisher()
                if discord.validate_config():
                    tag = f"**{args.title}**\n"
                    if discord.publish(content, tag=tag):
                        logger.info("✅ Discord 발송 완료")
                        results.append("Discord: ✅ 성공")
                    else:
                        results.append("Discord: ❌ 실패")
                else:
                    logger.error("Discord 웹훅 설정 오류")
                    results.append("Discord: ❌ 설정 오류")
            except Exception as e:
                logger.error(f"Discord 오류: {str(e)}")
                results.append(f"Discord: ❌ {str(e)[:30]}")
    
    # 결과 요약
    logger.info("\n" + "=" * 60)
    logger.info("📊 발송 결과:")
    for result in results:
        logger.info(f"  {result}")
    logger.info("=" * 60)
    
    return 0 if all("✅" in r or "DRY-RUN" in r for r in results) else 1

if __name__ == "__main__":
    exit(main())