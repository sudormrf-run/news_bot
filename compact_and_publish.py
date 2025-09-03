#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기존 마크다운 파일을 Compact Summary로 변환하고 Discord로 발송
"""

import os
import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.summarizers.compact import CompactSummarizer
from src.publishers.discord import DiscordPublisher
from src.logger import setup_logger, logger
from src.config import Config


def main():
    """메인 함수"""
    
    # 로거 설정
    setup_logger(level="INFO")
    
    logger.info("=" * 60)
    logger.info("📋 Compact Summary & Discord 발송 시작")
    logger.info("=" * 60)
    
    # 파일 경로와 GitHub URL
    input_file = "/Users/jonhpark/workspace/news_bot/outputs/2025/09/smol_ai_news_20250902.md"
    github_url = "https://github.com/orgs/sudormrf-run/discussions/6"
    
    try:
        # 1. 마크다운 파일 읽기
        logger.info(f"📖 마크다운 파일 읽기: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            full_content = f.read()
        logger.info(f"✅ 파일 읽기 완료 ({len(full_content)}자)")
        
        # 2. CompactSummarizer로 간결한 요약 생성
        logger.info("\n=== Compact Summary 생성 중 ===")
        compact = CompactSummarizer()
        
        if not compact.validate_config():
            logger.error("❌ OpenAI API 키가 설정되지 않았습니다.")
            return 1
        
        result = compact.summarize_with_metadata(
            full_content,
            github_url=github_url,
            style="discord",
            max_length=2000
        )
        
        if not result or not result.get('markdown'):
            logger.error("❌ Compact summary 생성 실패")
            return 1
        
        compact_content = result['markdown']
        logger.info(f"✅ Compact summary 생성 완료 ({result['char_count']}자)")
        
        # 생성된 요약 출력
        logger.info("\n" + "=" * 40)
        logger.info("📝 생성된 Discord 요약:")
        logger.info("=" * 40)
        print(compact_content)
        logger.info("=" * 40)
        
        # 3. Compact 버전 파일로 저장
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        compact_file = f"/Users/jonhpark/workspace/news_bot/outputs/2025/09/compact/discord_{timestamp}.md"
        
        os.makedirs(os.path.dirname(compact_file), exist_ok=True)
        with open(compact_file, 'w', encoding='utf-8') as f:
            f.write(compact_content)
        logger.info(f"💾 Compact 버전 저장: {compact_file}")
        
        # 4. Discord로 발송
        logger.info("\n=== Discord 발송 중 ===")
        discord = DiscordPublisher()
        
        if not discord.validate_config():
            logger.error("❌ Discord 웹훅이 설정되지 않았습니다.")
            logger.info("💡 .env 파일에 DISCORD_WEBHOOK_URL을 설정하세요.")
            return 1
        
        success = discord.publish(compact_content)
        
        if success:
            logger.info("✅ Discord 발송 성공!")
        else:
            logger.error("❌ Discord 발송 실패")
            return 1
        
        # 5. 결과 요약
        logger.info("\n" + "=" * 60)
        logger.info("📊 작업 완료 요약:")
        logger.info(f"  ✅ 원본 파일: {input_file}")
        logger.info(f"  ✅ Compact 저장: {compact_file}")
        logger.info(f"  ✅ Discord 발송: 성공")
        logger.info(f"  ✅ GitHub URL: {github_url}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ 처리 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())