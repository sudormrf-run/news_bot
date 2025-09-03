## 오늘의 요약
- 집계 범위: 2025‑09‑02 ~ 2025‑09‑03.
- Anthropic가 시리즈 F로 130억 달러를 조달, 포스트머니 1,830억 달러. 주요 수치: 2025‑01 월 약 10억 달러 런레이트 → 2025‑08 월 50억 달러, Claude Code 런레이트 5억 달러, 엔터프라이즈 고객 30만+ 및 연 10만 달러 이상 매출 계정 7배 증가([announcement](https://www.anthropic.com/news/series-f)).
- 밸류에이션·멀티플 해석: 현재 ARR 대비 36.6배, 연말(EoY25) 기준 20배 멀티플 주장([20x EOY25 multiple](https://x.com/swyx/status/1951775849533038969)).

---

## AI Twitter Recap — 한 줄 총평
- 강점은 에이전트·추론 스택의 “실용화” 가속과 비용·신뢰성 최적화, 약점은 툴 사용 평가의 편향과 안전성 관리의 복잡성.

- Mistral Le Chat가 20+ MCP 커넥터와 “Memories”를 추가, Stripe·GitHub·Atlassian·Linear·Notion·Snowflake 등과의 엔터프라이즈형 액션·검색 허브 지향([@MistralAI](https://twitter.com/MistralAI/status/1962881084183527932), [@emilygsands](https://twitter.com/emilygsands/status/1962857931839101296)).
- 에이전트 벤치마크 업데이트: Artificial Analysis Intelligence Index V3가 Terminal‑Bench Hard·τ²‑Bench(통신)를 포함하도록 확장. GPT‑5가 선두, o3 근접 추격; Grok·Claude·Kimi·gpt‑oss 계열이 툴콜/에이전트 과제에서 양호([@ArtificialAnlys](https://twitter.com/ArtificialAnlys/status/1962881314925023355), [follow‑up 1](https://twitter.com/ArtificialAnlys/status/1962882417852987586), [2](https://twitter.com/ArtificialAnlys/status/1962882687010193760)).
- Salesforce의 MCP‑Universe: 실제 MCP 서버(예: Google Maps, GitHub 등) 기반 231개 과제 평가에서 최고 모델 성공률 43.7%, 도메인 특화 성능·“툴 더하기” 역효과 관찰([@_philschmid](https://twitter.com/_philschmid/status/1962935890415599650), [paper/leaderboard](https://twitter.com/_philschmid/status/1962936199345582222)).
- TAU Bench 주의: 무툴 SFT 베이스라인이 아부 성향(sycophancy)으로 Qwen3‑4B를 이기는 사례 제기, 신호 복원 대책 제안([@_lewtun](https://twitter.com/_lewtun/status/1962891555421571316), [follow‑ups](https://twitter.com/_lewtun/status/1962891628688816317)).
- 운영 신뢰성/비용: Galileo 에이전트 평가지표·가드레일(Luna‑2)과 “xpander” 백엔드(메모리·툴·상태·가드레일; 자체 호스팅) 소개([@omarsar0](https://twitter.com/omarsar0/status/1962880974104014948), [@_avichawla](https://twitter.com/_avichawla/status/1962764993587564861), [repo](https://twitter.com/_avichawla/status/1962765005537059007)).
- RL/추론 고성능화: Zhipu/THUDM의 Slime v0.1.0(RL 인프라) 공개·FP8/DeepEP/통합 텐서 오프로드·MoE GSPO 등, PyTorch 대칭 메모리 기반 all‑to‑all 최적화, ZeroGPU AoT로 콜드스타트 단축([@ZhihuFrontier](https://twitter.com/ZhihuFrontier/status/1962751555591086226), [update](https://twitter.com/cloneofsimo/status/1962889777570787723), [ZeroGPU AoT](https://twitter.com/RisingSayak/status/1962844485118996545)).
- 데이터/툴체인 업데이트: Jupyter Agent Dataset(코드 실행 트레이스 포함) 공개([@a_yukh](https://twitter.com/a_yukh/status/1962911097452683710)), LangChain/LangGraph 1.0 알파(중심 에이전트 추상화·표준화된 콘텐츠 블록)([@LangChainAI](https://twitter.com/LangChainAI/status/1962934869065191457)), Qdrant 재검색 랭킹·ChromaSwift on‑device 인덱싱 도입([1](https://twitter.com/qdrant_engine/status/1962876567362617445), [@trychroma](https://twitter.com/trychroma/status/1962917927382122857)), Anthropic API의 코드 실행 프리미티브/컨테이너 수명 30일 확대([@alexalbert__](https://twitter.com/alexalbert__/status/1962912152555225296)).

> 용어 메모 — MCP(모델 컨텍스트 프로토콜): 모델이 외부 도구/데이터 소스에 안전하게 접근하도록 표준화한 커넥터 계층. TAU Bench: 도메인별 툴 사용 능력을 측정하는 에이전트 벤치. 대칭 메모리 all‑to‑all: H100 등에서 통신 경로/경합을 줄여 집단 통신 효율을 높이는 최적화. ZeroGPU AoT: 배포 전 모델을 Ahead‑of‑Time으로 컴파일해 콜드스타트/처리량을 개선. ([news.smol.ai](https://news.smol.ai/issues/25-09-02-anthropic-f))

---

## AI Reddit Recap — 한 줄 총평
- 로컬·오픈 생태계의 실험과 사용자 체감 사례가 풍부했고, 안전성·UX 논쟁이 재점화.

- /r/LocalLlama: 멀티 에이전트 코더가 Stanford TerminalBench에서 Claude Code를 앞지른 36.0% 기록 보고([My weekend project accidentally beat Claude Code - multi-agent coder now #12 on Stanford’s TerminalBench](https://www.reddit.com/r/LocalLLaMA/comments/1n6bihk/my_weekend_project_accidentally_beat_claude_code/), [Stanford/Laude TerminalBench](https://www.tbench.ai/), [Danau5tin/multi-agent-coding-system](https://github.com/Danau5tin/multi-agent-coding-system)).
- /r/LocalLlama: 독일판 “누가 백만장자가 되고 싶은가” 벤치마크 공개, 로컬 양자화 모델 비교 및 프롬프트/파싱 개선 논의([German “Who Wants to Be a Millionaire” Benchmark](https://i.redd.it/fbl0eolgmomf1), [repo](https://github.com/ikiruneo/millionaire-bench)).
- Apertus LLM(ETHZ) 런칭: 40%+ 비영어 데이터·1,811개 언어 지원 주장과 재현 가능한 프리트레인 코퍼스 투명성 약속, 그러나 커뮤니티는 저자원 언어 품질·레포 공개(404) 지연을 지적([New Open LLM from Switzerland “Apertus”, 40%+ training data is non English](https://www.reddit.com/r/MachineLearning/comments/1n6lbaj/new_open_llm_from_switzerland_apertus_40_training/), [press release](https://ethz.ch/en/news-and-events/eth-news/news/2025/09/anthropic-raises-13b-at-183b.html) [원문 앵커 유지], [swiss-ai/pretrain-data](https://github.com/swiss-ai/pretrain-data), [demo](https://chat.publicai.co/)).
- MAESTRO v0.1.5‑alpha: 로컬 LLM 우선의 자율 연구 에이전트 대규모 업데이트(병렬화/워크플로우 개선, 예시 리포트 갤러리)([I just released a big update for my AI research agent, MAESTRO…](https://www.reddit.com/r/LocalLLaMA/comments/1n6lcu9/i_just_released_a_big_update_for_my_ai_research/), [docs](https://murtaza-nasir.github.io/maestro/)).
- Less‑tech: Google “Nano Banana” 명칭이 정식 UI에 노출·빠른 편집 성능 사례 공유, 다만 텍스트 색상 오류 등 아티팩트 지적([Google is now officially calling “Gemini 2.5 Flash image preview”, “Nano Banana”](https://i.redd.it/h0jr0x2qkmmf1), [Nano Banana passed in my benchmark](https://i.redd.it/z49gij8q8mmf1)).
- 안전성·UX: AI 오진 사례와 과도한 자기해 손해 필터 논쟁(헬프라인 자동 연결 등)으로 가드레일 설계의 정밀도·일관성 이슈 부각([Bro asked an AI for a diagnosis instead of a doctor.](https://i.redd.it/l3z7t3f3gomf1), [Stop Redirecting us to helpline just because one person committed suicide.](https://i.redd.it/0e3y7mmzpomf1)).
- 거시담론: Anthropic 초대형 라운드 체감과 Hinton의 AI 공존 낙관론 소개(영상 링크는 접근 제한)([Anthropic has raised $13 billion at a $183 billion post-money valuation](https://i.redd.it/nqwx7yq4wmmf1), [Geoffrey Hinton says he’s more optimistic now…](https://v.redd.it/j61qai9kmsmf1)).

---

## AI Discord Recap — 한 줄 총평
- 모델 드롭·현장 튜닝·툴체인 자잘한 이슈가 다양하게 공유되었고, 일부 상용 서비스의 안정성·정책 변화가 사용자 경험을 좌우.

- Nous Research: Hermes‑4‑14B 오픈 가중치 공개(BF16/FP8), steerability 호평·GGUF 대기([BF16](https://huggingface.co/NousResearch/Hermes-4-14B), [FP8](https://huggingface.co/NousResearch/Hermes-4-14B-FP8)).
- LMArena: ByteDance USO가 픽사 스타일 변환에서 우수 성능 보고, 영상→오디오 생성에는 Kling AI 추천([ByteDance’s USO](https://huggingface.co/ByteDance/USO), [Kling AI](https://kling.ai)).
- LMArena 리더보드: [Gemini 2.5 Pro Experimental](https://ai.google.dev/gemini-api/docs/models/gemini#gemini-2.5-pro-experimental) 5개월 연속 선두 유지로 모델 경쟁 논쟁 재점화.
- Cursor 커뮤니티: 토큰 사용량 폭증 사례(단일 프롬프트 600만 토큰 주장) 논쟁과 관리 팁 공유(파일 분할, [dashboard](https://cursor.com/)).
- GPU MODE: AMD Research의 SHMEM‑유사 RMA 라이브러리 [Iris](https://github.com/ROCm/iris) 공개(멀티‑GPU를 단일 GPU처럼 프로그래밍).
- OpenRouter: DeepSeek 대안으로 Kimi K‑2·GLM‑4.5 활용, 일부 모델·앱 매핑 혼선 제기([a list of free models on OpenRouter](https://openrouter.ai)).
- OpenAI: GPT 응답 정지 사례 다수 보고, 문제 재현용 [chat log](https://chatgpt.com) 공유 및 단순 새로고침 권고.

---

출처: AINews — Anthropic raises $13B at $183B Series F https://news.smol.ai/issues/25-09-02-anthropic-f