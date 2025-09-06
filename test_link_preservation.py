#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
링크 보존 테스트
X.com/Twitter 링크가 올바르게 보존되는지 확인
"""

import os
import sys

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.link_preserver import LinkPreserver
from src.logger import setup_logger

setup_logger(level="INFO")

# 테스트용 콘텐츠 (실제 SmolAI 출력 예시)
test_content = """## AI Twitter Recap

**OpenAI gpt-realtime 출시**: OpenAI가 음성-음성 대화가 가능한 gpt-realtime을 발표했습니다. [공식 발표](https://openai.com/blog/realtime), [트윗](https://x.com/openai/status/1234567890123456789)

**xAI Grok Code Fast**: 속도 우선 코딩 모델이 통합되었습니다. [발표](https://x.com/xai/status/9876543210987654321), [데모](https://x.com/elonmusk/status/1111222233334444555)

## AI Reddit Recap

Llama 3.3 70B 성능이 뛰어나다는 보고가 있었습니다. [원문](https://reddit.com/r/LocalLLaMA/comments/abc123), [벤치마크](https://huggingface.co/meta-llama/Llama-3.3-70B)

## AI Discord Recap

Claude 3.5 Sonnet 업데이트가 화제입니다. [Discord 토론](https://discord.com/channels/123/456), [Anthropic 발표](https://x.com/anthropic/status/5555666677778888999)"""

print("=" * 60)
print("링크 보존 테스트")
print("=" * 60)

# LinkPreserver 초기화
preserver = LinkPreserver()

print("\n1️⃣ 원본 콘텐츠:")
print("-" * 40)
print(test_content[:300] + "...")
print("-" * 40)

# 링크 추출
original_links = preserver.extract_links(test_content)
print(f"\n✅ 원본에서 {len(original_links)}개 링크 발견:")
for i, link in enumerate(original_links, 1):
    print(f"   {i}. {link[:60]}...")

# X.com 링크만 필터링
x_links = [link for link in original_links if 'x.com' in link or 'twitter.com' in link]
print(f"\n✅ X.com/Twitter 링크: {len(x_links)}개")
for link in x_links:
    print(f"   - {link}")

print("\n2️⃣ 링크 보존 처리:")
print("-" * 40)

# 링크를 placeholder로 치환
processed_content, link_map = preserver.preserve_links(test_content)

print(f"생성된 placeholder: {len(link_map)}개")
for placeholder, url in list(link_map.items())[:3]:
    print(f"   {placeholder} → {url[:50]}...")

print("\n처리된 콘텐츠 (일부):")
print(processed_content[:300] + "...")

print("\n3️⃣ 링크 복원:")
print("-" * 40)

# Placeholder를 원본 링크로 복원
restored_content = preserver.restore_links(processed_content, link_map)

print("복원된 콘텐츠 (일부):")
print(restored_content[:300] + "...")

# 검증
print("\n4️⃣ 검증:")
print("-" * 40)

restored_links = preserver.extract_links(restored_content)
print(f"복원 후 링크 수: {len(restored_links)}개")

# 원본과 비교
if set(original_links) == set(restored_links):
    print("✅ 모든 링크가 완벽하게 보존됨!")
else:
    missing = set(original_links) - set(restored_links)
    added = set(restored_links) - set(original_links)
    if missing:
        print(f"❌ 누락된 링크: {missing}")
    if added:
        print(f"❌ 추가된 링크: {added}")

# X.com 링크 status ID 검증
print("\n5️⃣ X.com Status ID 검증:")
print("-" * 40)

import re

original_x_status = re.findall(r'x\.com/[^/]+/status/(\d+)', test_content)
restored_x_status = re.findall(r'x\.com/[^/]+/status/(\d+)', restored_content)

print(f"원본 Status IDs: {original_x_status}")
print(f"복원 Status IDs: {restored_x_status}")

if original_x_status == restored_x_status:
    print("✅ 모든 X.com Status ID가 정확히 보존됨!")
else:
    print("❌ Status ID 불일치!")

print("\n" + "=" * 60)