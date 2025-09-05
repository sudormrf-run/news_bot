#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CompactSummarizer 테스트
간결한 Discord 요약 생성 기능 확인
"""

import os
import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.summarizers.compact import CompactSummarizer
from src.config import Config
from src.logger import setup_logger, logger


def test_compact_summarizer():
    """CompactSummarizer 테스트"""
    
    # 로거 설정
    setup_logger(level="DEBUG")
    
    # 테스트용 전체 요약 (실제 SmolAI 요약 예시)
    full_content = """# AI News Summary - 2025.09.01

## 오늘의 요약

### 🚀 주요 뉴스
- **OpenAI gpt-realtime 정식 출시**: OpenAI가 gpt-realtime(음성-음성)과 Realtime API를 정식으로 출시했습니다. 가격이 20% 인하되었으며, 음성 제어, 다국어 전환, 신규 보이스 추가 등 다양한 기능이 개선되었습니다.
- **xAI Grok Code Fast 1**: xAI가 "속도-우선" 코딩 모델을 주요 IDE와 도구에 통합했습니다. 빠른 응답 속도가 특징이며, 1주간 무료 체험 제공 중입니다.
- **Microsoft MAI-1-preview 발표**: Microsoft가 MAI-1-preview와 MAI-Voice-1 모델을 공개했습니다. 새로운 음성 AI 모델로 주목받고 있습니다.
- **Cohere 번역 특화 모델**: Cohere가 다국어 번역에 특화된 새로운 모델을 출시했습니다. 100개 이상의 언어를 지원합니다.
- **ByteDance USO 공개**: ByteDance가 스타일 편집을 위한 오픈소스 도구 USO를 공개했습니다.

### 💡 기술 트렌드
1. **음성 AI의 진화**: 실시간 음성 처리와 다국어 전환 기능이 크게 향상
2. **IDE 통합 가속화**: AI 코딩 도구들이 개발 환경에 더욱 깊이 통합
3. **오픈소스 경쟁 심화**: 대기업들이 경쟁적으로 AI 도구를 오픈소스로 공개

### 🔍 상세 분석
각 기업들이 자사의 강점을 살린 특화 모델들을 경쟁적으로 출시하고 있으며, 
특히 음성 AI와 코딩 도구 분야에서 혁신이 두드러지고 있습니다.

## 출처
- https://openai.com/index/introducing-gpt-realtime/
- https://twitter.com/xai/status/1961129789944627207
- https://twitter.com/kevinweil/status/1960854500278985189
- https://twitter.com/mustafasuleyman/status/1961111770422186452
"""
    
    logger.info("=" * 60)
    logger.info("CompactSummarizer 테스트 시작")
    logger.info("=" * 60)
    
    try:
        # CompactSummarizer 초기화
        compact = CompactSummarizer()
        
        # 설정 검증
        if not compact.validate_config():
            logger.error("❌ OpenAI API 키가 설정되지 않았습니다.")
            logger.info("💡 .env 파일에 OPENAI_API_KEY를 설정하세요.")
            return
        
        logger.info("✅ CompactSummarizer 초기화 완료")
        logger.info(f"📝 원본 콘텐츠 길이: {len(full_content)}자")
        
        # 간결한 요약 생성
        logger.info("\n" + "=" * 40)
        logger.info("Discord 스타일 간결 요약 생성 중...")
        logger.info("=" * 40)
        
        result = compact.summarize_with_metadata(
            full_content,
            github_url="https://github.com/orgs/sudormrf-run/discussions/123",
            style="discord",
            max_length=2000
        )
        
        if result and result.get('markdown'):
            logger.info(f"\n✅ 간결 요약 생성 성공!")
            logger.info(f"📊 글자수: {result['char_count']}자")
            logger.info(f"🎨 스타일: {result['style']}")
            logger.info("\n" + "=" * 40)
            logger.info("📝 생성된 Discord 요약:")
            logger.info("=" * 40)
            print("\n" + result['markdown'])
            logger.info("\n" + "=" * 40)
            
            # 2000자 제한 확인
            if result['char_count'] <= 2000:
                logger.info("✅ Discord 2000자 제한 충족")
            else:
                logger.warning(f"⚠️ Discord 2000자 제한 초과: {result['char_count']}자")
        else:
            logger.error("❌ 간결 요약 생성 실패")
            
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_compact_summarizer()