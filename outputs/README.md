# News Bot Outputs

이 디렉토리는 생성된 뉴스 요약 마크다운 파일들을 저장합니다.

## 📁 디렉토리 구조

```
outputs/
├── 2025/               # 연도별 디렉토리
│   ├── 01/            # 월별 디렉토리 (1월)
│   ├── 02/            # 2월
│   ├── ...
│   └── 12/            # 12월
├── archive/           # 오래된 파일 보관
├── drafts/            # 초안 및 테스트 파일
└── README.md          # 이 파일
```

## 📝 파일명 규칙

- **일반 요약**: `recap_YYYYMMDD_HHMMSS.md`
- **SmolAI News**: `smol_ai_news_YYYYMMDD.md`
- **수동 저장**: 사용자가 지정한 파일명

## 🔍 예시

```
outputs/2025/09/smol_ai_news_20250901.md
outputs/2025/09/recap_20250901_143022.md
outputs/drafts/test_summary.md
```

## 📌 참고사항

- 파일은 자동으로 연도/월 디렉토리에 저장됩니다
- `--out` 옵션으로 경로를 직접 지정할 수 있습니다
- drafts 폴더는 테스트용 파일에 사용하세요