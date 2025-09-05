#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
최종 워크플로우 테스트 - 프롬프트 개선 확인
"""

import os
import sys

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.summarizers.weekly_robotics import WeeklyRoboticsSummarizer
from src.publishers.discord import DiscordPublisher
from src.logger import logger, setup_logger

# 로거 초기화
setup_logger(level="INFO")

# 테스트
summarizer = WeeklyRoboticsSummarizer()
url = "https://www.weeklyrobotics.com/weekly-robotics-315"

print("=" * 60)
print("Weekly Robotics 최종 테스트")
print("=" * 60)

try:
    # 1. 요약 생성 (새 프롬프트로)
    print("\n1️⃣ 요약 생성 중... (프롬프트 개선 확인)")
    result = summarizer.summarize_with_result(url)
    
    print("\n📋 메타데이터:")
    print(f"  - 헤드라인: {result.metadata.get('headline')}")
    print(f"  - 날짜: {result.metadata.get('date')}")
    
    # 2. 링크 중복 확인
    print("\n2️⃣ 링크 중복 체크:")
    import re
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', result.summary)
    url_counts = {}
    for text, url in links:
        url_counts[url] = url_counts.get(url, 0) + 1
        
    duplicates = {url: count for url, count in url_counts.items() if count > 1}
    if duplicates:
        print("  ⚠️ 중복 링크 발견:")
        for url, count in duplicates.items():
            print(f"    - {url[:50]}... : {count}번")
    else:
        print("  ✅ 중복 링크 없음")
    
    # 3. Discord 임베드 비활성화 테스트
    print("\n3️⃣ Discord 링크 처리 테스트:")
    discord = DiscordPublisher()
    
    # GitHub URL 시뮬레이션
    github_url = "https://github.com/orgs/example/discussions/123"
    discord_content = result.summary + f"\n\n---\n📖 **상세 뉴스레터**: {github_url}"
    
    # 링크 처리
    processed = discord._disable_link_embeds(discord_content)
    
    # 확인
    processed_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', processed)
    print("  처리된 링크 예시 (첫 3개):")
    for i, (text, url) in enumerate(processed_links[:3]):
        if url.startswith('<') and url.endswith('>'):
            print(f"    ✅ [{text}]({url[:30]}...) - 임베드 비활성화")
        else:
            print(f"    ⚠️ [{text}]({url[:30]}...) - 임베드 활성")
    
    # GitHub 링크 확인
    for text, url in processed_links:
        if 'github.com' in url and 'discussions' in url:
            if not (url.startswith('<') and url.endswith('>')):
                print(f"    ✅ GitHub Discussion 링크는 임베드 유지: {url[:50]}...")
                break
    
    # 4. 출력 샘플
    print("\n4️⃣ 최종 출력 샘플 (첫 800자):")
    print("-" * 40)
    print(processed[:800])
    print("-" * 40)
    
except Exception as e:
    print(f"❌ 에러: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)