# -*- coding: utf-8 -*-
"""
Smol AI News Summarizer with Link Preservation
링크 보존 기능이 추가된 SmolAI News 요약기
"""

import re
from typing import Optional, Dict, Any, List
from openai import OpenAI

from .base import BaseSummarizer
from .postprocessors import SmolAIPostProcessor
from ..utils.link_preserver import LinkPreserver
from ..config import Config
from ..logger import logger, log_execution_time


class SmolAINewsWithLinkPreserveSummarizer(BaseSummarizer):
    """링크 보존 기능이 있는 Smol AI News Summarizer"""
    
    # 기본 프롬프트는 기존 SmolAI와 동일
    SYSTEM_PROMPT = """역할: 당신은 기술 뉴스레터 편집자입니다. 입력으로 제공된 뉴스레터 본문에서 AI Twitter Recap, AI Reddit Recap, AI Discord Recap 섹션만 다룹니다. 추가로 그날의 요약 섹션이 최상단에 있다면 그 내용도 다룹니다.

내용 읽기: 각 섹션의 핵심 뉴스와 논의를 한국어로 번역·정리하되, 제품명/서비스명/수치는 원어 유지. 가능한 원문의 링크와 앵커 텍스트를 재사용.

레이아웃: 마크다운 형식으로 ## AI Twitter Recap (한 줄 총평), ## AI Reddit Recap (한 줄 총평), ## AI Discord Recap (한 줄 총평) 세 섹션 각각 1) 한 줄 총평 정리, 2) 불릿 포인트로 핵심 항목 나열.

톤/언어: 기술 전문가를 대상으로 한 간결한 한국어. 불필요한 수식어 금지. 주장과 평가는 구분하고, 근거 링크 제시.

세 섹션 공통적으로 가장 첫번째 문장에는 '오늘의 요약' 문단을 보고 한 줄 총평으로 표현"""
    
    DEVELOPER_PROMPT = """마크다운 출력 규칙:
- 출처: [원문](링크) 형태로 마지막에 1회만.
- 각 섹션: ## AI [Platform] Recap — 한 줄 총평 형태로 제목을 작성
  - 한 줄 총평(굵게) 1~2문장 →
  - 핵심 항목 불릿: 주장/사례/평가 각각에 원문 링크를 마크다운 링크로 삽입.
  - 필요 시 > *용어 메모* — ... 형태로 1~4줄.
- 링크 보존 원칙: 
  * 모든 x.com/twitter.com 링크의 status ID를 정확히 보존
  * [LINK_XXXX] 형태의 placeholder를 발견하면 절대 변경하지 말 것
  * 링크의 숫자나 경로를 임의로 변경하지 말 것
- 링크 정리: 같은 URL은 중복 삽입하지 않음.
- 문장 다듬기: 과장/과도한 수사를 피하고, 사실-평가를 분리."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize with link preservation capability"""
        super().__init__("Smol AI News (Link Preserve)", api_key, model)
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, timeout=6000.0)
            self.postprocessor = SmolAIPostProcessor(api_key=self.api_key, model="gpt-5")
            self.link_preserver = LinkPreserver()
    
    def _intercept_web_search_response(self, response) -> tuple[Any, Dict[str, str]]:
        """web_search 도구 응답을 가로채서 링크를 보존
        
        Returns:
            (수정된 response, 링크 매핑)
        """
        link_map = {}
        
        try:
            # response에서 web_search 결과 추출
            if hasattr(response, 'output'):
                for item in response.output:
                    if hasattr(item, 'type') and item.type == 'tool_result':
                        if hasattr(item, 'tool_name') and item.tool_name == 'web_search':
                            # web_search 결과에서 콘텐츠 추출 및 링크 보존
                            if hasattr(item, 'content'):
                                # 링크 보존 처리
                                processed_content, link_map = self.link_preserver.preserve_links(item.content)
                                # 수정된 콘텐츠로 교체 (이 부분은 API 구조상 직접 수정이 어려울 수 있음)
                                logger.debug(f"Web search 결과에서 {len(link_map)}개 링크 보존")
        except Exception as e:
            logger.warning(f"web_search 응답 처리 중 오류: {e}")
        
        return response, link_map
    
    @log_execution_time
    def summarize_with_metadata(self, url: str, **kwargs) -> Dict[str, Any]:
        """링크 보존 기능이 있는 요약 생성"""
        timeframe = kwargs.get('timeframe')
        
        # 사용자 프롬프트
        user_text = (
            f"요약 대상 URL: {url}\n"
            "요청: 상기 페이지에서 'AI Twitter Recap', 'AI Reddit Recap', 'AI Discord Recap' "
            "세 섹션만 인용·요약하고, 원문 링크를 정확히 보존하여 한국어 마크다운으로 출력해 주세요. "
            "특히 x.com/twitter.com의 status ID 숫자를 절대 변경하지 마세요. "
            + (f"기간 힌트: {timeframe}" if timeframe else "")
        )
        
        input_messages = [
            {"role": "system", "content": [{"type": "input_text", "text": self.SYSTEM_PROMPT}]},
            {"role": "developer", "content": [{"type": "input_text", "text": self.DEVELOPER_PROMPT}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_text}]},
        ]
        
        try:
            # OpenAI API 호출
            logger.debug("링크 보존 SmolAI 요약 시작...")
            resp = self.client.responses.create(
                model=self.model,
                input=input_messages,
                tools=[{"type": "web_search"}],
                reasoning={"effort": "high"},
            )
            
            # 응답에서 마크다운 추출
            md = self._extract_markdown(resp)
            
            if not md:
                raise RuntimeError("모델이 유효한 마크다운을 반환하지 않았습니다.")
            
            # 링크 검증
            self._validate_links(md)
            
            # 후처리
            cleaned_md, headline = self.postprocessor.process_with_headline(md.strip(), original_source_url=url)
            
            # 날짜 추출
            date_match = re.search(r'(\d{2})-(\d{2})-(\d{2})', url)
            if date_match:
                date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
            else:
                from datetime import datetime
                date_str = datetime.now().strftime("%y.%m.%d")
            
            return {
                'markdown': cleaned_md.strip(),
                'headline': headline or "",
                'date': date_str
            }
            
        except Exception as e:
            logger.error(f"링크 보존 SmolAI 요약 실패: {str(e)}", exc_info=True)
            raise
    
    def _validate_links(self, content: str):
        """x.com 링크가 올바른지 검증"""
        x_links = re.findall(r'https?://(?:x\.com|twitter\.com)/[^/]+/status/(\d+)', content)
        
        if x_links:
            logger.info(f"발견된 x.com/twitter.com 링크: {len(x_links)}개")
            
            # Status ID 길이 검증 (일반적으로 19자리)
            for status_id in x_links[:5]:  # 처음 5개만 로그
                if len(status_id) != 19:
                    logger.warning(f"비정상적인 status ID 길이: {status_id} ({len(status_id)}자리)")
                else:
                    logger.debug(f"정상 status ID: {status_id}")
    
    def _extract_markdown(self, response) -> str:
        """응답에서 마크다운 추출"""
        try:
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
            
        except Exception as e:
            logger.error(f"마크다운 추출 실패: {str(e)}")
            return ""
    
    def summarize(self, url: str, **kwargs) -> str:
        """기본 요약 메서드"""
        result = self.summarize_with_metadata(url, **kwargs)
        return result.get('markdown', '')