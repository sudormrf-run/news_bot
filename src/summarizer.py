# -*- coding: utf-8 -*-
"""
OpenAI API를 사용한 요약 생성 모듈
"""

from typing import Optional, List
from openai import OpenAI

from .config import Config
from .prompts import SYSTEM_PROMPT, DEVELOPER_PROMPT
from .logger import logger, log_execution_time


class Summarizer:
    """AINews 요약 생성 클래스"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Args:
            api_key: OpenAI API 키 (기본값: Config.OPENAI_API_KEY)
            model: 사용할 모델 (기본값: Config.OPENAI_MODEL)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"Summarizer 초기화 완료 (모델: {self.model})")
    
    @log_execution_time
    def generate_markdown(self, issue_url: str, timeframe: Optional[str] = None) -> str:
        """URL에서 요약 생성
        
        Args:
            issue_url: AINews 이슈 URL
            timeframe: 기간 정보 (예: "2025-08-29 ~ 2025-09-01")
        
        Returns:
            마크다운 형식의 요약
        
        Raises:
            RuntimeError: API 호출 실패 시
        """
        logger.info(f"요약 생성 시작: {issue_url}")
        
        # 사용자 프롬프트 구성
        user_text = (
            f"요약 대상 URL: {issue_url}\n"
            "요청: 상기 페이지에서 'AI Twitter Recap', 'AI Reddit Recap', 'AI Discord Recap' "
            "세 섹션만 인용·요약하고, 원문 링크/앵커를 그대로 보존하여 한국어 마크다운으로 출력해 주세요. "
            + (f"기간 힌트: {timeframe}" if timeframe else "")
        )
        
        # API 메시지 구성
        input_messages = [
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
            {"role": "developer", "content": [{"type": "input_text", "text": DEVELOPER_PROMPT}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_text}]},
        ]
        
        try:
            # OpenAI Responses API 호출
            logger.debug("OpenAI API 호출 중...")
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
            
            logger.info(f"요약 생성 완료 (길이: {len(md)}자)")
            return md.strip()
            
        except Exception as e:
            logger.error(f"요약 생성 실패: {str(e)}", exc_info=True)
            raise RuntimeError(f"요약 생성 중 오류 발생: {str(e)}")
    
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
    
    def generate_with_retry(
        self, 
        issue_url: str, 
        timeframe: Optional[str] = None,
        max_retries: int = 3
    ) -> str:
        """재시도 로직이 포함된 요약 생성
        
        Args:
            issue_url: AINews 이슈 URL
            timeframe: 기간 정보
            max_retries: 최대 재시도 횟수
        
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
                
                return self.generate_markdown(issue_url, timeframe)
                
            except Exception as e:
                last_error = e
                logger.warning(f"시도 {attempt + 1} 실패: {str(e)}")
                
                if attempt < max_retries - 1:
                    import time
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"{wait_time}초 대기 후 재시도...")
                    time.sleep(wait_time)
        
        raise RuntimeError(f"모든 재시도 실패: {str(last_error)}")