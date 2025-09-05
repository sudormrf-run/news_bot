#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""날짜 포맷 테스트"""

import re

# 테스트 URL들
test_urls = [
    "https://news.smol.ai/issues/25-09-01",
    "https://news.smol.ai/issues/25-08-28",
    "https://news.smol.ai/issues/24-12-31",
]

print("날짜 추출 테스트")
print("=" * 40)

for url in test_urls:
    print(f"\nURL: {url}")
    
    # 현재 수정된 코드
    date_match = re.search(r'(\d{2})-(\d{2})-(\d{2})', url)
    if date_match:
        date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
        print(f"  추출된 날짜: {date_str}")
        
        # 타이틀 형식
        title = f"[AI News, {date_str}] 테스트 헤드라인"
        print(f"  생성된 타이틀: {title}")
    else:
        print("  날짜 매칭 실패")

print("\n" + "=" * 40)
print("✅ 테스트 완료")