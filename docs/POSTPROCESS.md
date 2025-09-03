# 마크다운 후처리 가이드

## 개요
생성된 마크다운 파일에서 중복된 출처 표기를 제거하는 후처리 기능입니다.

## 사용 방법

### 1. 독립 실행 스크립트 사용

#### 기본 사용법
```bash
# 가상환경 활성화
source .venv/bin/activate

# 입력 파일만 지정 (결과는 input_cleaned.md로 저장)
python postprocess_md.py test_summary.md

# 입출력 파일 모두 지정
python postprocess_md.py test_summary.md cleaned_summary.md
```

#### 예시
```bash
# test_summary_high.md를 처리하여 test_summary_high_cleaned.md 생성
python postprocess_md.py test_summary_high.md

# 특정 출력 파일명으로 저장
python postprocess_md.py test_summary_high.md final_summary.md
```

### 2. 전체 파이프라인에서 자동 처리

`main.py`를 실행하면 자동으로 후처리가 수행됩니다:

```bash
python main.py --url "https://news.smol.ai/issues/25-09-02-anthropic-f"
```

파이프라인 처리 과정:
1. 원본 요약 생성 (high reasoning effort)
2. **중간 결과 로깅** (후처리 전 마크다운)
3. 중복 출처 제거 (GPT-5, low reasoning effort)
4. **최종 결과 로깅** (후처리 후 마크다운)
5. 파일 저장 및 배포

### 3. Python 코드에서 직접 사용

```python
from postprocess_md import MarkdownPostProcessor

# 초기화
processor = MarkdownPostProcessor(model="gpt-5")

# 파일 처리
processor.process_file("input.md", "output.md")

# 또는 텍스트 직접 처리
original_md = "..."
cleaned_md = processor.process_markdown(original_md)
```

## 로그 확인

### 로그 레벨
- **INFO**: 처리 단계, 파일 크기, 진행 상황
- **DEBUG**: 마크다운 내용 일부 (처음 500자)
- **ERROR**: 오류 발생 시 상세 정보

### 로그 파일 위치
- 메인 파이프라인: `logs/news_bot_YYYYMMDD.log`
- 독립 스크립트: `logs/postprocess.log`

### 로그 예시
```
2025-09-03 10:00:00 - INFO - === 후처리 전 마크다운 (길이: 5234자) ===
2025-09-03 10:00:00 - DEBUG - 원본 마크다운:
## 오늘의 요약
- Anthropic가 시리즈 F로 130억 달러를 조달...

2025-09-03 10:00:05 - INFO - === 후처리 후 마크다운 (길이: 4521자) ===
2025-09-03 10:00:05 - DEBUG - 정리된 마크다운:
## 오늘의 요약
- Anthropic가 시리즈 F로 130억 달러를 조달...
```

## 처리 규칙

후처리는 다음 규칙을 따릅니다:

1. **중복 링크 제거**
   - 같은 문단/불릿 내 동일 URL은 첫 번째만 유지
   - 연속된 문장의 같은 링크는 첫 번째만 유지

2. **반복 출처 제거**
   - `(news.smol.ai)` 같은 괄호 출처가 매 불릿마다 반복되면 제거
   - 단, 마지막 "출처:" 줄은 항상 유지

3. **내용 보존**
   - 텍스트 내용은 변경하지 않음
   - 링크 텍스트와 URL 매칭 관계 유지
   - 원문 구조와 의미 100% 보존

## 성능 정보

- **모델**: GPT-5
- **Reasoning Effort**: low (단순 정리 작업)
- **처리 시간**: 일반적으로 3-5초
- **텍스트 감소율**: 평균 15-25%

## 문제 해결

### API 키 오류
```bash
export OPENAI_API_KEY="your-api-key"
# 또는 .env 파일에 추가
```

### 타임아웃 오류
`postprocess_md.py`의 timeout 값 조정:
```python
self.client = OpenAI(api_key=self.api_key, timeout=120.0)  # 120초로 증가
```

### 모델 변경
```python
# GPT-4o 사용
processor = MarkdownPostProcessor(model="gpt-4o")

# 또는 o1-preview 사용
processor = MarkdownPostProcessor(model="o1-preview")
```