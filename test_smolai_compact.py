#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SmolAI News Compact 버전 테스트
"""

import os
import sys

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 가상의 SmolAI 요약 (실제 요약 예시)
smolai_full_content = """## 오늘의 요약

오늘 AI 분야에서는 OpenAI의 gpt-realtime과 Realtime API 정식 출시, xAI의 속도 우선 코딩 모델, Microsoft의 새로운 AI 모델 발표 등이 주목받았습니다.

## AI Twitter Recap — 주목할 만한 발표와 논쟁

### 주요 트윗
- **OpenAI gpt-realtime 출시**: OpenAI가 gpt-realtime(음성-음성)과 Realtime API를 정식 출시하며 가격을 20% 인하했습니다. 음성 제어, 다국어 전환, 신규 보이스 추가 등 기능이 개선되었습니다. [공식 발표](https://openai.com/blog/realtime)
- **xAI Grok Code Fast 1**: xAI가 "속도-우선" 코딩 모델을 주요 IDE와 도구에 통합했습니다. 빠른 응답속도에 중점을 둔 모델입니다. [트윗](https://x.com/xai/status/123)
- **OpenAI Codex 업데이트**: Codex가 IDE 확장, 로컬 CLI 등으로 대폭 재정비되었습니다. [발표](https://openai.com/codex)

## AI Reddit Recap — 커뮤니티 반응

### 인기 토픽
- **Llama 3.3 70B 성능**: Meta의 Llama 3.3 70B가 벤치마크에서 뛰어난 성능을 보였다는 보고
- **OpenAI 가격 정책**: Realtime API 가격 인하에 대한 긍정적 반응
- **오픈소스 vs 클로즈드 모델**: 지속적인 논쟁

## AI Discord Recap — 개발자 커뮤니티

### 핫이슈
- **Claude 3.5 Sonnet 업데이트**: 성능 향상과 새로운 기능 추가
- **로컬 LLM 최적화**: Ollama와 LM Studio 최신 버전 비교
"""

# 테스트 실행
print("=" * 60)
print("SmolAI News Compact 버전 테스트")
print("=" * 60)

try:
    from src.summarizers.compact import CompactSummarizer
    from src.logger import setup_logger
    
    setup_logger(level="INFO")
    
    # GitHub URL 시뮬레이션
    github_url = "https://github.com/orgs/example/discussions/123"
    
    # Compact 버전 생성
    print("\n1️⃣ Compact 버전 생성 중...")
    compact = CompactSummarizer()
    compact_content = compact.summarize(
        content=smolai_full_content,
        github_url=github_url,
        style="discord"
    )
    
    print("\n2️⃣ 결과 비교:")
    print(f"원본 길이: {len(smolai_full_content)}자")
    print(f"Compact 길이: {len(compact_content)}자")
    print(f"압축률: {(1 - len(compact_content)/len(smolai_full_content))*100:.1f}%")
    
    print("\n3️⃣ Compact 버전 내용:")
    print("-" * 40)
    print(compact_content)
    print("-" * 40)
    
    # GitHub URL 포함 확인
    if github_url in compact_content:
        print("\n✅ GitHub Discussion 링크 포함됨")
    else:
        print("\n⚠️ GitHub Discussion 링크 누락")
        
except Exception as e:
    print(f"\n❌ 오류: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)