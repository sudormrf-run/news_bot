# -*- coding: utf-8 -*-
"""
SmolAI News 전용 PostProcessor
중복된 출처 표기를 제거합니다.
"""

from typing import Optional, Tuple
from ...logger import logger
from .base import BasePostProcessor


class SmolAIPostProcessor(BasePostProcessor):
    """SmolAI News 요약의 중복 출처를 제거하는 PostProcessor"""
    
    # 후처리용 프롬프트
    SYSTEM_PROMPT = """역할: AI 뉴스 큐레이터 및 마크다운 정리 전문가

목표: 
1. 입력된 마크다운 텍스트에서 중복된 출처 표기를 제거하고, 정확하지 않은 링크를 보완
2. 가장 중요하거나 흥미로운 뉴스를 선정하여 헤드라인 생성

규칙:
1. 각 문단/불릿에서 동일한 출처가 반복되면 한 번만 남기기
2. 연속된 문장에서 같은 링크가 반복되면 첫 번째만 남기기
3. 마지막 "출처:" 부분은 반드시 있어야 함.
4. 내용은 변경하지 말고 중복 링크만 제거
5. 원문의 구조와 의미를 100% 보존
6. URL 은 하위 링크까지 정확하게 작성
7. 최상단 '오늘의 요약' 섹션이 비어있거나 내용이 없다면 '오늘은 AI 분야에 특별히 주목할 만한 이벤트가 없었습니다'로 명시

헤드라인 선정 기준:
- 가장 혁신적이거나 영향력 있는 뉴스 우선
- 대중의 관심을 끌 만한 흥미로운 소식 선택
- 간결하고 임팩트 있는 표현 사용
- 15자 이내로 핵심만 전달"""

    DEVELOPER_PROMPT = """작업:
1. 동일한 URL이 한 문단/불릿 내에서 2번 이상 나타나면 첫 번째만 남기고 제거
2. "(news.smol.ai)" 같은 괄호 출처가 각 불릿 끝마다 반복되면 제거
3. 마지막 "출처:" 줄은 반드시 있어야하고, 간결하게 원출처 링크만 표시.
4. 링크 텍스트와 URL의 매칭 관계는 유지
5. web_search로 원본 소스를 확인하고, 현재 문서의 URL이 부정확하면 원본의 정확한 URL로 교체
6. 특히 x.com/twitter.com 링크는 트윗 ID까지 포함된 전체 URL로 교체
7. '오늘의 요약' 섹션이 비어있거나 무의미한 경우, '오늘은 AI 분야에 특별히 주목할 만한 이벤트가 없었습니다'로 명시

출력 형식 (JSON):
{
  "headline": "가장 중요하거나 흥미로운 뉴스의 핵심 (15자 이내)",
  "cleaned_markdown": "정리된 전체 마크다운 문서"
}"""
    
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
        cleaned_md, _ = self.process_with_headline(markdown, original_source_url)
        return cleaned_md
    
    def process_with_headline(self, markdown: str, original_source_url: Optional[str] = None) -> Tuple[str, str]:
        """SmolAI News 마크다운의 중복 출처 제거 및 헤드라인 추출
        
        Args:
            markdown: 원본 마크다운 텍스트
            original_source_url: 원본 소스 URL (선택적)
        
        Returns:
            (중복 제거된 마크다운 텍스트, 헤드라인) 튜플
        """
        # 메시지 구성
        user_prompt = f"""다음 마크다운에서:
1. 중복된 출처 표기를 제거하고, 부정확한 링크를 보완
2. 가장 중요하거나 흥미로운 뉴스를 선정하여 헤드라인 생성 (15자 이내)

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
            
            # 응답에서 JSON 추출
            result = self._extract_json(resp)
            
            if result and isinstance(result, dict):
                cleaned_md = result.get('cleaned_markdown', markdown)
                headline = result.get('headline', '')
                
                if cleaned_md:
                    logger.debug(f"SmolAI 후처리 완료 - 헤드라인: {headline}")
                    return cleaned_md, headline
            
            # JSON 파싱 실패 시 마크다운만 추출 시도
            cleaned_md = self._extract_markdown(resp)
            if cleaned_md:
                logger.debug("SmolAI 중복 출처 제거 완료 (헤드라인 없음)")
                return cleaned_md, ""
            
            logger.warning("후처리 결과가 비어있음, 원본 반환")
            return markdown, ""
                
        except Exception as e:
            logger.warning(f"SmolAI 후처리 중 오류 발생: {str(e)}, 원본 반환")
            return markdown, ""