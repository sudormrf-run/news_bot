# -*- coding: utf-8 -*-
"""
Link Preserver
AI 요약 중 링크가 변경되지 않도록 보호하는 유틸리티
"""

import re
from typing import Dict, List, Tuple
from ..logger import logger


class LinkPreserver:
    """링크를 placeholder로 치환하고 복원하는 클래스"""
    
    def __init__(self):
        """Initialize Link Preserver"""
        self.link_map: Dict[str, str] = {}
        self.placeholder_pattern = r'\[LINK_(\d{4})\]'
        
    def preserve_links(self, content: str) -> Tuple[str, Dict[str, str]]:
        """콘텐츠의 모든 링크를 placeholder로 치환
        
        Args:
            content: 원본 콘텐츠
            
        Returns:
            (처리된 콘텐츠, 링크 매핑 딕셔너리)
        """
        self.link_map = {}
        link_counter = 1
        
        # 마크다운 링크 패턴: [텍스트](URL)
        markdown_link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        
        # 일반 URL 패턴 (http/https로 시작하는 URL)
        url_pattern = r'https?://[^\s\)\]<>"]+'
        
        def replace_markdown_link(match):
            """마크다운 링크를 placeholder로 치환"""
            nonlocal link_counter
            link_text = match.group(1)
            url = match.group(2)
            
            # URL 부분만 placeholder로 치환
            placeholder = f"LINK_{link_counter:04d}"
            self.link_map[placeholder] = url
            link_counter += 1
            
            return f"[{link_text}]([{placeholder}])"
        
        def replace_plain_url(match):
            """일반 URL을 placeholder로 치환"""
            nonlocal link_counter
            url = match.group(0)
            
            # 이미 placeholder인 경우 스킵
            if url.startswith('[LINK_') and url.endswith(']'):
                return url
                
            placeholder = f"LINK_{link_counter:04d}"
            self.link_map[placeholder] = url
            link_counter += 1
            
            return f"[{placeholder}]"
        
        # 1. 먼저 마크다운 링크 처리
        processed = re.sub(markdown_link_pattern, replace_markdown_link, content)
        
        # 2. 남은 일반 URL 처리 (마크다운 링크 내부가 아닌 것만)
        # 마크다운 링크를 임시로 보호
        temp_protected = []
        for match in re.finditer(r'\[([^\]]+)\]\(\[LINK_\d{4}\]\)', processed):
            temp_protected.append(match.group(0))
            
        # 마크다운 링크를 임시 마커로 치환
        for i, protected in enumerate(temp_protected):
            processed = processed.replace(protected, f"<<<PROTECTED_{i}>>>")
            
        # 일반 URL 처리
        processed = re.sub(url_pattern, replace_plain_url, processed)
        
        # 보호된 마크다운 링크 복원
        for i, protected in enumerate(temp_protected):
            processed = processed.replace(f"<<<PROTECTED_{i}>>>", protected)
        
        logger.info(f"링크 보존: {len(self.link_map)}개 링크를 placeholder로 치환")
        
        # 디버그: 몇 개 링크 샘플 출력
        if self.link_map:
            samples = list(self.link_map.items())[:3]
            for placeholder, url in samples:
                logger.debug(f"  {placeholder} → {url[:50]}...")
        
        return processed, self.link_map.copy()
    
    def restore_links(self, content: str, link_map: Dict[str, str] = None) -> str:
        """placeholder를 원본 링크로 복원
        
        Args:
            content: placeholder가 포함된 콘텐츠
            link_map: 링크 매핑 (None이면 self.link_map 사용)
            
        Returns:
            링크가 복원된 콘텐츠
        """
        if link_map is None:
            link_map = self.link_map
            
        if not link_map:
            logger.warning("링크 매핑이 비어있음")
            return content
            
        restored = content
        restore_count = 0
        
        # placeholder를 원본 링크로 복원
        for placeholder, url in link_map.items():
            # [LINK_0001] 형태와 LINK_0001 형태 모두 처리
            patterns = [
                f"\\[{placeholder}\\]",  # [LINK_0001]
                placeholder  # LINK_0001
            ]
            
            for pattern in patterns:
                if re.search(pattern, restored):
                    restored = re.sub(pattern, url, restored)
                    restore_count += 1
                    break
        
        logger.info(f"링크 복원: {restore_count}개 placeholder를 원본 링크로 복원")
        
        # 복원되지 않은 placeholder 확인
        remaining = re.findall(r'\[?LINK_\d{4}\]?', restored)
        if remaining:
            logger.warning(f"복원되지 않은 placeholder: {remaining[:5]}")
            # 복원되지 않은 것들을 빈 문자열로 치환 (또는 원본 유지)
            for placeholder in remaining:
                if placeholder in link_map or placeholder.strip('[]') in link_map:
                    continue
                logger.warning(f"  알 수 없는 placeholder: {placeholder}")
        
        return restored
    
    def extract_links(self, content: str) -> List[str]:
        """콘텐츠에서 모든 링크 추출
        
        Args:
            content: 콘텐츠
            
        Returns:
            링크 URL 리스트
        """
        links = []
        
        # 마크다운 링크에서 URL 추출
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        for _, url in markdown_links:
            if not url.startswith('[LINK_'):  # placeholder가 아닌 경우만
                links.append(url)
        
        # 일반 URL 추출 (마크다운 링크에 포함되지 않은 것)
        plain_urls = re.findall(r'https?://[^\s\)\]<>"]+', content)
        for url in plain_urls:
            if url not in links:  # 중복 제거
                links.append(url)
        
        return links
    
    def validate_links(self, original_content: str, processed_content: str) -> Dict[str, any]:
        """원본과 처리된 콘텐츠의 링크 비교 검증
        
        Args:
            original_content: 원본 콘텐츠
            processed_content: 처리된 콘텐츠
            
        Returns:
            검증 결과 딕셔너리
        """
        original_links = set(self.extract_links(original_content))
        processed_links = set(self.extract_links(processed_content))
        
        missing_links = original_links - processed_links
        added_links = processed_links - original_links
        preserved_links = original_links & processed_links
        
        result = {
            'total_original': len(original_links),
            'total_processed': len(processed_links),
            'preserved': len(preserved_links),
            'missing': list(missing_links),
            'added': list(added_links),
            'success_rate': len(preserved_links) / len(original_links) * 100 if original_links else 100
        }
        
        if missing_links:
            logger.warning(f"누락된 링크 {len(missing_links)}개:")
            for link in list(missing_links)[:5]:
                logger.warning(f"  - {link[:80]}...")
        
        if added_links:
            logger.info(f"추가된 링크 {len(added_links)}개:")
            for link in list(added_links)[:5]:
                logger.info(f"  + {link[:80]}...")
        
        logger.info(f"링크 보존율: {result['success_rate']:.1f}%")
        
        return result