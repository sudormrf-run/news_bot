# News Bot

확장 가능한 뉴스 요약 생성 및 다중 플랫폼 배포 자동화 시스템

## 주요 기능

- 🤖 다양한 뉴스 소스 지원 (현재: Smol AI News, 확장 가능)
- 🌐 URL 기반 자동 소스 감지
- 📝 한국어 마크다운 형식으로 요약 생성
- 📤 다중 플랫폼 자동 배포:
  - Discord 웹훅
  - GitHub Discussions
  - 카카오톡 봇
- 📊 파일 로깅 및 Discord 에러 알림
- 🔧 모듈화된 구조로 쉬운 확장
- 🎯 Factory 패턴으로 새로운 뉴스 소스 추가 간편

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/news_bot.git
cd news_bot
```

### 2. 가상환경 설정 (권장)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 필요한 API 키와 설정을 입력:

```env
# 필수
OPENAI_API_KEY=your_openai_api_key

# 선택 (사용할 플랫폼만 설정)
DISCORD_WEBHOOK_URL=your_discord_webhook
GITHUB_TOKEN=your_github_token
# ... 기타 설정
```

## 사용법

### 기본 사용

```bash
# URL에서 소스 자동 감지하여 요약 생성
python main.py --url https://news.smol.ai/issues/25-09-01-not-much

# 특정 소스 명시
python main.py --url https://news.smol.ai/issues/25-09-01 \
  --source smol_ai_news

# 기간 정보와 함께 요약
python main.py --url https://news.smol.ai/issues/25-09-01 \
  --timeframe "2025-08-29 ~ 2025-09-01"
```

### Discord로 발송

```bash
python main.py --url https://news.smol.ai/issues/25-09-01 \
  --title "AI News 9월 1일" \
  --send-discord
```

### GitHub Discussions 게시

```bash
python main.py --url https://news.smol.ai/issues/25-09-01 \
  --title "AI News Weekly Recap - September 1" \
  --send-github
```

### 카카오톡 발송

```bash
# '오늘의 요약' 섹션만 발송
python main.py --url https://news.smol.ai/issues/25-09-01 \
  --send-kakao
```

### 모든 채널로 발송

```bash
python main.py --url https://news.smol.ai/issues/25-09-01 \
  --title "AI News 9월 1일" \
  --send-all
```

### 고급 옵션

```bash
# 지원하는 뉴스 소스 확인
python main.py --help  # --source 옵션의 choices 확인

# 디버그 모드 (상세 로그)
python main.py --url https://news.smol.ai/issues/25-09-01 --debug

# 드라이런 (실제 발송 없이 시뮬레이션)
python main.py --url https://news.smol.ai/issues/25-09-01 \
  --send-all --dry-run

# 출력 파일 지정
python main.py --url https://news.smol.ai/issues/25-09-01 \
  --out summaries/2025-09-01.md
```

## 프로젝트 구조

```
news_bot/
├── src/
│   ├── config.py          # 환경변수 관리
│   ├── logger.py          # 로깅 시스템
│   ├── notifier.py        # 에러 알림
│   ├── summarizer.py      # Summarizer Factory
│   ├── markdown_utils.py  # 마크다운 처리
│   ├── summarizers/       # 뉴스 소스별 요약 모듈
│   │   ├── base.py        # BaseSummarizer 클래스
│   │   └── smol_ai_news.py # Smol AI News Summarizer
│   └── publishers/        # 배포 모듈
│       ├── base.py        # BasePublisher 클래스
│       ├── discord.py     # Discord 발송
│       ├── github.py      # GitHub 발송
│       └── kakao.py       # 카카오톡 발송
├── logs/                  # 로그 파일
├── main.py               # CLI 진입점
├── requirements.txt      # 의존성
├── .env.example         # 환경변수 예시
├── ARCHITECTURE.md      # 상세 아키텍처 문서
└── README.md           # 이 파일
```

## 환경변수 상세

### 필수 설정

- `OPENAI_API_KEY`: OpenAI API 키
- `OPENAI_MODEL`: 사용할 모델 (기본: gpt-4o)

### Discord 설정

- `DISCORD_WEBHOOK_URL`: 콘텐츠 발송용 웹훅
- `ERROR_DISCORD_WEBHOOK_URL`: 에러 알림용 웹훅

### GitHub 설정

- `GITHUB_TOKEN`: Personal Access Token (Discussion 권한 필요)
- `GH_REPO`: 저장소 (형식: owner/repo)
- `GH_DISCUSSION_CATEGORY`: Discussion 카테고리명

### 카카오톡 설정

- `KAKAO_BOT_WEBHOOK_URL`: 카카오톡 봇 웹훅 URL

### 로깅 설정

- `LOG_LEVEL`: 로그 레벨 (DEBUG/INFO/WARNING/ERROR)
- `LOG_DIR`: 로그 파일 디렉토리

## 확장 가이드

### 새로운 Summarizer (뉴스 소스) 추가

1. `src/summarizers/` 디렉토리에 새 파일 생성
2. `BaseSummarizer` 클래스 상속
3. 필수 메서드 구현: `summarize()`, `validate_config()`, `get_supported_domains()`
4. `src/summarizer.py`의 `NewsSource` Enum에 추가
5. `SummarizerFactory._summarizers`에 등록

예시 (`src/summarizers/hacker_news.py`):

```python
from .base import BaseSummarizer

class HackerNewsSummarizer(BaseSummarizer):
    def __init__(self, api_key=None, model=None):
        super().__init__("Hacker News", api_key, model)
    
    def summarize(self, url: str, **kwargs) -> str:
        # Hacker News 요약 로직
        pass
    
    def get_supported_domains(self) -> list[str]:
        return ['news.ycombinator.com', 'hackernews.com']
```

### 새로운 Publisher 추가

1. `src/publishers/` 디렉토리에 새 파일 생성
2. `BasePublisher` 클래스 상속
3. `publish()` 및 `validate_config()` 메서드 구현

예시 (`src/publishers/slack.py`):

```python
from .base import BasePublisher

class SlackPublisher(BasePublisher):
    def __init__(self, webhook_url: str):
        super().__init__("Slack")
        self.webhook_url = webhook_url
    
    def publish(self, content: str, **kwargs) -> bool:
        # Slack 발송 로직
        pass
    
    def validate_config(self) -> bool:
        return bool(self.webhook_url)
```

## 문제 해결

### OpenAI API 오류

- API 키가 올바른지 확인
- 사용량 한도 확인
- 네트워크 연결 확인

### Discord 발송 실패

- 웹훅 URL이 유효한지 확인
- 메시지가 2000자를 초과하지 않는지 확인

### GitHub Discussion 게시 실패

- Personal Access Token 권한 확인 (repo, discussion 권한 필요)
- 저장소명과 카테고리명이 정확한지 확인

## 로그 확인

로그는 `logs/` 디렉토리에 날짜별로 저장됩니다:

```bash
tail -f logs/news_bot_20250903.log
```

## 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 연락처

문제가 있거나 제안사항이 있으면 이슈를 등록해 주세요.