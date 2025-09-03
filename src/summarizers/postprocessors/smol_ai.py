# -*- coding: utf-8 -*-
"""
SmolAI News 전용 PostProcessor
중복된 출처 표기를 제거합니다.
"""

from typing import Optional
from ...logger import logger
from .base import BasePostProcessor


class SmolAIPostProcessor(BasePostProcessor):
    """SmolAI News 요약의 중복 출처를 제거하는 PostProcessor"""
    
    # 후처리용 프롬프트
    SYSTEM_PROMPT = """역할: 마크다운 문서 정리 전문가

목표: 입력된 마크다운 텍스트에서 중복된 출처 표기를 제거하고, 정확하지 않은 링크는 보완을 하고 가독성을 개선

규칙:
1. 각 문단/불릿에서 동일한 출처가 반복되면 한 번만 남기기
2. 연속된 문장에서 같은 링크가 반복되면 첫 번째만 남기기
3. 마지막 "출처:" 부분은 반드시 유지
4. 내용은 변경하지 말고 중복 링크만 제거
5. 원문의 구조와 의미를 100% 보존
6. URL 은 하위 링크까지 정확하게 작성
7. 최상단 '오늘의 요약' 섹션이 비어있거나 내용이 없다면 '오늘은 AI 분야에 특별히 주목할 만한 이벤트가 없었습니다'로 명시"""

    DEVELOPER_PROMPT = """작업:
1. 동일한 URL이 한 문단/불릿 내에서 2번 이상 나타나면 첫 번째만 남기고 제거
2. "(news.smol.ai)" 같은 괄호 출처가 각 불릿 끝마다 반복되면 제거
3. 마지막 "출처:" 줄은 그대로 유지
4. 링크 텍스트와 URL의 매칭 관계는 유지
5. 결과는 정리된 마크다운만 출력
6. web_search로 원본 소스를 확인하고, 현재 문서의 URL이 부정확하면 원본의 정확한 URL로 교체
7. 특히 x.com/twitter.com 링크는 트윗 ID까지 포함된 전체 URL로 교체
8. '오늘의 요약' 섹션이 비어있거나 무의미한 경우 위 규칙 7번 적용"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Args:
            api_key: OpenAI API 키
            model: 사용할 모델 (기본값: gpt-5)
        """
        super().__init__("SmolAI PostProcessor", api_key, model or "gpt-5")
    
    def process(self, markdown: str, original_source_url: Optional[str] = None) -> str:
        """SmolAI News 마크다운의 중복 출처 제거
        
        Args:
            markdown: 원본 마크다운 텍스트
            original_source_url: 원본 소스 URL (선택적)
        
        Returns:
            중복 제거된 마크다운 텍스트
        """
        # 메시지 구성
        user_prompt = f"""다음 마크다운에서 중복된 출처 표기를 제거하고, 부정확한 링크는 보완해 주세요:

{markdown}"""
        
        if original_source_url:
            user_prompt += f"\n\n원본 소스 URL: {original_source_url}"
        
        input_messages = [
            {"role": "system", "content": [{"type": "input_text", "text": self.SYSTEM_PROMPT}]},
            {"role": "developer", "content": [{"type": "input_text", "text": self.DEVELOPER_PROMPT}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
        ]
        
        try:
            logger.debug(f"SmolAI 중복 출처 제거 시작 (모델: {self.model}, reasoning: low)")
            if original_source_url:
                logger.debug(f"원본 소스로 URL 검증: {original_source_url}")
            
            # GPT-5 사용, reasoning effort는 low로 설정, web_search 도구 추가
            resp = self.client.responses.create(
                model=self.model,
                input=input_messages,
                tools=[{"type": "web_search"}] if original_source_url else [],
                reasoning={"effort": "low"},  # 단순 정리 작업이므로 low
            )
            
            # 응답에서 마크다운 추출
            cleaned_md = self._extract_markdown(resp)
            
            if cleaned_md:
                logger.debug("SmolAI 중복 출처 제거 완료")
                return cleaned_md
            else:
                logger.warning("후처리 결과가 비어있음, 원본 반환")
                return markdown
                
        except Exception as e:
            logger.warning(f"SmolAI 후처리 중 오류 발생: {str(e)}, 원본 반환")
            return markdown