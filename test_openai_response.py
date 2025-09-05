#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenAI 응답 테스트
"""

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model = os.getenv('OPENAI_MODEL', 'gpt-4')

print(f"모델: {model}")

# 간단한 요약 테스트
response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that summarizes robotics news in Korean."
        },
        {
            "role": "user",
            "content": """Weekly Robotics #315의 내용입니다:

Title: Weekly Robotics #315
Issue: 2 June 2025

주요 뉴스:
1. Boston Dynamics Atlas robot perception demo
2. ETH Zurich ANYmal plays badminton
3. Amazon drone crash in Arizona

이것을 한국어로 간단히 요약해주세요."""
        }
    ],
    max_completion_tokens=1000
)

message = response.choices[0].message
print(f"Message type: {type(message)}")
print(f"Content type: {type(message.content)}")
print(f"Content is None: {message.content is None}")
print(f"Content is empty: {message.content == ''}")
print(f"Content: '{message.content}'")