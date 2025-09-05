#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
생성된 마크다운을 GitHub Discussions에 올리는 스크립트
"""

import os
import sys
import argparse
from datetime import datetime
import re

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.publishers.github import GitHubPublisher
from src.logger import setup_logger, logger
from src.config import Config

def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="생성된 마크다운을 GitHub Discussions에 게시"
    )
    
    parser.add_argument(
        "markdown_file",
        help="게시할 마크다운 파일 경로"
    )
    
    parser.add_argument(
        "--title",
        help="Discussion 제목 (기본: 파일명에서 자동 생성)"
    )
    
    parser.add_argument(
        "--extract-headline",
        action="store_true",
        help="마크다운에서 헤드라인 자동 추출"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 게시하지 않고 시뮬레이션"
    )
    
    return parser.parse_args()

def extract_headline_from_markdown(content: str) -> str:
    """마크다운에서 헤드라인 추출"""
    # "오늘의 요약" 섹션 찾기
    summary_match = re.search(r'## 오늘의 요약\s*\n(.*?)(?:\n##|\Z)', content, re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1).strip()
        # 첫 번째 불릿 포인트나 문장 추출
        first_item = re.search(r'[-*]\s*(.+?)(?:\n|$)', summary_text)
        if first_item:
            headline = first_item.group(1).strip()
            # 링크 제거
            headline = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', headline)
            # 15자로 제한
            if len(headline) > 15:
                headline = headline[:15] + "..."
            return headline
    return ""

def generate_title_from_filename(filename: str, headline: str = "") -> str:
    """파일명에서 제목 생성"""
    basename = os.path.basename(filename)
    
    # SmolAI News 형식 확인
    date_match = re.search(r'smol_ai_news_(\d{4})(\d{2})(\d{2})', basename)
    if date_match:
        year = date_match.group(1)
        month = date_match.group(2)
        day = date_match.group(3)
        date_str = f"{year[-2:]}.{month}.{day}"
    else:
        # 일반 형식
        date_match = re.search(r'(\d{4})(\d{2})(\d{2})', basename)
        if date_match:
            year = date_match.group(1)
            month = date_match.group(2)
            day = date_match.group(3)
            date_str = f"{year[-2:]}.{month}.{day}"
        else:
            # 현재 날짜 사용
            date_str = datetime.now().strftime("%y.%m.%d")
    
    if headline:
        return f"[AI News, {date_str}] {headline}"
    else:
        return f"[AI News, {date_str}] AI 뉴스 요약"

def main():
    """메인 함수"""
    args = parse_arguments()
    
    # 로거 초기화
    setup_logger(level="INFO")
    
    # 마크다운 파일 읽기
    if not os.path.exists(args.markdown_file):
        logger.error(f"파일을 찾을 수 없습니다: {args.markdown_file}")
        return 1
    
    with open(args.markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    logger.info(f"📄 파일 읽기: {args.markdown_file}")
    logger.info(f"   크기: {len(content)} 글자")
    
    # 제목 생성
    if not args.title:
        headline = ""
        if args.extract_headline:
            headline = extract_headline_from_markdown(content)
            if headline:
                logger.info(f"📝 추출된 헤드라인: {headline}")
        
        args.title = generate_title_from_filename(args.markdown_file, headline)
        logger.info(f"📌 자동 생성 제목: {args.title}")
    
    # GitHub Publisher 초기화
    publisher = GitHubPublisher(
        repo="sudormrf-run/community",  # 직접 지정
        category="News"
    )
    
    if not publisher.validate_config():
        logger.error("❌ GitHub 설정이 올바르지 않습니다")
        logger.error("필요한 환경변수:")
        logger.error("  - GITHUB_TOKEN")
        logger.error("  - GH_DISCUSSION_CATEGORY=News")
        return 1
    
    logger.info("✅ GitHub 설정 확인 완료")
    logger.info(f"   Repository: {publisher.repo}")
    logger.info(f"   Category: {publisher.category}")
    
    if args.dry_run:
        logger.info("[DRY-RUN] 실제 게시하지 않고 시뮬레이션")
        logger.info(f"제목: {args.title}")
        logger.info(f"내용: {len(content)} 글자")
        return 0
    
    # Discussion 게시
    logger.info("📤 GitHub Discussions 게시 중...")
    
    result_data = {}
    success = publisher.publish(
        content,
        title=args.title,
        **result_data
    )
    
    if success:
        logger.info("✅ GitHub Discussion 게시 성공!")
        if 'discussion_url' in result_data:
            logger.info(f"🔗 URL: {result_data['discussion_url']}")
    else:
        logger.error("❌ GitHub Discussion 게시 실패")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())