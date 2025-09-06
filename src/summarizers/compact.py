# -*- coding: utf-8 -*-
"""
Compact Summarizer
기존 전체 요약을 간결한 버전으로 재요약
"""

from typing import Dict, Any, Optional
from openai import OpenAI

from .base import BaseSummarizer
from ..config import Config
from ..logger import logger


class CompactSummarizer(BaseSummarizer):
    """전체 요약을 간결하게 재요약하는 Summarizer"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Args:
            api_key: OpenAI API 키
            model: 사용할 모델 (기본: gpt-5)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or "gpt-5"
        super().__init__("Compact Summarizer", self.api_key, self.model)
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, timeout=6000.0)
        else:
            self.client = None
    
    def summarize(self, content: str, **kwargs) -> str:
        """전체 요약을 간결하게 재요약
        
        Args:
            content: 전체 마크다운 콘텐츠 (URL 아님)
            **kwargs: 
                - github_url: GitHub Discussion URL
                - max_length: 최대 글자수 (기본 2000)
                - style: 요약 스타일 (discord, twitter, slack 등)
        
        Returns:
            간결한 마크다운 요약
        """
        result = self.summarize_with_metadata(content, **kwargs)
        return result['markdown']
    
    def summarize_with_metadata(self, content: str, **kwargs) -> Dict[str, Any]:
        """전체 요약을 간결하게 재요약 (메타데이터 포함)
        
        Args:
            content: 전체 마크다운 콘텐츠
            **kwargs: 추가 옵션
        
        Returns:
            {
                'markdown': 간결한 요약,
                'char_count': 글자수,
                'style': 스타일
            }
        """
        import re
        from datetime import datetime
        
        github_url = kwargs.get('github_url', '')
        max_length = kwargs.get('max_length', 2000)
        style = kwargs.get('style', 'discord')
        
        # content에서 날짜 추출 시도
        date_str = datetime.now().strftime("%y.%m.%d")
        date_patterns = [
            r'(\d{2})\.(\d{2})\.(\d{2})',  # YY.MM.DD
            r'20(\d{2})[/-](\d{2})[/-](\d{2})',  # 20YY-MM-DD or 20YY/MM/DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                if len(match.groups()) == 3:
                    date_str = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                break
        
        logger.info(f"간결한 요약 생성 시작 (날짜: {date_str}, 스타일: {style}, 최대 {max_length}자)")
        
        # 콘텐츠 소스 판별 (Weekly Robotics인지 AI News인지)
        # Weekly Robotics는 명시적으로 표시되어 있을 때만
        is_robotics = 'Weekly Robotics' in content or '출처: [Weekly Robotics' in content
        
        # Discord 스타일 프롬프트
        if is_robotics:
            system_prompt = """당신은 로보틱스 뉴스를 Discord용으로 간결하게 요약하는 전문가입니다.

아래 형식을 정확히 따라주세요. 날짜는 실제 뉴스 날짜를 사용하세요.

출력 형식:
# Robotics News [YY.MM.DD]

## 🤖 핵심 뉴스
• **[제목]**: [1-2문장 설명]. [자세히 보기](링크)
(3-5개 항목)

## 📊 주요 트렌드
• [트렌드 1]
• [트렌드 2]

---
📖 상세 뉴스레터: [GitHub Discussion URL]"""
        else:
            system_prompt = """당신은 AI 뉴스를 Discord용으로 간결하게 요약하는 전문가입니다.

아래 형식을 정확히 따라주세요. 날짜는 실제 뉴스 날짜를 사용하세요.

출력 형식:
# AI News [YY.MM.DD]

## 🔥 핵심 뉴스
• **[제목]**: [1-2문장 설명]. [자세히 보기](링크)
(3-5개 항목)

## 📊 주요 트렌드
• [트렌드 1]
• [트렌드 2]
• [트렌드 3]

---
📖 상세 뉴스레터: [GitHub Discussion 링크](실제 URL)

규칙:
1. 각 뉴스는 반드시 "**제목**: 설명. [자세히 보기](링크)" 형식
2. 설명은 1-2문장으로 핵심만
3. 가장 중요하고 영향력 있는 뉴스 3-5개만 선별
4. 트렌드는 전체 뉴스에서 도출되는 큰 흐름 2-3개
5. 전체 2000자 이내
6. 이모지 사용 필수 (🤖 🔥 📊 📖)
7. 기술 용어는 이해하기 쉽게"""
        
        # 1-shot example
        example_input = """## 요약
- OpenAI가 gpt‑realtime(음성‑음성)과 Realtime API를 정식 출시하고 가격 인하
- xAI Grok Code Fast 1: "속도‑우선" 코딩 모델을 주요 IDE/툴에 통합
- Microsoft MAI‑1‑preview와 MAI‑Voice‑1 발표
- Cohere 번역 특화 모델 출시
- ByteDance USO 오픈소스 스타일 편집 도구 공개"""
        
        example_output = """# AI News 25.09.04

## 🔥 핵심 뉴스
• **OpenAI, gpt-realtime 출시**: OpenAI가 gpt-realtime과 Realtime API를 공식 출시하며 가격을 20% 인하했습니다. 음성 제어, 다국어 전환, 신규 보이스 추가 등 다양한 기능이 개선되었습니다. [자세히 보기](https://openai.com/index/introducing-gpt-realtime/)
• **xAI, 속도 중심 코딩 모델 통합**: xAI가 주요 IDE와 도구에 "속도-우선" 코딩 모델을 통합했습니다. 1주 무료 체험이 제공됩니다. [자세히 보기](https://twitter.com/xai/status/1961129789944627207)
• **OpenAI Codex 업데이트**: OpenAI Codex가 IDE 확장과 로컬 CLI 등으로 재정비되었습니다. [자세히 보기](https://twitter.com/kevinweil/status/1960854500278985189)
• **Microsoft, 새로운 AI 모델 공개**: Microsoft가 MAI-1-preview와 MAI-Voice-1을 발표했습니다. [자세히 보기](https://twitter.com/mustafasuleyman/status/1961111770422186452)

## 📊 주요 트렌드
• 음성 인식 및 다국어 전환 기술 발전
• IDE와 도구에 AI 통합 증가
• AI 모델의 기능적 개선과 가격 인하 추세

---
📖 상세 뉴스레터: [GitHub Discussion 링크](https://github.com/orgs/sudormrf-run/discussions/4)"""
        
        news_type = "로보틱스" if is_robotics else "AI"
        user_prompt = f"""다음 {news_type} 뉴스 요약을 위 형식에 맞춰 Discord용으로 간결하게 재요약해주세요.

날짜: {date_str}
GitHub Discussion URL: {github_url if github_url else 'https://github.com/sudormrf-run/community/discussions'}

중요: 반드시 마지막에 다음 형식으로 GitHub 링크를 추가하세요:
---
📖 상세 뉴스레터: {github_url if github_url else 'GitHub Discussion 링크'}

원본 요약:
{content}"""
        
        try:
            if not self.client:
                logger.warning("OpenAI 클라이언트 없음, 템플릿 사용")
                compact_summary = self._create_template_summary(content, github_url, style)
            else:
                # OpenAI Responses API 호출 (GPT-5)
                logger.info("OpenAI Responses API 호출 시작 (GPT-5, reasoning: low)...")
                
                # Responses API 형식으로 메시지 구성
                input_messages = [
                    {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                    {"role": "user", "content": [{"type": "input_text", "text": example_input}]},
                    {"role": "assistant", "content": [{"type": "output_text", "text": example_output}]},
                    {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]}
                ]
                
                response = self.client.responses.create(
                    model=self.model,
                    input=input_messages,
                    reasoning={"effort": "low"}  # 빠른 응답을 위해 low 설정
                )
                
                # 응답에서 텍스트 추출
                compact_summary = self._extract_text_from_response(response)
                logger.info(f"OpenAI Responses API 응답 수신 완료")
                
                # GitHub URL이 없으면 추가
                if github_url and github_url not in compact_summary:
                    if not compact_summary.strip().endswith(github_url):
                        compact_summary = compact_summary.rstrip()
                        if "---" not in compact_summary[-100:]:  # 마지막 100자 내에 구분선이 없으면
                            compact_summary += "\n\n---"
                        compact_summary += f"\n📖 상세 뉴스레터: {github_url}"
            
            result = {
                'markdown': compact_summary,
                'char_count': len(compact_summary),
                'style': style
            }
            
            logger.info(f"간결한 요약 생성 완료 ({result['char_count']}자)")
            return result
            
        except Exception as e:
            logger.error(f"간결한 요약 생성 실패: {str(e)}")
            # 실패 시 기본 템플릿 반환
            return {
                'markdown': self._create_fallback_summary(github_url),
                'char_count': 0,
                'style': style
            }
    
    def _create_template_summary(self, content: str, github_url: str, style: str) -> str:
        """템플릿 기반 임시 요약 생성"""
        # TODO: 실제 LLM 호출로 대체
        template = f"""# 🤖 AI News Summary

## 📌 핵심 뉴스
• [주요 뉴스 1]
• [주요 뉴스 2]
• [주요 뉴스 3]

## 🔍 주요 트렌드
• [트렌드 분석]

---
📖 전체 요약: {github_url if github_url else '[GitHub Discussion]'}"""
        
        return template
    
    def _create_fallback_summary(self, github_url: str) -> str:
        """오류 시 기본 요약"""
        return f"AI 뉴스 요약이 생성되었습니다.\n\n📖 자세히 보기: {github_url}"
    
    def _extract_text_from_response(self, response) -> str:
        """Responses API 응답에서 텍스트 추출
        
        Args:
            response: OpenAI Responses API 응답 객체
        
        Returns:
            추출된 텍스트
        """
        # SDK 버전에 따라 output_text가 없을 수 있으므로 안전 추출
        text = getattr(response, "output_text", None)
        
        if not text:
            chunks = []
            for item in getattr(response, "output", []) or []:
                if getattr(item, "type", "") == "message":
                    for content in getattr(item, "content", []) or []:
                        if getattr(content, "type", "") == "output_text":
                            chunks.append(getattr(content, "text", ""))
            text = "\n".join(chunks).strip()
        
        return text
    
    def validate_config(self) -> bool:
        """설정 검증"""
        return bool(self.api_key)
    
    def get_supported_domains(self) -> list[str]:
        """지원 도메인 (해당 없음 - 콘텐츠 직접 처리)"""
        return []