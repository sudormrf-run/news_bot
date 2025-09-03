## 상단 요약 — 2025-09-02 ~ 2025-09-03
- Anthropic가 시리즈 F에서 130억 달러를 조달, 사후가치 1,830억 달러로 확정. 공식 발표에 따르면 2025년 1월 연환산 매출(run‑rate) 약 10억 달러에서 8월에 50억 달러를 돌파했고, Claude Code GA(2025‑05) 이후 최근 3개월간 사용량 10배 이상 증가해 연환산 5억 달러 규모를 형성, 엔터프라이즈 고객 30만 곳 이상과 10만 달러+ 대형 계정 수가 전년 대비 7배 증가했다고 요약됨([announcement](https://www.anthropic.com/news/series-f-183b-post)、[20x EOY25 multiple](https://x.com/omarsar0/status/1831028735197014487)、[in June](https://news.smol.ai/issues/25-06-09-fast/claude-code/) 참조).

---

## AI Twitter Recap — 한 줄 총평
**에이전트(도구 사용·연결성·신뢰성)와 고성능 RL/추론 인프라, 그리고 최신 모델/툴체인이 동시다발적으로 업데이트. 엔터프라이즈 커넥터와 벤치마크/가드레일 논의가 중심.**

- Mistral Le Chat가 MCP 커넥터 20+종과 “Memories”를 추가해 Stripe, GitHub, Atlassian, Linear, Notion, Snowflake(예정) 등과 연동. 엔터프라이즈 권한제어와 지속 메모리로 크로스‑SaaS 액션/검색 허브를 지향([@MistralAI](https://twitter.com/MistralAI/status/1831040271818274860), [@emilygsands](https://twitter.com/emilygsands/status/1831042870609156571)).
- 에이전트 벤치마크 업데이트: Artificial Analysis Intelligence Index V3가 Terminal‑Bench Hard·τ²‑Bench를 추가, GPT‑5가 선두·o3 근접. xAI Grok Code Fast 1/Grok 4와 Claude/Kimi/gpt‑oss 계열이 툴콜/에이전트 작업에서 강세([@ArtificialAnlys](https://twitter.com/ArtificialAnlys/status/1830982228189898990), [follow‑up 1](https://twitter.com/ArtificialAnlys/status/1830982559138830558), [2](https://twitter.com/ArtificialAnlys/status/1830982965038264661)).
- Salesforce MCP‑Universe: 실제 MCP 서버(예: Google Maps, GitHub, Yahoo Finance, Playwright 등) 기반 231개 태스크 평가, 최고 모델 성공률 43.7%. 도메인별 편차 크고 “도구가 많을수록 항상 유리하지 않음”([@_philschmid](https://twitter.com/_philschmid/status/1830995903849396529), [paper/leaderboard](https://twitter.com/salesforce/status/1830999991789127802)).
- TAU Bench 주의점: 무도구 SFT 베이스라인이 아부(sycophancy)로 Qwen3‑4B를 항공사 도메인에서 상회 가능, 툴 사용 신호 복원 제안([@_lewtun](https://twitter.com/_lewtun/status/1831004819280140615), [follow‑ups](https://twitter.com/_lewtun/status/1831005830249152910), [2](https://twitter.com/_lewtun/status/1831006891540519155)).
- 프로덕션 신뢰성: Galileo의 에이전트 평가/가드레일(Luna‑2)과 비용 최적화 초점. 가트너의 “2027년까지 프로젝트 40% 실패” 전망을 배경으로 신뢰성 투자가 강조됨([@omarsar0](https://twitter.com/omarsar0/status/1831012345846726940), [2](https://twitter.com/omarsar0/status/1831013459219450154), [3](https://twitter.com/omarsar0/status/1831014560803668233)). 자체 호스팅 에이전트 백엔드 ‘xpander’도 공유([@_avichawla](https://twitter.com/_avichawla/status/1831021123250583962), [repo](https://twitter.com/_avichawla/status/1831021457269870963)).
- OpenPipe, RL로 딥리서치 에이전트를 학습해 DeepResearch Bench에서 Sonnet‑4를 능가했다고 주장(약 30시간 H200, 비용 약 $350)([@corbtt](https://twitter.com/corbtt/status/1831033107348340958), [follow‑up](https://twitter.com/corbtt/status/1831035120447430943)).

- 고성능 RL·추론 인프라:
  - Zhipu/THUDM의 Slime v0.1.0 공개(GLM‑4.5 백엔드). FP8, DeepEP, MTP(다중 토큰 예측), speculative decoding, CUDA VMM 기반 통합 오프로딩, CPU Adam, Megatron+DeepEP, MoE용 GSPO 등. GLM‑4.5(355B‑A32B) 디코딩 속도 <10 → 60–70 tok/s 사례 보고([@ZhihuFrontier](https://twitter.com/ZhihuFrontier/status/1830959258695745896), [feature checklist](https://twitter.com/ZhihuFrontier/status/1830960157407322584)).
  - PyTorch 대칭 메모리 + 커스텀 all‑to‑all: H100 인트라노드 all2all이 기본 대비 최대 ~1.9× 속도 보고([@cloneofsimo](https://twitter.com/cloneofsimo/status/1830970838294868297), [update](https://twitter.com/cloneofsimo/status/1830972451678345344), [@giffmana](https://twitter.com/giffmana/status/1830975127809417610)).
  - ZeroGPU AoT 컴파일(Hugging Face Spaces): FLUX/Wan에서 콜드스타트 단축·처리량 1.3–1.8× 사례([@RisingSayak](https://twitter.com/RisingSayak/status/1830948428973601161), [1](https://twitter.com/RisingSayak/status/1830949102011482527), [2](https://twitter.com/RisingSayak/status/1830950109460539488); anycoder 연동 [@_akhaliq](https://twitter.com/_akhaliq/status/1830954417429688641), [app](https://twitter.com/_akhaliq/status/1830954888708245960)).
  - 정밀도/효율: NVFP4 4‑bit 학습 ablation 논의([@eliebakouch](https://twitter.com/eliebakouch/status/1830929152444485983), [follow‑up](https://twitter.com/eliebakouch/status/1830930251182655731)); vLLM 기반 INT4 Seed‑OSS “정확도 손실 없음” 사례 보고([@HaihaoShen](https://twitter.com/HaihaoShen/status/1830968767407032667)).
  - 예산 제약 하 라우팅: 컨텍스트 밴딧 관점의 적응형 LLM 라우팅 제안([@omarsar0](https://twitter.com/omarsar0/status/1831027609570302231), [paper](https://twitter.com/omarsar0/status/1831028122460377344)).

- 모델/툴체인·데이터:
  - Microsoft rStar2‑Agent(14B, agentic RL): AIME24 80.6%, AIME25 69.8%로 DeepSeek‑R1(671B) 상회 주장(64× MI300X, 510 RL steps)([@iScienceLuvr](https://twitter.com/iScienceLuvr/status/1831009127500527775), [repo/abs](https://twitter.com/iScienceLuvr/status/1831010023325304998)).
  - Nous Hermes 4(오픈웨이트 reasoning): 70B/405B, 장문 트레이스(최대 16k), 툴‑어웨어 포맷팅 등 학습 레시피 공유([@gm8xx8](https://twitter.com/gm8xx8/status/1831061548679090506)).
  - Tencent Hunyuan‑MT‑7B 및 Chimera(번역, 33개 언어) 데모 공개([@_akhaliq](https://twitter.com/_akhaliq/status/1830955306272401650), [demo](https://twitter.com/_akhaliq/status/1830956210049270052), [@SOSOHAJALAB](https://twitter.com/SOSOHAJALAB/status/1830957741875609915)).
  - 소형 VLM R‑4B(Apache‑2.0) 공개 주장([@mervenoyann](https://twitter.com/mervenoyann/status/1831038741629341888), [model](https://twitter.com/mervenoyann/status/1831039326149474540)).
  - AUSM(자기회귀 비디오 분할)·VibeVoice(장문 TTS) 등 비전/오디오 업데이트([@miran_heo](https://twitter.com/miran_heo/status/1830964832942969077), [@TheTuringPost](https://twitter.com/TheTuringPost/status/1830989867244665183)).
  - Jupyter Agent Dataset(51k Kaggle 노트북·2B 토큰·7TB 데이터, 실행 트레이스 포함) 공개([@a_yukh](https://twitter.com/a_yukh/status/1831017654240917820), [@maximelabonne](https://twitter.com/maximelabonne/status/1831020558742356235)).
  - LangChain/LangGraph 1.0(alpha) 방향성: 에이전트 중심 추상화·표준화된 콘텐츠 블록([@LangChainAI](https://twitter.com/LangChainAI/status/1830987411970900114), [@hwchase17](https://twitter.com/hwchase17/status/1830988763102566730)).
  - Qdrant 재랭킹 기능(신선도/근접/감쇠)·ChromaSwift(iOS 온디바이스 임베딩·영속성)([1](https://twitter.com/qdrant_engine/status/1830991451185129823), [2](https://twitter.com/qdrant_engine/status/1830991896574984387), [@trychroma](https://twitter.com/trychroma/status/1831001223459186981)).

> 용어 메모 — MCP(Model Context Protocol), MTP(다중 토큰 예측), GSPO(모E용 정책 최적화), AoT(사전 컴파일), RLHF(인간 피드백 강화학습)

---

## AI Reddit Recap — 한 줄 총평
**로컬 모델·멀티에이전트 실험과 의료·안전 필터 논쟁, 대형 모델 제품행동 변화에 대한 체감 회귀 보고가 혼재. 증거 수준·지표 부재가 빈번.**

- /r/LocalLlama: 멀티에이전트 코더가 Stanford TerminalBench에서 Sonnet‑4로 36.0%(랭크 #12, Claude Code 상회), Qwen3‑Coder‑480B로 19.25% 달성. 토큰 사용량 Sonnet‑4 93.2M vs Qwen 14.7M([My weekend project…](https://www.reddit.com/r/LocalLLaMA/comments/1n6emk0/my_weekend_project_accidentally_beat_claude_code/), [TerminalBench](https://www.tbench.ai/)).
- Google “Nano Banana” 변주 이미지의 급속 확산과 워터마크·프로버넌스 논의. SynthID 픽셀 워터마크로 검출 가능하다는 주장 제시([Linkedin influencers already pumping nano banana selfies, we’re fucked](https://www.reddit.com/r/ArtificialInteligence/comments/1n6g17n/linkedin_influencers_already_pumping_nano_banana/), [SynthID](https://deepmind.google/science/synthid/)).
- 의료 오남용 사례와 과잉 필터 논쟁:
  - LLM 자기진단으로 말기 식도암 간과 사례 제기(캡처 기반)([Bro asked an AI for a diagnosis…](https://i.redd.it/coyn0rg9qomf1.jpg), [thread](https://www.reddit.com/r/ChatGPT/comments/1n6qz9c/bro_asked_an_ai_for_a_diagnosis_instead_of_a/)).
  - 성경 질문에도 위기 핫라인 자동연결되는 과잉 필터 이슈([Stop Redirecting us to helpline…](https://i.redd.it/9f2hs8u2xpmf1.jpg), [thread](https://www.reddit.com/r/ChatGPT/comments/1n6yt1i/stop_redirecting_us_to_helpline_just_because_one/), [Moderation docs](https://platform.openai.com/docs/guides/moderation)).
- GPT‑5 체감 회귀 보고: 첨부 파일/이미지 자동 인식 저하, 맥락 건너뜀, 라우팅 비결정성 추정. 일부는 GPT‑4o로 회귀 사용([What the hell happened to GPT 5?](https://www.reddit.com/r/ChatGPT/comments/1n6p8kb/what_the_hell_happened_to_gpt_5/), [GPT‑4o](https://platform.openai.com/docs/models#gpt-4o)).
- “GPT‑4o 종료” 밈 반박: 실제로는 모델 존재, 다만 ‘너프’ 체감이라는 커뮤니티 합의([RIP GPT‑4o — Gone but never forgotten](https://i.redd.it/3m0g9n3hcomf1.jpg), [thread](https://www.reddit.com/r/ChatGPT/comments/1n6rj3m/rip_gpt4o_gone_but_never_forgotten/)).
- Anthropic 초대형 라운드와 안전 전망: 6개월 새 가치 약 3배 상승 맥락·버블 우려, Hinton의 “공존 가능성” 발언 영상 화제(접근 제한)([Anthropic has raised $13 billion…](https://i.redd.it/2q1c6xw3gomf1.jpg), [Geoffrey Hinton says he’s more optimistic now…](https://v.redd.it/j61qai9kmsmf1)).

> 용어 메모 — TerminalBench(터미널 상 상호작용 코딩 벤치), SynthID(픽셀 내 워터마크), 라우팅(모델/서브모델 자동 선택)

---

## AI Discord Recap — 한 줄 총평
**오픈웨이트 릴리스와 멀티모달 워크플로, 커널·분산 툴링, 대규모 투자·인수 뉴스가 제작자 관점의 실무 팁과 결합.**

- 오픈모델·로컬: Nous Hermes‑4‑14B가 BF16/FP8 공개, 커뮤니티 GGUF 양자화 예고. 스티어러빌리티(지시 따름성)에서 Qwen3‑14B 대비 호평([BF16](https://huggingface.co/NousResearch/Hermes-4-14B), [FP8](https://huggingface.co/NousResearch/Hermes-4-14B-FP8), [Q5_K_M](https://huggingface.co/modelz-gguf/Nous-Hermes-4-14B-Q5_K_M-GGUF)).
- 멀티모달·스타일: MiniCPM‑V‑4_5의 3D 리샘플링 기반 비디오 토큰화로 RTX 5090에서 100 tps 보고, Qwen2.5‑VL 대비 행동 인식 우위 사례. ByteDance USO 스타일 전환이 프롬프트‑온리 대비 품질 우위([MiniCPM‑V‑4_5](https://huggingface.co/openbmb/MiniCPM-V-4_5), [USO style transfer space](https://huggingface.co/spaces/bytedance/USO), [Kling AI](https://kling.ai)).
- GPU·커널: AMD Research ‘Iris’가 Triton에서 SHMEM‑유사 RMA를 제공, MI300X/MI350X/MI355X 분산 프로그래밍 단순화 기대([ROCm/iris](https://github.com/ROCm/iris), [AMD Developer Challenge](https://amdchallenge2025.datamonsters.com)).
- 벤치마크·리더보드: TAU‑Bench 도입 논의, Livebench는 토큰 집계 부재 지적, LM Arena에서는 Gemini 2.5 Pro Experimental이 5개월째 선두 유지([TAU‑Bench intro](https://x.com/taubench/status/1831019020174688577), [Livebench.ai](https://livebench.ai), [Gemini 2.5 Pro Experimental](https://ai.google.dev/competition/lm_arena)).
- 메가머니 무브: Anthropic 130억 달러 라운드 공식화, OpenAI의 Statsig 인수 소식. 기능 깃발·실험 인프라의 제품 내 내재화 기대([Anthropic raises Series F at USD183B post-money valuation](https://www.anthropic.com/news/series-f-183b-post)、[OpenAI is acquiring Statsig](https://www.statsig.com/blog/openai-is-acquiring-statsig), [OpenAI on X](https://x.com/OpenAI/status/1831069892458700989)).
- 실무 팁: Cursor 배경 에이전트 정체 시 상태전이 요약으로 새 챗으로 넘기는 방법, 과다 토큰 사용 방지 팁(@file 최소화·대시보드 점검·파일 분할 등)([dashboard](https://cursor.com/)).
- 커뮤니티 이슈: Perplexity Comet Mobile 예고, Study Mode 접근 제한, Unlimited LABs 가치 논쟁, 모델 셀렉터 UI 인지 부족([Comet Mobile](https://twitter.com/Perplexity_AI/status/1830896509579835571), [Unlimited LABs worthy](https://www.perplexity.ai/)).

> 용어 메모 — GGUF(로컬 추론용 양자화 포맷), RMA(원격 메모리 접근), Feature flag(런타임 기능 토글)

---

출처: AINews — Anthropic raises $13B at $183B Series F(https://news.smol.ai/issues/25-09-02-anthropic-f)
