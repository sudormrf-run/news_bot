#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Weekly Robotics 최종 테스트
- 제목 제거
- 썸네일 추가 
- 출처 하단 이동
- Discord용 Compact 버전
"""

import os
import sys
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.summarizers.weekly_robotics import WeeklyRoboticsSummarizer
from src.summarizers.compact import CompactSummarizer
from src.logger import setup_logger

setup_logger(level="INFO")

# 테스트
print("=" * 60)
print("Weekly Robotics 최종 테스트")
print("=" * 60)

summarizer = WeeklyRoboticsSummarizer()
url = "https://www.weeklyrobotics.com/weekly-robotics-315"

try:
    # 1. 전체 요약 생성
    print("\n1️⃣ 전체 요약 생성 중...")
    result = summarizer.summarize_with_result(url)
    
    print(f"\n✅ 요약 생성 완료")
    print(f"   헤드라인: {result.metadata.get('headline', 'N/A')}")
    print(f"   썸네일: {result.metadata.get('thumbnail', 'N/A')}")
    print(f"   길이: {len(result.summary)}자")
    
    print("\n2️⃣ GitHub Discussion용 내용:")
    print("-" * 40)
    print(result.summary[:500] + "..." if len(result.summary) > 500 else result.summary)
    print("-" * 40)
    
    # 제목 없는지 확인
    if "# Weekly Robotics #" in result.summary:
        print("\n⚠️ 경고: 제목이 여전히 포함되어 있습니다!")
    else:
        print("\n✅ 제목이 제거되었습니다")
    
    # 썸네일 있는지 확인
    if "![Weekly Robotics](" in result.summary:
        print("✅ 썸네일이 추가되었습니다")
    else:
        print("⚠️ 썸네일이 없습니다")
    
    # 출처가 하단에 있는지 확인
    if "📖 출처: [Weekly Robotics" in result.summary:
        print("✅ 출처가 하단에 있습니다")
    else:
        print("⚠️ 출처가 하단에 없습니다")
    
    # 2. Discord용 Compact 버전 생성
    print("\n3️⃣ Discord용 Compact 버전 생성 중...")
    
    # 썸네일 제거
    content_for_compact = result.summary
    lines = content_for_compact.split('\n')
    filtered_lines = []
    for line in lines:
        if not line.startswith('![Weekly Robotics]('):
            filtered_lines.append(line)
    content_for_compact = '\n'.join(filtered_lines).strip()
    
    compact = CompactSummarizer()
    github_url = "https://github.com/sudormrf-run/community/discussions/123"
    
    compact_content = compact.summarize(
        content=content_for_compact,
        github_url=github_url,
        style="discord"
    )
    
    print(f"\n✅ Compact 버전 생성 완료")
    print(f"   길이: {len(compact_content)}자")
    
    print("\n4️⃣ Discord 메시지 내용:")
    print("-" * 40)
    print(compact_content)
    print("-" * 40)
    
    # Robotics News 제목인지 확인
    if "# Robotics News" in compact_content:
        print("\n✅ Robotics News 제목이 사용되었습니다")
    else:
        print("⚠️ AI News 제목이 사용되고 있습니다")
    
except Exception as e:
    print(f"\n❌ 에러: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)