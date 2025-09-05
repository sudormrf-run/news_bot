#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Discord용 간결한 요약 생성 테스트
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI
from src.config import Config
from src.logger import setup_logger, logger

# 프롬프트
DISCORD_SUMMARY_PROMPT = """당신은 AI 뉴스를 Discord용으로 간결하게 요약하는 전문가입니다.

주어진 긴 뉴스 요약을 읽고, Discord 메시지 1개(2000자 이내)로 압축하세요.

형식:
# 🤖 AI News [날짜]

## 🔥 핵심 뉴스 (3-5개)
• **제목**: 한 줄 설명 [링크]
• **제목**: 한 줄 설명 [링크]
...

## 📊 주요 트렌드
• 트렌드 1
• 트렌드 2

---
📖 전체 요약: [GitHub Discussion 링크]

규칙:
1. 가장 중요하고 영향력 있는 뉴스만 선별
2. 각 항목은 1-2줄로 간결하게
3. 기술 용어는 최소화, 이해하기 쉽게
4. 링크는 원본 링크 유지
5. 전체 2000자 이내
6. 이모지로 가독성 향상"""

def create_discord_summary(markdown_content: str, github_url: str = None) -> str:
    """Discord용 간결한 요약 생성"""
    
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    # 날짜 추출 시도
    import re
    date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{2})', markdown_content[:200])
    if date_match:
        date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    else:
        from datetime import datetime
        date_str = datetime.now().strftime("%y.%m.%d")
    
    # GitHub URL이 없으면 예시 URL
    if not github_url:
        github_url = "https://github.com/orgs/sudormrf-run/discussions/[번호]"
    
    user_prompt = f"""다음 AI 뉴스 요약을 Discord용으로 간결하게 요약해주세요.
날짜: {date_str}
GitHub Discussion URL: {github_url}

원본 요약:
{markdown_content}"""
    
    messages = [
        {"role": "system", "content": DISCORD_SUMMARY_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

def main():
    """테스트 실행"""
    setup_logger(level="INFO")
    
    # 원본 파일 읽기
    input_file = "outputs/2025/09/smol_ai_news_20250828.md"
    output_file = "outputs/drafts/discord_summary_20250828.md"
    
    logger.info(f"📄 원본 파일: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    logger.info(f"   원본 크기: {len(content)} 글자")
    
    # Discord 요약 생성
    logger.info("🤖 Discord용 요약 생성 중...")
    
    # 예시 GitHub URL (실제로는 발송 후 받은 URL 사용)
    github_url = "https://github.com/orgs/sudormrf-run/discussions/4"
    
    discord_summary = create_discord_summary(content, github_url)
    
    # 결과 저장
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(discord_summary)
    
    logger.info(f"💾 Discord 요약 저장: {output_file}")
    logger.info(f"   요약 크기: {len(discord_summary)} 글자")
    
    # 화면에도 출력
    print("\n" + "="*60)
    print("📝 생성된 Discord 요약:")
    print("="*60)
    print(discord_summary)
    print("="*60)
    
    return discord_summary

if __name__ == "__main__":
    main()