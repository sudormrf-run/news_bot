#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Weekly Robotics 헤드라인 추출 테스트
"""

import os
import sys

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.summarizers.weekly_robotics import WeeklyRoboticsSummarizer
from src.logger import logger, setup_logger

# 로거 초기화
setup_logger(level="INFO")

# 테스트
summarizer = WeeklyRoboticsSummarizer()
url = "https://www.weeklyrobotics.com/weekly-robotics-315"

print("=" * 60)
print("Weekly Robotics 헤드라인 추출 테스트")
print("=" * 60)

try:
    # summarize_with_result 메서드 사용
    result = summarizer.summarize_with_result(url)
    
    print("\n📋 메타데이터:")
    print(f"  - 헤드라인: {result.metadata.get('headline')}")
    print(f"  - 날짜: {result.metadata.get('date')}")
    print(f"  - 이슈 번호: {result.metadata.get('issue_number')}")
    print(f"  - 소스: {result.metadata.get('source')}")
    
    print(f"\n📄 요약 내용 (첫 500자):")
    print("-" * 40)
    print(result.summary[:500])
    print("-" * 40)
    
    # 타이틀 생성 예시
    headline = result.metadata.get('headline')
    date = result.metadata.get('date')
    if headline and date:
        title = f"[Robotics News, {date}] {headline}"
        print(f"\n🏷️ GitHub Discussion 타이틀:")
        print(f"  {title}")
    
except Exception as e:
    print(f"❌ 에러: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)