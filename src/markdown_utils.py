# -*- coding: utf-8 -*-
"""
마크다운 처리 유틸리티 모듈
"""

import re
from typing import Optional, List, Tuple

from .logger import logger


# 헤더 매칭 정규식
HEADER_RE = re.compile(r"^(#{1,6})\s*(.+?)\s*$", re.MULTILINE)


def extract_section(markdown: str, section_title: str) -> str:
    """마크다운에서 특정 섹션 추출
    
    Args:
        markdown: 마크다운 텍스트
        section_title: 추출할 섹션 제목
    
    Returns:
        추출된 섹션 텍스트 (없으면 빈 문자열)
    """
    lines = markdown.splitlines()
    headers = _find_headers(lines)
    
    # 섹션 찾기
    for idx, (line_idx, level, title) in enumerate(headers):
        if section_title.lower() in title.lower():
            # 다음 동일/상위 레벨 헤더까지의 범위 찾기
            end_idx = len(lines)
            for j in range(idx + 1, len(headers)):
                next_line_idx, next_level, _ = headers[j]
                if next_level <= level:
                    end_idx = next_line_idx
                    break
            
            # 섹션 추출
            section_lines = lines[line_idx:end_idx]
            return "\n".join(section_lines).strip()
    
    return ""


def extract_today_summary(markdown: str) -> str:
    """마크다운에서 '오늘의 요약' 섹션 추출
    
    Args:
        markdown: 마크다운 텍스트
    
    Returns:
        '오늘의 요약' 섹션 텍스트 (없으면 빈 문자열)
    """
    # '오늘'과 '요약'이 모두 포함된 섹션 찾기
    lines = markdown.splitlines()
    headers = _find_headers(lines)
    
    for idx, (line_idx, level, title) in enumerate(headers):
        if "오늘" in title and "요약" in title:
            # 다음 동일/상위 레벨 헤더까지의 범위 찾기
            end_idx = len(lines)
            for j in range(idx + 1, len(headers)):
                next_line_idx, next_level, _ = headers[j]
                if next_level <= level:
                    end_idx = next_line_idx
                    break
            
            # 섹션 추출
            section_lines = lines[line_idx:end_idx]
            return "\n".join(section_lines).strip()
    
    logger.debug("'오늘의 요약' 섹션을 찾을 수 없음")
    return ""


def _find_headers(lines: List[str]) -> List[Tuple[int, int, str]]:
    """마크다운 라인에서 헤더 찾기
    
    Args:
        lines: 마크다운 라인 리스트
    
    Returns:
        (라인 인덱스, 레벨, 제목) 튜플 리스트
    """
    headers = []
    for i, line in enumerate(lines):
        match = HEADER_RE.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headers.append((i, level, title))
    return headers


def save_markdown(file_path: str, content: str) -> None:
    """마크다운 파일 저장
    
    Args:
        file_path: 저장할 파일 경로
        content: 마크다운 내용
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.rstrip() + "\n")
        logger.info(f"마크다운 파일 저장 완료: {file_path}")
    except Exception as e:
        logger.error(f"마크다운 파일 저장 실패: {str(e)}", exc_info=True)
        raise


def read_markdown(file_path: str) -> str:
    """마크다운 파일 읽기
    
    Args:
        file_path: 읽을 파일 경로
    
    Returns:
        파일 내용
    
    Raises:
        FileNotFoundError: 파일이 없는 경우
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.debug(f"마크다운 파일 읽기 완료: {file_path}")
        return content
    except FileNotFoundError:
        logger.error(f"파일을 찾을 수 없음: {file_path}")
        raise
    except Exception as e:
        logger.error(f"마크다운 파일 읽기 실패: {str(e)}", exc_info=True)
        raise


def validate_markdown(content: str) -> bool:
    """마크다운 유효성 검사
    
    Args:
        content: 검사할 마크다운 내용
    
    Returns:
        유효성 여부
    """
    if not content or not content.strip():
        return False
    
    # 최소한 하나의 헤더가 있는지 확인
    has_header = bool(HEADER_RE.search(content))
    
    # 최소 길이 확인 (임의로 100자)
    has_content = len(content.strip()) > 100
    
    return has_header and has_content


def split_by_sections(markdown: str) -> dict[str, str]:
    """마크다운을 섹션별로 분리
    
    Args:
        markdown: 마크다운 텍스트
    
    Returns:
        섹션 제목을 키로 하는 딕셔너리
    """
    lines = markdown.splitlines()
    headers = _find_headers(lines)
    sections = {}
    
    for idx, (line_idx, level, title) in enumerate(headers):
        # 다음 헤더까지의 범위 찾기
        end_idx = len(lines)
        if idx + 1 < len(headers):
            end_idx = headers[idx + 1][0]
        
        # 섹션 내용 추출 (헤더 제외)
        content_lines = lines[line_idx + 1:end_idx]
        content = "\n".join(content_lines).strip()
        
        if content:
            sections[title] = content
    
    return sections


def add_today_summary(markdown: str, summary: str) -> str:
    """마크다운에 '오늘의 요약' 섹션 추가
    
    Args:
        markdown: 원본 마크다운
        summary: 추가할 요약 내용
    
    Returns:
        요약이 추가된 마크다운
    """
    if not summary:
        return markdown
    
    # 이미 '오늘의 요약'이 있는지 확인
    existing = extract_today_summary(markdown)
    if existing:
        logger.warning("'오늘의 요약' 섹션이 이미 존재함")
        return markdown
    
    # 마지막에 추가
    today_section = f"\n\n## 오늘의 요약\n\n{summary}"
    return markdown.rstrip() + today_section