#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compact 요약 GitHub 링크 테스트
Discord 발송 시 GitHub Discussion 링크가 포함되는지 확인
"""

import os
import sys

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.summarizers.compact import CompactSummarizer
from src.logger import setup_logger

setup_logger(level="INFO")

# Mock 뉴스 콘텐츠들
mock_smolai = """## 오늘의 요약

오늘 AI 분야에서는 OpenAI의 gpt-realtime과 Realtime API 정식 출시가 주목받았습니다.

## AI Twitter Recap

### 주요 트윗
- **OpenAI gpt-realtime 출시**: OpenAI가 gpt-realtime(음성-음성)과 Realtime API를 정식 출시했습니다.
- **xAI Grok Code Fast 1**: xAI가 "속도-우선" 코딩 모델을 통합했습니다."""

mock_weekly_robotics = """## 🤖 이번 주 핵심 동향

휴머노이드 로봇의 상용화 진전과 자율주행 기술의 안전성 개선이 주목받았습니다.

## 📰 주요 뉴스

• **Tesla Optimus 손 동작 개선**: 22개 자유도를 가진 손으로 계란을 잡는 데모를 선보였습니다.
• **Boston Dynamics Atlas 전기 버전**: 유압식에서 전기 구동으로 전환했습니다."""

print("=" * 60)
print("Compact 요약 GitHub 링크 테스트")
print("=" * 60)

# GitHub URL
github_url = "https://github.com/sudormrf-run/community/discussions/123"

# CompactSummarizer 테스트
compact = CompactSummarizer()

print("\n1️⃣ SmolAI News Compact 테스트:")
print("-" * 40)

try:
    result = compact.summarize_with_metadata(
        content=mock_smolai,
        github_url=github_url,
        style="discord"
    )
    
    compact_content = result['markdown']
    
    # GitHub URL 확인
    if github_url in compact_content:
        print("✅ GitHub URL이 포함되어 있습니다")
    else:
        print("❌ GitHub URL이 누락되었습니다")
    
    if "📖 상세 뉴스레터:" in compact_content:
        print("✅ '상세 뉴스레터' 텍스트가 있습니다")
    else:
        print("❌ '상세 뉴스레터' 텍스트가 없습니다")
    
    # 마지막 부분 출력
    lines = compact_content.split('\n')
    print("\n마지막 3줄:")
    for line in lines[-3:]:
        print(f"  {line}")
        
except Exception as e:
    print(f"❌ SmolAI 테스트 실패: {e}")

print("\n2️⃣ Weekly Robotics Compact 테스트:")
print("-" * 40)

try:
    result = compact.summarize_with_metadata(
        content=mock_weekly_robotics,
        github_url=github_url,
        style="discord"
    )
    
    compact_content = result['markdown']
    
    # GitHub URL 확인
    if github_url in compact_content:
        print("✅ GitHub URL이 포함되어 있습니다")
    else:
        print("❌ GitHub URL이 누락되었습니다")
    
    if "📖 상세 뉴스레터:" in compact_content:
        print("✅ '상세 뉴스레터' 텍스트가 있습니다")
    else:
        print("❌ '상세 뉴스레터' 텍스트가 없습니다")
    
    if "# Robotics News" in compact_content:
        print("✅ Robotics News 제목이 사용되었습니다")
    else:
        print("❌ AI News 제목이 사용되었습니다")
    
    # 마지막 부분 출력
    lines = compact_content.split('\n')
    print("\n마지막 3줄:")
    for line in lines[-3:]:
        print(f"  {line}")
        
except Exception as e:
    print(f"❌ Weekly Robotics 테스트 실패: {e}")

print("\n" + "=" * 60)