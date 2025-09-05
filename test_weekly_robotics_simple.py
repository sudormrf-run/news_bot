#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
간단한 Weekly Robotics 테스트
"""

import os
import sys
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.summarizers.weekly_robotics import WeeklyRoboticsSummarizer

# 테스트
summarizer = WeeklyRoboticsSummarizer()
url = "https://www.weeklyrobotics.com/weekly-robotics-315"

print("테스트 시작...")
try:
    result = summarizer.summarize(url)
    print(f"결과 길이: {len(result)}")
    print(f"결과:\n{result}")
except Exception as e:
    print(f"에러: {e}")
    import traceback
    traceback.print_exc()