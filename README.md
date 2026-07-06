# Project APEX

Project APEX는 한국/미국 주식과 ETF를 검색하고, 포트폴리오 비중·리스크·기술적 지표·거시 시장 흐름을 함께 확인하는 Streamlit 기반 투자 의사결정 대시보드입니다.

## 현재 버전

- Project APEX v1.0 Beta Prep
- Build: AI Portfolio Expert
- Build Date: 2026-07-07
- Current Plan: FREE

## 실행 방법

```bash
python -m streamlit run app/main.py
```

## 테스트

```bash
python -m compileall app modules tests
python -m pytest
```

## Sprint 6.2 - Free / Pro Tier Architecture + Beginner Watchlist UX

### Free / Pro 구조

이번 Sprint에서는 실제 로그인, 결제, 회원가입을 구현하지 않습니다. 대신 내부 설정값 `APP_TIER`로 기능 제한 구조를 준비했습니다.

- `modules/config/app_tier.py`: 현재 플랜과 feature 사용 가능 여부를 제공합니다.
- `modules/config/feature_flags.py`: FREE / PRO / PREMIUM 기능 제한을 정의합니다.
- `app/ui/pro_gate_view.py`: Pro 잠금 카드와 투자 고지 문구를 렌더링합니다.

현재 기본값은 `FREE`입니다.

### FREE 기능 제한

FREE 플랜:

- Morning Brief 사용 가능
- Macro Dashboard 사용 가능
- 기본 포트폴리오 사용 가능
- 보유종목 최대 5개
- 오늘의 관심 후보 최대 3개
- 기본 리스크 알림 사용 가능
- 고급 포트폴리오 엔진 일부 제한
- 통화/섹터/승인 판단 일부 제한

PRO 플랜 준비 구조:

- 보유종목 무제한
- 관심 후보 전체 표시
- 상세 후보 사유 표시
- 통화별 노출 분석
- 섹터별 중복투자 경고
- 추가매수 승인/보류 판단

PREMIUM은 향후 AI 리포트, 투자이력, 성과분석 확장용으로 구조만 준비했습니다.

### 오늘의 관심 후보 UX

Home 화면의 `오늘의 관심 후보`는 매수 추천이 아닙니다. 관심 후보 또는 매수 검토 후보로 표시하며, 초보자에게 다음 메시지를 함께 보여줍니다.

> 오늘의 관심 후보는 바로 매수하라는 의미가 아닙니다. 시장 상황, 종목 흐름, 포트폴리오 비중을 함께 확인하기 위한 검토 대상입니다.

후보 상태:

- Strong Watch
- Watch
- Wait
- Avoid

FREE에서는 최대 3개 후보만 상세 표시하고, 이후 후보는 Pro Locked Card로 표시합니다.

### 투자 고지 문구

Home 상단과 포트폴리오 입력 전 영역에 투자 고지 문구를 표시합니다.

초보자 모드:

> APEX는 종목을 대신 사라고 지시하지 않습니다. 오늘 살펴볼 만한 후보와 주의할 점을 알려주는 도구입니다.

고급자 모드:

> 본 서비스는 투자 판단을 돕기 위한 정보 제공 도구입니다. 표시되는 관심 후보는 매수 지시가 아니며, 최종 투자 결정과 책임은 사용자 본인에게 있습니다.

## Sprint 6.1 - Macro Data Engine + Market Signal System

`modules/market/macro_provider.py`는 yfinance 기반으로 주요 거시지표를 조회합니다. 실패해도 앱은 종료되지 않고 fallback 데이터를 사용하거나 조회 실패 상태를 표시합니다.

지원 지표:

- KOSPI: `^KS11`
- KOSDAQ: `^KQ11`
- S&P500: `^GSPC`
- NASDAQ: `^IXIC`
- VIX: `^VIX`
- USD/KRW: `KRW=X`
- Gold: `GC=F`
- WTI: `CL=F`

Market Signal:

- `STRONG_RISK` → 리스크 확대
- `RISK` → 주의
- `NEUTRAL` → 관망
- `FAVORABLE` → 우호적
- `STRONG_FAVORABLE` → 강한 우호

## Data Freshness

Home 상단과 Sidebar에 다음 기준 시간을 표시합니다.

- 앱 버전
- 데이터 기준 시간
- 가격 데이터 갱신 시간
- 환율 데이터 갱신 시간
- Macro 데이터 갱신 시간
- KRX Master DB 갱신 날짜
- AI 분석 실행 시간

## Market Database

- `modules/market/master_loader.py`: pykrx, 미국 심볼, ETF, 외부 fallback master를 병합합니다.
- `modules/market/ticker_search.py`: 검색 API를 제공합니다.
- `modules/market/external_fallback_loader.py`: pykrx에 늦게 반영되는 신규/특수 KRX 단축코드를 fallback master로 병합합니다.
- `modules/market/macro_provider.py`: MacroDashboard와 MacroIndicator를 생성합니다.
- `modules/market/macro_signal.py`: APEX Macro Score와 Market Signal을 계산합니다.

지원 예시:

- 삼성전자, 삼성전기, 삼성에피스홀딩스, SK하이닉스, SK스퀘어
- TIGER 미국S&P500, KODEX, ACE, SOL 등 한국 ETF
- AAPL, MU, KORU, SOXL, QQQ, SPY 등 미국 주식/ETF

## Portfolio Engine

평균단가는 종목 거래통화 기준으로 입력합니다.

- 삼성전자 평균단가 75000 → KRW
- MU 평균단가 120 → USD
- KORU 평균단가 25 → USD
- TIGER 미국S&P500 평균단가 20000 → KRW

## 상업화 로드맵

- Free / Pro / Premium 기능 분리
- 로그인과 사용자별 저장소
- 결제 시스템 연동
- AI 리포트
- 투자이력 및 성과분석
- 고급 리스크 승인 엔진

## 아직 미구현

- 실제 결제 기능
- 로그인/회원가입
- 실제 뉴스 API 연동
- Fear & Greed API 연동
- OpenAI API 기반 자연어 분석
- 백테스트
- 자동매매
