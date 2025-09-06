# -*- coding: utf-8 -*-
"""
Smol AI News Summarizer
https://news.smol.ai 전용 요약 생성기
"""

from typing import Optional, List, Dict, Any
from openai import OpenAI

from .base import BaseSummarizer
from .postprocessors import SmolAIPostProcessor
from ..utils.link_preserver import LinkPreserver
from ..config import Config
from ..logger import logger, log_execution_time


class SmolAINewsSummarizer(BaseSummarizer):
    """Smol AI News 전용 Summarizer"""
    
    # Smol AI News 전용 프롬프트
    SYSTEM_PROMPT = """역할: 당신은 기술 뉴스레터 편집자입니다. 입력으로 제공된 뉴스레터 본문에서 AI Twitter Recap, AI Reddit Recap, AI Discord Recap 섹션만 다룹니다. 추가로 그날의 요약 섹션이 최상단에 있다면 그 내용도 다룹니다.

톤/언어: 한국어, 공적이고 전문적/건조한 문체. 아부·추임새 금지.

핵심 목표:
- 원문 출처 링크를 최대한 “그대로” 보존하여 본문에 자연스럽게 걸어 둘 것(앵커 텍스트가 있으면 그 텍스트를 사용).
- 각 리캡마다 한 줄 총평 → 핵심 항목 불릿 3~7개 → (필요 시) 용어 메모 순서.
- 수치·주장·발표는 반드시 관련 원본 링크를 문장 안 또는 끝에 마크다운 링크로 달 것.
- 요청 범위를 벗어난 섹션은 제외.
- 새 용어가 나오면 괄호로 짧은 부연설명(예: “MoE(전문가 혼합 아키텍처)”).
- 결과는 마크다운만 출력(프론트매터·HTML 불가).
- 제목은 ## 수준.
"""

    DEVELOPER_PROMPT = """출력 포맷 규칙
- AI Twitter Recap 섹션 위에 주요 이슈가 있었다면 요약이 있음. 그것도 최상단에 요약해서 작성할 것
- 최상단 3개 섹션만: ## AI Twitter Recap — 한 줄 총평, ## AI Reddit Recap — 한 줄 총평, ## AI Discord Recap — 한 줄 총평.
- 집계 범위는 생략해도 됨.
- 각 섹션은
  - 한 줄 총평(굵게) 1~2문장 →
  - 핵심 항목 불릿: 주장/사례/평가 각각에 원문 링크를 마크다운 링크로 삽입.
  - 필요 시 > *용어 메모* — ... 형태로 1~4줄.
  - 링크 보존 원칙: 입력에서 제공된 원본 앵커 텍스트와 URL을 그대로 우선 사용.
- 만약 hosted web_search 또는 외부 검색으로 추가 근거를 보강했다면, 새 링크는 해당 불릿의 끝에 **[추가 참고]**로 추가하되, 본문 핵심은 원문 링크를 우선.
- 링크 정리: 같은 URL은 중복 삽입하지 않음.
- 문장 다듬기: 과장/과도한 수사를 피하고, 사실-평가를 분리.
- 력은 마크다운 단일 블록만. 여백/구분선은 ---로만.
- 입력으로 제공된 원문 뉴스레터 링크는 한번만 명시하면 되니까 반복해서 입력을 넣지말고, 마지막에 출처로 한번만 명시해줘
- 연속적으로 중복된 링크는 사용자의 피로함을 불러일으키니, 링크는 하나만 잘 달아야 해, 같은 URL을 연속적으로 중복해서 작성하지 않도록 해. 
- x.com 링크들이 하위의 정확한 tweet 까지 잘 링크가 되어야해. 'x.com' 이라고만 URL 이 작성되면 사용자들은 정확한 출처를 보기가 힘들어. 유념해서 링크를 잘 작성해.
- [LINK_0001], [LINK_0002] 같은 placeholder를 발견하면 절대 변경하지 말고 그대로 유지할 것. 이것들은 나중에 원본 링크로 복원됨.
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
            self.client = OpenAI(api_key=self.api_key, timeout=6000.0)
            # SmolAI 전용 PostProcessor 초기화
            self.postprocessor = SmolAIPostProcessor(api_key=self.api_key, model="gpt-5")
    
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
        
        Returns:
            마크다운 형식의 요약
        """
        result = self.summarize_with_metadata(url, **kwargs)
        return result['markdown']
    
    @log_execution_time
    def summarize_with_metadata(self, url: str, **kwargs) -> Dict[str, Any]:
        """Smol AI News 요약과 메타데이터 생성
        
        Args:
            url: Smol AI News 이슈 URL
            timeframe: 기간 정보 (선택)
        
        Returns:
            {
                'markdown': 마크다운 형식의 요약,
                'headline': 추출된 헤드라인,
                'date': 날짜 정보
            }
        """
        timeframe = kwargs.get('timeframe')
        
        # 사용자 프롬프트 구성
        user_text = (
            f"요약 대상 URL: {url}\n"
            "요청: 상기 페이지에서 'AI Twitter Recap', 'AI Reddit Recap', 'AI Discord Recap' "
            "세 섹션만 인용·요약하고, 원문 링크/앵커를 그대로 보존하여 한국어 마크다운으로 출력해 주세요. "
            "중요: 모든 링크 placeholder ([LINK_0001] 형태)는 절대 변경하지 말고 그대로 유지하세요. "
            + (f"기간 힌트: {timeframe}" if timeframe else "")
        )
        
        # API 메시지 구성
        input_messages = [
            {"role": "system", "content": [{"type": "input_text", "text": self.SYSTEM_PROMPT}]},
            {"role": "developer", "content": [{"type": "input_text", "text": self.DEVELOPER_PROMPT}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_text}]},
        ]
        
        try:
            # LinkPreserver 초기화
            link_preserver = LinkPreserver()
            
            # OpenAI Responses API 호출
            logger.debug("Smol AI News 요약을 위한 OpenAI API 호출 중...")
            resp = self.client.responses.create(
                model=self.model,
                input=input_messages,
                tools=[{"type": "web_search"}],
                reasoning={"effort": "high"},
                #service_tier="flex"
            )
            
            # 응답에서 마크다운 추출
            md = self._extract_markdown(resp)
            
            if not md:
                raise RuntimeError("모델이 유효한 마크다운을 반환하지 않았습니다.")
            
            # 원본 마크다운에서 링크 추출 및 보존
            original_links = link_preserver.extract_links(md)
            logger.info(f"원본에서 {len(original_links)}개 링크 발견")
            
            # 중간 결과 로깅 (후처리 전)
            logger.info(f"=== 후처리 전 마크다운 (길이: {len(md)}자) ===")
            logger.debug(f"원본 마크다운:\n{md[:500]}..." if len(md) > 500 else f"원본 마크다운:\n{md}")
            
            # 후처리: SmolAI 전용 PostProcessor 사용 (원본 URL 전달)
            logger.debug("중복 출처 제거 및 헤드라인 추출 시작...")
            cleaned_md, headline = self.postprocessor.process_with_headline(md.strip(), original_source_url=url)
            
            # 링크 검증 및 복구
            processed_links = link_preserver.extract_links(cleaned_md)
            logger.info(f"후처리 후 {len(processed_links)}개 링크 존재")
            
            # 원본 링크와 비교하여 누락된 링크 확인
            validation_result = link_preserver.validate_links(md, cleaned_md)
            if validation_result['missing']:
                logger.warning(f"링크 {len(validation_result['missing'])}개 누락됨, 복구 시도...")
                # TODO: 누락된 링크 복구 로직 구현 필요
            
            # 최종 결과 로깅
            logger.info(f"=== 후처리 후 마크다운 (길이: {len(cleaned_md)}자) ===")
            if headline:
                logger.info(f"=== 추출된 헤드라인: {headline} ===")
            logger.debug(f"정리된 마크다운:\n{cleaned_md[:500]}..." if len(cleaned_md) > 500 else f"정리된 마크다운:\n{cleaned_md}")
            
            # URL에서 날짜 추출 시도
            import re
            date_match = re.search(r'(\d{2})-(\d{2})-(\d{2})', url)
            if date_match:
                date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
            else:
                # 기본값
                from datetime import datetime
                date_str = datetime.now().strftime("%y.%m.%d")
            
            return {
                'markdown': cleaned_md.strip(),
                'headline': headline or "",
                'date': date_str
            }
            
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
