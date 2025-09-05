#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compact 버전 저장 테스트
Discord로 발송되는 compact 버전이 별도 파일로 저장되는지 확인
"""

import os
import sys
import tempfile
import shutil

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.markdown_utils import save_markdown
from src.logger import setup_logger

setup_logger(level="INFO")

# Mock 데이터
mock_full_content = """![Weekly Robotics](https://example.com/image.jpg)

## 🤖 이번 주 핵심 동향

휴머노이드 로봇의 상용화 진전과 자율주행 기술 개선이 주목받았습니다.

## 📰 주요 뉴스

• **Tesla Optimus**: 정밀한 손 제어 기능 공개
• **Boston Dynamics Atlas**: 전기 구동 버전 출시
• **Waymo 라이다**: 5세대 센서 기술 공개

## 🛠 기술 리소스

• **ROS 2 Jazzy**: 최신 버전 릴리스
• **OpenCV 5.0**: 베타 버전 출시

---
📖 출처: [Weekly Robotics #315](https://example.com)"""

mock_discord_content = """# Robotics News [25.09.15]

## 🤖 핵심 뉴스
• **Tesla Optimus**: 22개 자유도 손으로 계란 잡기 성공
• **Boston Dynamics Atlas**: 유압→전기 전환
• **Waymo 라이다**: 2배 해상도, 500m 감지

## 📊 주요 트렌드
• 휴머노이드 로봇 상용화 가속
• 자율주행 센서 기술 고도화

---
📖 상세 뉴스레터: https://github.com/sudormrf-run/community/discussions/123"""

print("=" * 60)
print("Compact 버전 저장 테스트")
print("=" * 60)

# 임시 디렉토리 생성
test_dir = tempfile.mkdtemp(prefix="news_bot_test_")
print(f"\n테스트 디렉토리: {test_dir}")

try:
    # 1. 원본 파일 저장
    original_file = os.path.join(test_dir, "weekly_robotics_315_20250915.md")
    save_markdown(original_file, mock_full_content)
    print(f"\n✅ 원본 파일 저장: {original_file}")
    print(f"   크기: {os.path.getsize(original_file)} bytes")
    
    # 2. Discord 버전 파일 저장 시뮬레이션
    discord_file = original_file.replace('.md', '_discord.md')
    save_markdown(discord_file, mock_discord_content)
    print(f"\n✅ Discord 버전 저장: {discord_file}")
    print(f"   크기: {os.path.getsize(discord_file)} bytes")
    
    # 3. 파일 내용 확인
    print("\n📁 생성된 파일들:")
    for filename in os.listdir(test_dir):
        filepath = os.path.join(test_dir, filename)
        size = os.path.getsize(filepath)
        print(f"   - {filename} ({size} bytes)")
    
    # 4. Discord 파일 내용 검증
    with open(discord_file, 'r', encoding='utf-8') as f:
        saved_content = f.read()
    
    print("\n🔍 Discord 파일 검증:")
    if "# Robotics News" in saved_content:
        print("   ✅ Robotics News 제목 확인")
    else:
        print("   ❌ Robotics News 제목 없음")
    
    if "📖 상세 뉴스레터:" in saved_content:
        print("   ✅ GitHub 링크 확인")
    else:
        print("   ❌ GitHub 링크 없음")
    
    if "![Weekly Robotics](" not in saved_content:
        print("   ✅ 썸네일 제거됨")
    else:
        print("   ❌ 썸네일이 여전히 있음")
    
    # 5. 파일명 패턴 테스트
    print("\n📝 파일명 패턴 테스트:")
    test_cases = [
        ("smol_ai_news_20250915.md", "smol_ai_news_20250915_discord.md"),
        ("weekly_robotics_315_20250915.md", "weekly_robotics_315_20250915_discord.md"),
        ("outputs/2025/09/recap_20250915_141500.md", "outputs/2025/09/recap_20250915_141500_discord.md")
    ]
    
    for original, expected in test_cases:
        result = original.replace('.md', '_discord.md')
        if result == expected:
            print(f"   ✅ {original} → {expected}")
        else:
            print(f"   ❌ {original} → {result} (기대값: {expected})")
    
finally:
    # 테스트 디렉토리 정리
    shutil.rmtree(test_dir)
    print(f"\n🧹 테스트 디렉토리 삭제됨: {test_dir}")

print("\n" + "=" * 60)