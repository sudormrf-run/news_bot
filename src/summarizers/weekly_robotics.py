# -*- coding: utf-8 -*-
"""
Weekly Robotics Newsletter Summarizer
https://www.weeklyrobotics.com 전용 요약 생성기
"""

from typing import Optional, List, Dict, Any
from openai import OpenAI
import re

from .base import BaseSummarizer, SummarizerResult
from ..config import Config
from ..logger import logger, log_execution_time


class WeeklyRoboticsSummarizer(BaseSummarizer):
    """Weekly Robotics 뉴스레터 전용 Summarizer"""
    
    # Weekly Robotics 전용 프롬프트
    SYSTEM_PROMPT = """역할: 당신은 로보틱스 기술 전문 편집자입니다. Weekly Robotics 뉴스레터를 한국어로 요약합니다.

톤/언어: 한국어, 기술적이고 전문적인 문체. 불필요한 수식어 금지.

핵심 목표:
- Weekly Robotics의 주요 로봇 기술 뉴스와 리소스를 체계적으로 정리
- 원문 링크를 최대한 보존하여 본문에 자연스럽게 포함
- 기술적 용어는 영어 원문과 함께 한국어로 설명
- 각 뉴스 항목의 핵심 기술과 의미를 명확히 전달
- 실용적인 리소스(튜토리얼, 오픈소스 프로젝트 등) 강조
- 가장 주목할 만한 뉴스 1개를 헤드라인으로 선정
"""

    DEVELOPER_PROMPT = """출력 포맷 규칙:
- 최상단에 헤드라인 필수 (내부 추출용): **헤드라인: [가장 주목할 만한 뉴스 제목 - 짧고 임팩트 있게]**
- 썸네일 URL 추출 (내부용): **썸네일: [이미지 URL]** (있는 경우에만)
- 제목 없음 (Weekly Robotics #XXX 형식의 제목 금지!)
- 3개 섹션만: ## 🤖 이번 주 핵심 동향, ## 📰 주요 뉴스, ## 🛠 기술 리소스
- 핵심 동향: 전체 뉴스를 관통하는 트렌드 1-2문장으로 요약 (링크 없음)
- 주요 뉴스: 
  • **[제목]**: 설명 1-2문장. [자세히 보기](원문링크)
  • 가장 중요한 5-7개 뉴스만 선별
  • 각 뉴스당 링크는 "[자세히 보기]" 하나만 포함
  • 설명 내부에 추가 링크 금지
- 기술 리소스:
  • **[리소스명]**: 설명. [링크](url)
  • 3-5개 선별
  • 각 항목당 링크 하나만
- 마지막에 출처 추가: 
  ---
  📖 출처: [Weekly Robotics #이슈번호](원문URL)
- 링크 규칙 (중요!):
  • 각 뉴스/리소스당 링크는 단 1개만
  • "[자세히 보기]" 또는 "[링크]" 형태로 통일
  • 중복된 URL 절대 금지
  • 설명 문장 내부에 링크 포함 금지
- 전체 분량: 2000자 이내
- 이벤트/행사 정보는 제외
- 출력은 순수 마크다운만 (프론트매터, HTML 불가)
- 헤드라인과 썸네일은 내부 추출용이므로 본문 시작은 ## 🤖 부터"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize Weekly Robotics Summarizer
        
        Args:
            api_key: OpenAI API key (default: from Config)
            model: Model name (default: from Config)
        """
        # Config에서 기본값 가져오기
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        
        super().__init__("Weekly Robotics", self.api_key, self.model)
        self.client = OpenAI(api_key=self.api_key)
        
    def validate_config(self) -> bool:
        """설정 유효성 검사
        
        Returns:
            API 키와 모델이 설정되어 있으면 True
        """
        return bool(self.api_key and self.model)
        
    def get_supported_domains(self) -> List[str]:
        """지원하는 도메인 목록"""
        return ['weeklyrobotics.com', 'www.weeklyrobotics.com']
    
    def extract_issue_info(self, content: str, url: str) -> tuple[str, str]:
        """URL과 콘텐츠에서 이슈 번호와 날짜 추출
        
        Args:
            content: 뉴스레터 내용
            url: 뉴스레터 URL
            
        Returns:
            (issue_number, date_str) 튜플
        """
        # URL에서 이슈 번호 추출
        issue_match = re.search(r'weekly-robotics-(\d+)', url)
        issue_number = issue_match.group(1) if issue_match else "Unknown"
        
        # 콘텐츠에서 날짜 추출 시도
        date_patterns = [
            r'(\d{1,2}\s+\w+\s+\d{4})',  # "2 June 2025"
            r'(\d{4}-\d{2}-\d{2})',       # "2025-06-02"
            r'(\d{1,2}/\d{1,2}/\d{4})'    # "6/2/2025"
        ]
        
        date_str = None
        for pattern in date_patterns:
            date_match = re.search(pattern, content[:500])  # 상단 500자에서만 검색
            if date_match:
                date_str = date_match.group(1)
                break
        
        if not date_str:
            from datetime import datetime
            date_str = datetime.now().strftime("%Y.%m.%d")
            
        return issue_number, date_str
    
    @log_execution_time
    def summarize(self, url: str, **kwargs) -> str:
        """Weekly Robotics 뉴스레터 요약 생성
        
        Args:
            url: Weekly Robotics 뉴스레터 URL
            **kwargs: 추가 파라미터
            
        Returns:
            요약된 마크다운 콘텐츠
        """
        try:
            logger.info(f"Weekly Robotics 요약 시작: {url}")
            
            # GPT-5 Responses API 사용 (web_search tool 포함)
            input_messages = [
                {"role": "system", "content": [{"type": "input_text", "text": self.SYSTEM_PROMPT}]},
                {"role": "developer", "content": [{"type": "input_text", "text": self.DEVELOPER_PROMPT}]},
                {"role": "user", "content": [{"type": "input_text", "text": f"다음 Weekly Robotics 뉴스레터를 요약해주세요: {url}"}]},
            ]
            
            completion = self.client.responses.create(
                model=self.model,
                input=input_messages,
                tools=[{"type": "web_search"}],
                reasoning={"effort": "medium"},
                timeout=600  # 10분 timeout
            )
            
            # 응답에서 마크다운 콘텐츠 추출
            logger.debug(f"Completion: {completion}")
            markdown = self._extract_markdown(completion)
            
            # 헤드라인 추출
            headline = self._extract_headline(markdown)
            if headline:
                logger.info(f"추출된 헤드라인: {headline}")
            
            # 썸네일 추출
            thumbnail = self._extract_thumbnail(markdown)
            if thumbnail:
                logger.info(f"추출된 썸네일: {thumbnail}")
            
            # 마크다운에서 헤드라인과 썸네일 라인 제거
            lines = markdown.split('\n')
            filtered_lines = []
            for line in lines:
                if not line.startswith('**헤드라인:') and not line.startswith('**썸네일:'):
                    filtered_lines.append(line)
            markdown = '\n'.join(filtered_lines).strip()
            
            # 썸네일이 있으면 최상단에 추가
            if thumbnail:
                markdown = f"![Weekly Robotics]({thumbnail})\n\n{markdown}"
            
            # 출처 URL이 없으면 추가
            if f"출처: [Weekly Robotics" not in markdown:
                issue_number, date_str = self.extract_issue_info(markdown, url)
                markdown = f"{markdown}\n\n---\n📖 출처: [Weekly Robotics #{issue_number}]({url})"
            
            # 헤드라인과 썸네일 저장 (메타데이터로 활용)
            self._last_headline = headline
            self._last_thumbnail = thumbnail
            
            logger.info("Weekly Robotics 요약 완료")
            return markdown
            
        except Exception as e:
            logger.error(f"Weekly Robotics 요약 실패: {str(e)}", exc_info=True)
            raise
    
    def _extract_markdown(self, response) -> str:
        """Responses API 응답에서 마크다운 콘텐츠 추출 (SmolAI와 동일한 방식)
        
        Args:
            response: OpenAI Responses API 응답
            
        Returns:
            추출된 마크다운 텍스트
        """
        try:
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
            
            if md:
                logger.debug(f"Markdown extracted: {md[:200]}..." if len(md) > 200 else f"Markdown extracted: {md}")
                return md
            
            logger.error("No markdown content found in response")
            return "요약 생성 실패: 응답에서 콘텐츠를 찾을 수 없습니다."
            
        except Exception as e:
            logger.error(f"마크다운 추출 실패: {str(e)}")
            return f"요약 생성 실패: {str(e)}"
    
    def _extract_headline(self, markdown: str) -> Optional[str]:
        """마크다운에서 헤드라인 추출
        
        Args:
            markdown: 요약된 마크다운 텍스트
            
        Returns:
            추출된 헤드라인 또는 None
        """
        lines = markdown.split('\n')
        for line in lines:
            if line.startswith('**헤드라인:'):
                # **헤드라인: 텍스트** 형식에서 추출
                headline = line.replace('**헤드라인:', '').replace('**', '').strip()
                return headline
        return None
    
    def _extract_thumbnail(self, markdown: str) -> Optional[str]:
        """마크다운에서 썸네일 URL 추출
        
        Args:
            markdown: 요약된 마크다운 텍스트
            
        Returns:
            추출된 썸네일 URL 또는 None
        """
        lines = markdown.split('\n')
        for line in lines:
            if line.startswith('**썸네일:'):
                # **썸네일: URL** 형식에서 추출
                thumbnail = line.replace('**썸네일:', '').replace('**', '').strip()
                return thumbnail
        return None
    
    def summarize_with_result(self, url: str, **kwargs) -> SummarizerResult:
        """Weekly Robotics 요약 생성 (메타데이터 포함)
        
        Args:
            url: 뉴스레터 URL
            **kwargs: 추가 파라미터
            
        Returns:
            SummarizerResult 객체
        """
        try:
            # 요약 생성
            markdown = self.summarize(url, **kwargs)
            
            # 메타데이터 추출
            issue_number, date_str = self.extract_issue_info(markdown, url)
            
            # 헤드라인과 썸네일 사용 (저장된 값 또는 기본값)
            headline = getattr(self, '_last_headline', None) or f"Weekly Robotics #{issue_number}"
            thumbnail = getattr(self, '_last_thumbnail', None)
            
            return SummarizerResult(
                summarizer_name=self.name,
                url=url,
                success=True,
                summary=markdown,
                error=None,
                metadata={
                    'headline': headline,
                    'date': date_str,
                    'issue_number': issue_number,
                    'source': 'Weekly Robotics',
                    'url': url,
                    'thumbnail': thumbnail
                }
            )
            
        except Exception as e:
            logger.error(f"Weekly Robotics 요약 실패: {str(e)}")
            raise