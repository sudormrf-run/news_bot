#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Weekly Robotics Summarizer 테스트 스크립트
"""

import os
import sys

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.summarizer import SummarizerFactory, NewsSource
from src.logger import logger, setup_logger
from src.publishers.discord import DiscordPublisher


def test_weekly_robotics():
    """Weekly Robotics summarizer 테스트"""
    
    # 로거 초기화
    setup_logger(level="INFO")
    
    # 테스트 URL
    test_url = "https://www.weeklyrobotics.com/weekly-robotics-315"
    
    logger.info("=" * 60)
    logger.info("Weekly Robotics Summarizer 테스트")
    logger.info(f"URL: {test_url}")
    logger.info("=" * 60)
    
    try:
        # 1. URL 기반 자동 감지 테스트
        logger.info("\n1. URL 자동 감지 테스트...")
        summarizer = SummarizerFactory.create_from_url(test_url)
        logger.info(f"✅ 감지된 Summarizer: {summarizer.name}")
        
        # 2. 명시적 생성 테스트
        logger.info("\n2. 명시적 생성 테스트...")
        summarizer2 = SummarizerFactory.create(NewsSource.WEEKLY_ROBOTICS)
        logger.info(f"✅ 생성된 Summarizer: {summarizer2.name}")
        
        # 3. 지원 도메인 확인
        logger.info("\n3. 지원 도메인 확인...")
        domains = summarizer.get_supported_domains()
        logger.info(f"지원 도메인: {domains}")
        
        # 4. URL 처리 가능 여부 확인
        logger.info("\n4. URL 처리 가능 여부...")
        can_handle = summarizer.can_handle(test_url)
        logger.info(f"처리 가능: {can_handle}")
        
        # 5. 요약 생성 테스트 (실제 API 호출 - 비용 발생 주의)
        logger.info("\n5. 요약 생성 테스트...")
        user_input = input("실제 요약을 생성하시겠습니까? (OpenAI API 비용 발생) [y/N]: ")
        
        if user_input.lower() == 'y':
            logger.info("요약 생성 중... (시간이 걸릴 수 있습니다)")
            
            # summarize_with_result 메서드가 있으면 사용
            if hasattr(summarizer, 'summarize_with_result'):
                result = summarizer.summarize_with_result(test_url)
                markdown_content = result.markdown
                metadata = result.metadata
                
                logger.info(f"\n📋 메타데이터:")
                for key, value in metadata.items():
                    logger.info(f"  - {key}: {value}")
            else:
                markdown_content = summarizer.safe_summarize(test_url)
                metadata = {}
            
            # 요약 미리보기
            logger.info(f"\n📄 요약 내용 (첫 500자):")
            logger.info("-" * 40)
            print(markdown_content[:500])
            logger.info("-" * 40)
            
            # 파일 저장 테스트
            save_input = input("\n파일로 저장하시겠습니까? [y/N]: ")
            if save_input.lower() == 'y':
                output_path = f"test_weekly_robotics_{metadata.get('issue_number', 'unknown')}.md"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                logger.info(f"✅ 파일 저장 완료: {output_path}")
            
            # Discord 발송 테스트
            discord_input = input("\nDiscord로 테스트 발송하시겠습니까? [y/N]: ")
            if discord_input.lower() == 'y':
                if Config.is_discord_enabled():
                    discord = DiscordPublisher()
                    if discord.safe_publish(markdown_content):
                        logger.info("✅ Discord 발송 성공")
                    else:
                        logger.error("❌ Discord 발송 실패")
                else:
                    logger.warning("Discord 웹훅이 설정되지 않았습니다.")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 테스트 완료!")
        
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {str(e)}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(test_weekly_robotics())