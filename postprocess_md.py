#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
독립 실행 가능한 마크다운 후처리 스크립트
기존 MD 파일의 중복 출처를 제거합니다.

사용법:
    python postprocess_md.py input.md [output.md]
    
    # 입력 파일만 지정 (결과는 input_cleaned.md로 저장)
    python postprocess_md.py test_summary.md
    
    # 입출력 파일 모두 지정
    python postprocess_md.py test_summary.md cleaned_summary.md
"""

import sys
import os
from pathlib import Path
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.logger import setup_logger

# 로거 설정
logger = setup_logger("postprocess")

# 환경 변수 로드
load_dotenv()


class MarkdownPostProcessor:
    """마크다운 중복 출처 제거 후처리기"""
    
    # 후처리용 프롬프트 (SmolAINewsSummarizer와 동일)
    POSTPROCESS_SYSTEM_PROMPT = """역할: 마크다운 문서 정리 전문가

목표: 입력된 마크다운 텍스트에서 중복된 출처 표기를 제거하고 가독성을 개선

규칙:
1. 각 문단/불릿에서 동일한 출처가 반복되면 한 번만 남기기
2. 연속된 문장에서 같은 링크가 반복되면 첫 번째만 남기기
3. 마지막 "출처:" 부분은 반드시 유지
4. 내용은 변경하지 말고 중복 링크만 제거
5. 원문의 구조와 의미를 100% 보존"""

    POSTPROCESS_DEVELOPER_PROMPT = """작업:
1. 동일한 URL이 한 문단/불릿 내에서 2번 이상 나타나면 첫 번째만 남기고 제거
2. "(news.smol.ai)" 같은 괄호 출처가 각 불릿 끝마다 반복되면 제거
3. 마지막 "출처:" 줄은 그대로 유지
4. 링크 텍스트와 URL의 매칭 관계는 유지
5. 결과는 정리된 마크다운만 출력"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5"):
        """
        Args:
            api_key: OpenAI API 키
            model: 사용할 모델 (기본값: gpt-5)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API 키가 필요합니다. .env 파일 또는 환경변수를 확인하세요.")
        
        self.client = OpenAI(api_key=self.api_key, timeout=6000.0)
        logger.info(f"PostProcessor 초기화 완료 (모델: {self.model})")
    
    def process_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """파일을 읽어서 후처리 수행
        
        Args:
            input_path: 입력 MD 파일 경로
            output_path: 출력 MD 파일 경로 (없으면 input_cleaned.md로 저장)
        
        Returns:
            처리된 마크다운 텍스트
        """
        # 입력 파일 읽기
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_path}")
        
        logger.info(f"입력 파일 읽기: {input_path}")
        with open(input_file, 'r', encoding='utf-8') as f:
            original_md = f.read()
        
        logger.info(f"원본 마크다운 길이: {len(original_md)}자")
        
        # 후처리 수행
        cleaned_md = self.process_markdown(original_md)
        
        # 출력 파일 경로 결정
        if output_path is None:
            output_path = input_file.parent / f"{input_file.stem}_cleaned{input_file.suffix}"
        else:
            output_path = Path(output_path)
        
        # 결과 저장
        logger.info(f"결과 저장: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_md)
        
        logger.info(f"처리 완료! 결과 길이: {len(cleaned_md)}자")
        print(f"✅ 처리 완료!")
        print(f"  - 입력: {input_path} ({len(original_md)}자)")
        print(f"  - 출력: {output_path} ({len(cleaned_md)}자)")
        print(f"  - 감소: {len(original_md) - len(cleaned_md)}자")
        
        return cleaned_md
    
    def process_markdown(self, markdown: str) -> str:
        """마크다운 텍스트의 중복 출처 제거
        
        Args:
            markdown: 원본 마크다운 텍스트
        
        Returns:
            중복 제거된 마크다운 텍스트
        """
        # 메시지 구성
        input_messages = [
            {"role": "system", "content": [{"type": "input_text", "text": self.POSTPROCESS_SYSTEM_PROMPT}]},
            {"role": "developer", "content": [{"type": "input_text", "text": self.POSTPROCESS_DEVELOPER_PROMPT}]},
            {"role": "user", "content": [{"type": "input_text", "text": f"다음 마크다운에서 중복된 출처 표기를 제거해주세요:\n\n{markdown}"}]},
        ]
        
        try:
            logger.info(f"OpenAI API 호출 중... (모델: {self.model}, reasoning: low)")
            
            # GPT-5 사용, reasoning effort는 low
            resp = self.client.responses.create(
                model=self.model,
                input=input_messages,
                reasoning={"effort": "low"},  # 단순 정리 작업이므로 low
            )
            
            # 응답에서 마크다운 추출
            cleaned_md = self._extract_markdown(resp)
            
            if cleaned_md:
                logger.info("중복 출처 제거 완료")
                return cleaned_md
            else:
                logger.warning("후처리 결과가 비어있음, 원본 반환")
                return markdown
                
        except Exception as e:
            logger.error(f"후처리 중 오류 발생: {str(e)}", exc_info=True)
            print(f"❌ 오류 발생: {str(e)}")
            return markdown
    
    def _extract_markdown(self, response) -> str:
        """API 응답에서 마크다운 텍스트 추출"""
        # SDK 버전에 따라 output_text가 없을 수 있으므로 안전 추출
        md = getattr(response, "output_text", None)
        
        if not md:
            chunks = []
            for item in getattr(response, "output", []) or []:
                if getattr(item, "type", "") == "message":
                    for content in getattr(item, "content", []) or []:
                        if getattr(content, "type", "") == "output_text":
                            chunks.append(getattr(content, "text", ""))
            md = "\n".join(chunks).strip()
        
        return md


def main():
    """메인 실행 함수"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        processor = MarkdownPostProcessor()
        processor.process_file(input_path, output_path)
    except Exception as e:
        logger.error(f"처리 실패: {str(e)}", exc_info=True)
        print(f"❌ 처리 실패: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
