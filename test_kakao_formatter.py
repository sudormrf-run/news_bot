#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KakaoFormatter 테스트
마크다운을 카카오톡용 플레인 텍스트로 변환 테스트
"""

import os
import sys

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.formatters.kakao import KakaoFormatter, save_kakao_text
from src.logger import setup_logger

setup_logger(level="INFO")

# Mock Discord 콘텐츠
mock_discord_content = """# AI News [25.09.05]

## 🔥 핵심 뉴스
• **OpenAI gpt-realtime 출시**: OpenAI가 음성-음성 대화가 가능한 gpt-realtime과 Realtime API를 정식 출시했습니다. [자세히 보기](https://openai.com/blog/realtime)
• **xAI Grok Code Fast**: xAI가 속도 우선 코딩 모델을 IDE에 통합했습니다. [자세히 보기](https://x.com/xai/status/123)
• **Microsoft 새 모델 발표**: MAI-1-preview와 MAI-Voice-1을 공개했습니다. [자세히 보기](https://microsoft.com/ai)

## 📊 주요 트렌드
• 음성 인터페이스 기술 발전
• IDE와 AI 통합 가속화
• 멀티모달 AI 모델 확산

---
📖 상세 뉴스레터: https://github.com/sudormrf-run/community/discussions/123"""

mock_robotics_content = """# Robotics News [25.09.15]

## 🤖 핵심 뉴스
• **Tesla Optimus 손 동작**: 22개 자유도 손으로 계란 잡기 성공. [자세히 보기](https://tesla.com/optimus/demo)
• **Boston Dynamics Atlas**: 유압에서 전기 구동으로 전환. [자세히 보기](https://bostondynamics.com/atlas)

## 📊 주요 트렌드
• 휴머노이드 로봇 상용화
• 전기 구동 시스템 채택

---
📖 상세 뉴스레터: https://github.com/sudormrf-run/community/discussions/456"""

print("=" * 60)
print("KakaoFormatter 테스트")
print("=" * 60)

formatter = KakaoFormatter()

print("\n1️⃣ AI News 변환 테스트:")
print("-" * 40)

kakao_text = formatter.format(mock_discord_content)

print("원본 마크다운 길이:", len(mock_discord_content))
print("변환된 텍스트 길이:", len(kakao_text))

print("\n변환 결과:")
print(kakao_text)

# 체크리스트
print("\n✅ 변환 체크리스트:")
if '#' not in kakao_text:
    print("  ✓ 헤더 마크다운 제거됨")
else:
    print("  ✗ 헤더 마크다운이 남아있음")

if '**' not in kakao_text:
    print("  ✓ Bold 마크다운 제거됨")
else:
    print("  ✗ Bold 마크다운이 남아있음")

if '[자세히 보기](' not in kakao_text:
    print("  ✓ 링크 형식 변환됨")
else:
    print("  ✗ 마크다운 링크가 남아있음")

if 'ㆍ' in kakao_text:
    print("  ✓ 불릿 포인트 변환됨")
else:
    print("  ✗ 불릿 포인트 변환 안됨")

print("\n" + "=" * 60)
print("\n2️⃣ Robotics News 변환 테스트:")
print("-" * 40)

kakao_text_robotics = formatter.format(mock_robotics_content)
print("변환 결과:")
print(kakao_text_robotics)

# 파일 저장 테스트
print("\n" + "=" * 60)
print("\n3️⃣ 파일 저장 테스트:")
print("-" * 40)

test_filename = "test_kakao_output.txt"
save_kakao_text(test_filename, kakao_text)

if os.path.exists(test_filename):
    print(f"✅ 파일 저장 성공: {test_filename}")
    
    # 저장된 파일 읽기
    with open(test_filename, 'r', encoding='utf-8') as f:
        saved_content = f.read()
    
    if saved_content == kakao_text:
        print("✅ 저장된 내용이 일치합니다")
    else:
        print("❌ 저장된 내용이 다릅니다")
    
    # 테스트 파일 삭제
    os.remove(test_filename)
    print(f"🧹 테스트 파일 삭제됨: {test_filename}")
else:
    print(f"❌ 파일 저장 실패")

print("\n" + "=" * 60)