#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Weekly Robotics Mock 테스트
실제 API 호출 없이 변경사항 확인
"""

import os
import sys

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.summarizers.compact import CompactSummarizer
from src.logger import setup_logger

setup_logger(level="INFO")

# Mock Weekly Robotics 요약 (실제 요약 예시)
mock_weekly_robotics = """![Weekly Robotics](https://www.weeklyrobotics.com/assets/img/wr-315.jpg)

## 🤖 이번 주 핵심 동향

이번 주에는 휴머노이드 로봇의 상용화 진전과 자율주행 기술의 안전성 개선이 주목받았습니다. 특히 Tesla의 Optimus 로봇 업데이트와 Waymo의 새로운 센서 기술이 업계의 관심을 끌었습니다.

## 📰 주요 뉴스

• **Tesla Optimus 손 동작 개선**: Tesla가 Optimus 로봇의 정밀한 손 제어 기능을 공개했습니다. 22개 자유도를 가진 손으로 계란을 깨지 않고 잡는 데모를 선보였습니다. [자세히 보기](https://example.com/tesla-optimus)

• **Boston Dynamics Atlas 전기 버전**: 유압식에서 전기 구동으로 전환한 새로운 Atlas를 발표했습니다. 더 조용하고 효율적인 작동이 특징입니다. [자세히 보기](https://example.com/atlas-electric)

• **Waymo 신규 라이다 센서**: 5세대 자율주행 시스템에 탑재될 새로운 라이다 센서를 공개했습니다. 기존 대비 2배 해상도와 500m 감지 거리를 달성했습니다. [자세히 보기](https://example.com/waymo-lidar)

• **ANYbotics 산업용 로봇 도입 확대**: ANYmal 로봇이 유럽 주요 화학 공장 10곳에 추가 배치되었습니다. 위험 지역 순찰과 가스 누출 감지에 활용됩니다. [자세히 보기](https://example.com/anybotics)

• **Figure 01 휴머노이드 BMW 공장 투입**: Figure의 휴머노이드 로봇이 BMW 생산 라인에서 시범 운영을 시작했습니다. 부품 운반과 단순 조립 작업을 수행합니다. [자세히 보기](https://example.com/figure-bmw)

## 🛠 기술 리소스

• **ROS 2 Jazzy 릴리스**: 최신 ROS 2 버전이 출시되었습니다. 실시간 성능 개선과 새로운 시뮬레이션 도구가 추가되었습니다. [링크](https://example.com/ros2-jazzy)

• **OpenCV 5.0 베타**: 컴퓨터 비전 라이브러리 메이저 업데이트. GPU 가속과 신경망 추론 성능이 크게 향상되었습니다. [링크](https://example.com/opencv5)

• **Robotics Transformer 2 논문**: Google이 발표한 새로운 로봇 학습 아키텍처. 비전-언어 모델을 활용한 제로샷 태스크 수행이 가능합니다. [링크](https://example.com/rt2-paper)

---
📖 출처: [Weekly Robotics #315](https://www.weeklyrobotics.com/weekly-robotics-315)"""

print("=" * 60)
print("Weekly Robotics Mock 테스트")
print("=" * 60)

print("\n1️⃣ GitHub Discussion용 내용 (썸네일 포함):")
print("-" * 40)
print(mock_weekly_robotics[:500] + "...")
print("-" * 40)

# 체크 사항
print("\n✅ 체크리스트:")
if "# Weekly Robotics #" not in mock_weekly_robotics:
    print("  ✓ 제목 제거됨")
else:
    print("  ✗ 제목이 여전히 있음")

if "![Weekly Robotics](" in mock_weekly_robotics:
    print("  ✓ 썸네일 추가됨")
else:
    print("  ✗ 썸네일 없음")

if mock_weekly_robotics.strip().endswith(")"):
    print("  ✓ 출처가 하단에 있음")
else:
    print("  ✗ 출처가 하단에 없음")

# Discord용 변환
print("\n2️⃣ Discord용 변환 (썸네일 제거):")

# 썸네일 제거
lines = mock_weekly_robotics.split('\n')
filtered_lines = []
for line in lines:
    if not line.startswith('![Weekly Robotics]('):
        filtered_lines.append(line)
content_for_discord = '\n'.join(filtered_lines).strip()

print("-" * 40)
print(content_for_discord[:300] + "...")
print("-" * 40)

# Compact 버전 테스트
print("\n3️⃣ Compact 요약 생성 테스트:")
try:
    compact = CompactSummarizer()
    github_url = "https://github.com/sudormrf-run/community/discussions/123"
    
    # Compact 요약 생성 시뮬레이션 (실제 API 호출 없이)
    mock_compact = f"""# Robotics News [25.09.15]

## 🤖 핵심 뉴스
• **Tesla Optimus 손 동작 개선**: 22개 자유도 손으로 계란 잡기 성공
• **Boston Dynamics Atlas 전기 버전**: 유압→전기 전환으로 조용하고 효율적
• **Waymo 5세대 라이다**: 2배 해상도, 500m 감지 거리 달성

## 📊 주요 트렌드
• 휴머노이드 로봇 상용화 가속
• 자율주행 센서 기술 고도화
• 산업 현장 로봇 도입 확대

---
📖 상세 뉴스레터: {github_url}"""

    print(mock_compact)
    print("-" * 40)
    
    print("\n✅ Compact 체크리스트:")
    if "# Robotics News" in mock_compact:
        print("  ✓ Robotics News 제목 사용")
    else:
        print("  ✗ AI News 제목이 사용됨")
    
    if github_url in mock_compact:
        print("  ✓ GitHub URL 포함")
    else:
        print("  ✗ GitHub URL 없음")
    
    print(f"  ✓ 길이: {len(mock_compact)}자 (2000자 이내)")
    
except Exception as e:
    print(f"❌ Compact 생성 에러: {e}")

print("\n" + "=" * 60)