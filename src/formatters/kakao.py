# -*- coding: utf-8 -*-
"""
Kakao Formatter
Discord 마크다운을 카카오톡용 플레인 텍스트로 변환
"""

import re
import requests
from typing import Optional
from ..logger import logger


class KakaoFormatter:
    """카카오톡용 텍스트 포맷터"""
    
    def __init__(self):
        """Initialize Kakao Formatter"""
        self.tinyurl_api = "http://tinyurl.com/api-create.php"
    
    def format(self, markdown_content: str) -> str:
        """마크다운을 카카오톡용 플레인 텍스트로 변환
        
        Args:
            markdown_content: Discord용 마크다운 콘텐츠
            
        Returns:
            카카오톡용 플레인 텍스트
        """
        try:
            # 1. 헤더 제거 및 변환
            text = self._remove_headers(markdown_content)
            
            # 2. 마크다운 링크를 텍스트와 URL로 분리
            text = self._convert_links(text)
            
            # 3. Bold, Italic 등 마크다운 포맷팅 제거
            text = self._remove_markdown_formatting(text)
            
            # 4. 불릿 포인트 정리
            text = self._clean_bullet_points(text)
            
            # 5. 구분선 변환
            text = self._convert_dividers(text)
            
            # 6. 이모지는 유지 (카카오톡 지원)
            
            # 7. 연속된 빈 줄 정리
            text = self._clean_empty_lines(text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"카카오 포맷팅 실패: {str(e)}")
            return markdown_content  # 실패 시 원본 반환
    
    def _remove_headers(self, text: str) -> str:
        """마크다운 헤더 제거
        
        # Title → Title
        ## Subtitle → [Subtitle]
        ### Subsubtitle → - Subsubtitle
        """
        lines = text.split('\n')
        result = []
        
        for line in lines:
            if line.startswith('### '):
                # ### 은 하위 항목으로
                result.append('- ' + line[4:])
            elif line.startswith('## '):
                # ## 은 대괄호로 강조
                result.append('[' + line[3:] + ']')
            elif line.startswith('# '):
                # # 은 그대로 (제목)
                result.append(line[2:])
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _convert_links(self, text: str) -> str:
        """마크다운 링크를 변환하고 TinyURL로 단축
        
        [텍스트](URL) → 텍스트 (단축URL)
        GitHub Discussion 링크는 단축하지 않음
        """
        def replace_link(match):
            link_text = match.group(1)
            url = match.group(2)
            
            # GitHub Discussion 링크는 그대로 유지
            if 'github.com' in url and 'discussions' in url:
                return f"{link_text} ({url})"
            
            # 다른 링크는 TinyURL로 단축
            short_url = self._shorten_url(url)
            return f"{link_text} ({short_url})"
        
        # 마크다운 링크 패턴: [텍스트](URL)
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        return re.sub(pattern, replace_link, text)
    
    def _shorten_url(self, url: str) -> str:
        """TinyURL을 사용해 URL 단축
        
        Args:
            url: 원본 URL
            
        Returns:
            단축된 URL 또는 실패 시 원본 URL
        """
        try:
            # URL이 이미 짧으면 그대로 반환
            if len(url) <= 30:
                return url
            
            # TinyURL API 호출
            response = requests.get(
                self.tinyurl_api,
                params={'url': url},
                timeout=5
            )
            
            if response.status_code == 200:
                short_url = response.text.strip()
                logger.debug(f"URL 단축: {url} → {short_url}")
                return short_url
            else:
                logger.warning(f"TinyURL 실패: {response.status_code}")
                return url
                
        except Exception as e:
            logger.warning(f"URL 단축 중 오류: {str(e)}")
            return url  # 실패 시 원본 반환
    
    def _remove_markdown_formatting(self, text: str) -> str:
        """마크다운 포맷팅 제거
        
        **bold** → bold
        *italic* → italic
        ***bold italic*** → bold italic
        `code` → code
        """
        # Bold italic (***text***)
        text = re.sub(r'\*\*\*([^\*]+)\*\*\*', r'\1', text)
        
        # Bold (**text**)
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        
        # Italic (*text* or _text_)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        text = re.sub(r'\_([^\_]+)\_', r'\1', text)
        
        # Code (`code`)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Strikethrough (~~text~~)
        text = re.sub(r'~~([^~]+)~~', r'\1', text)
        
        return text
    
    def _clean_bullet_points(self, text: str) -> str:
        """불릿 포인트 정리
        
        • → ㆍ (카카오톡에서 더 잘 보임)
        - → ㆍ
        * → ㆍ
        """
        text = text.replace('•', 'ㆍ')
        
        # 줄 시작의 - 또는 * 를 ㆍ로 변경
        lines = text.split('\n')
        result = []
        
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith('- ') or stripped.startswith('* '):
                indent = len(line) - len(stripped)
                result.append(' ' * indent + 'ㆍ' + stripped[1:])
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _convert_dividers(self, text: str) -> str:
        """구분선 변환
        
        --- → ─────────
        """
        lines = text.split('\n')
        result = []
        
        for line in lines:
            if line.strip() == '---':
                result.append('─────────')
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _clean_empty_lines(self, text: str) -> str:
        """연속된 빈 줄을 하나로 정리"""
        # 3개 이상의 연속된 줄바꿈을 2개로 제한
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 앞뒤 공백 제거
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            cleaned.append(line.rstrip())  # 줄 끝 공백만 제거
        
        return '\n'.join(cleaned)


def save_kakao_text(filepath: str, content: str) -> None:
    """카카오톡용 텍스트를 파일로 저장
    
    Args:
        filepath: 저장할 파일 경로 (.txt)
        content: 저장할 텍스트 내용
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"카카오톡 텍스트 저장 완료: {filepath}")
    except Exception as e:
        logger.error(f"카카오톡 텍스트 저장 실패: {str(e)}")
        raise