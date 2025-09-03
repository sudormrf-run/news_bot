# -*- coding: utf-8 -*-
"""
Smol AI News Summarizer
https://news.smol.ai 전용 요약 생성기
"""

from typing import Optional, List
from openai import OpenAI

from .base import BaseSummarizer
from ..config import Config
from ..logger import logger, log_execution_time


class SmolAINewsSummarizer(BaseSummarizer):
    """Smol AI News 전용 Summarizer"""
    
    # Smol AI News 전용 프롬프트
    SYSTEM_PROMPT = """당신은 기술 뉴스레터 편집자입니다. 입력 URL의 페이지에서 'AI Twitter Recap', 'AI Reddit Recap', 'AI Discord Recap' 섹션만 다룹니다.
톤/언어: 한국어, 공적이고 전문적인 문체(높임말), 과장·아부 금지.
핵심 규칙:
- 원문 출처 링크를 "그대로" 보존하고 문장 안에 자연스럽게 마크다운 링크로 삽입합니다(앵커 텍스트가 있으면 그대로 사용).
- 각 섹션은 ① **한 줄 총평**(굵게, 1~2문장) → ② 핵심 항목 불릿 3~7개 → ③ (필요 시) `> *용어 메모* — ...` 순.
- 새 용어는 괄호로 간단히 부연설명합니다(예: MoE(전문가 혼합 아키텍처)).
- 시간 범위가 제공되면 머리말에 "YYYY-MM-DD ~ YYYY-MM-DD"로 명시.
- 지정된 3개 섹션 외 내용 금지.
- 결과는 마크다운만 출력합니다.
"""

    DEVELOPER_PROMPT = """[출력 포맷]
1) 섹션 헤더(정확히 아래 3개만):
   ## AI Twitter Recap — 한 줄 총평
   ## AI Reddit Recap — 한 줄 총평
   ## AI Discord Recap — 한 줄 총평
2) 각 섹션:
   - 첫 문단: **한 줄 총평**(굵게) 1~2문장
   - 불릿 3~7개: 각 항목마다 원문 링크를 [앵커](URL)로 삽입(중복 링크 금지)
   - (옵션) `> *용어 메모* — ...` 1~4줄
[링크 보존] 입력 페이지의 원래 앵커·URL을 우선 사용. web_search 보강은 불릿 끝 "[추가 참고]"로만.
[형식] 마크다운 단일 블록만 출력(프론트매터/HTML 금지).
"""

    TODAY_SUMMARY_PROMPT = """
## 오늘의 요약

위 세 섹션 중에서 가장 중요하고 흥미로운 소식 3-5개를 선별하여 간단히 요약해 주세요.
각 항목은 한 문장으로 작성하고, 원문 링크를 포함해 주세요.
"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Args:
            api_key: OpenAI API 키 (기본값: Config.OPENAI_API_KEY)
            model: 사용할 모델 (기본값: Config.OPENAI_MODEL)
        """
        super().__init__("Smol AI News", api_key, model)
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    def validate_config(self) -> bool:
        """설정 유효성 검사"""
        return bool(self.api_key)
    
    def get_supported_domains(self) -> list[str]:
        """지원하는 도메인 목록"""
        return ['news.smol.ai', 'smol.ai/issues']
    
    @log_execution_time
    def summarize(self, url: str, **kwargs) -> str:
        """Smol AI News 이슈 요약 생성
        
        Args:
            url: Smol AI News 이슈 URL
            timeframe: 기간 정보 (선택)
            include_today_summary: '오늘의 요약' 포함 여부 (선택)
        
        Returns:
            마크다운 형식의 요약
        """
        timeframe = kwargs.get('timeframe')
        include_today = kwargs.get('include_today_summary', False)
        
        # 사용자 프롬프트 구성
        user_text = (
            f"요약 대상 URL: {url}\n"
            "요청: 상기 페이지에서 'AI Twitter Recap', 'AI Reddit Recap', 'AI Discord Recap' "
            "세 섹션만 인용·요약하고, 원문 링크/앵커를 그대로 보존하여 한국어 마크다운으로 출력해 주세요. "
            + (f"기간 힌트: {timeframe}" if timeframe else "")
        )
        
        if include_today:
            user_text += f"\n\n{self.TODAY_SUMMARY_PROMPT}"
        
        # API 메시지 구성
        input_messages = [
            {"role": "system", "content": [{"type": "input_text", "text": self.SYSTEM_PROMPT}]},
            {"role": "developer", "content": [{"type": "input_text", "text": self.DEVELOPER_PROMPT}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_text}]},
        ]
        
        try:
            # OpenAI Responses API 호출
            logger.debug("Smol AI News 요약을 위한 OpenAI API 호출 중...")
            resp = self.client.responses.create(
                model=self.model,
                input=input_messages,
                tools=[{"type": "web_search"}],
                temperature=0.5,
            )
            
            # 응답에서 마크다운 추출
            md = self._extract_markdown(resp)
            
            if not md:
                raise RuntimeError("모델이 유효한 마크다운을 반환하지 않았습니다.")
            
            return md.strip()
            
        except Exception as e:
            logger.error(f"Smol AI News 요약 생성 실패: {str(e)}", exc_info=True)
            raise
    
    def _extract_markdown(self, response) -> str:
        """API 응답에서 마크다운 텍스트 추출
        
        Args:
            response: OpenAI API 응답 객체
        
        Returns:
            추출된 마크다운 텍스트
        """
        # SDK 버전에 따라 output_text가 없을 수 있으므로 안전 추출
        md = getattr(response, "output_text", None)
        
        if not md:
            chunks: List[str] = []
            for item in getattr(response, "output", []) or []:
                if getattr(item, "type", "") == "message":
                    for content in getattr(item, "content", []) or []:
                        if getattr(content, "type", "") == "output_text":
                            chunks.append(getattr(content, "text", ""))
            md = "\n".join(chunks).strip()
        
        return md
    
    def summarize_with_retry(
        self, 
        url: str, 
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """재시도 로직이 포함된 요약 생성
        
        Args:
            url: Smol AI News 이슈 URL
            max_retries: 최대 재시도 횟수
            **kwargs: summarize 메서드에 전달할 추가 인자
        
        Returns:
            마크다운 형식의 요약
        
        Raises:
            RuntimeError: 모든 재시도 실패 시
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"재시도 {attempt}/{max_retries}")
                
                return self.summarize(url, **kwargs)
                
            except Exception as e:
                last_error = e
                logger.warning(f"시도 {attempt + 1} 실패: {str(e)}")
                
                if attempt < max_retries - 1:
                    import time
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"{wait_time}초 대기 후 재시도...")
                    time.sleep(wait_time)
        
        raise RuntimeError(f"모든 재시도 실패: {str(last_error)}")