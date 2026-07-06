# Project APEX

Project APEX는 한국/미국 주식과 ETF를 검색하고, 포트폴리오 비중·리스크·기술적 지표·거시 시장 흐름을 함께 확인하는 Streamlit 기반 투자 의사결정 대시보드입니다.

## 현재 버전

- Project APEX v1.0 Beta Prep
- Build: AI Portfolio Expert
- Build Date: 2026-07-07

## 실행 방법

```bash
python -m streamlit run app/main.py
```

## 테스트

```bash
python -m compileall app modules tests
python -m pytest
```

## Sprint 6.1 - Macro Data Engine + Market Signal System

### Macro Data Engine

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

각 지표는 다음 정보를 갖습니다.

- 현재값
- 전일 대비 등락폭
- 전일 대비 등락률
- 1개월 차트 데이터
- 6개월 차트 데이터
- 마지막 갱신 시간
- 데이터 소스
- 조회 상태와 실패 메시지

### APEX Macro Score

`modules/market/macro_signal.py`는 rule-based 방식으로 0~100점의 APEX Macro Score를 계산합니다.

긍정 요소:

- S&P500 상승
- NASDAQ 상승
- KOSPI 상승
- KOSDAQ 상승
- VIX 하락
- USD/KRW 안정 또는 하락
- Gold 급등 아님
- WTI 급등 아님

부정 요소:

- VIX 급등
- USD/KRW 급등
- 주요 주가지수 하락
- Gold 급등
- WTI 급등

Market Signal:

- `STRONG_RISK` → 리스크 확대
- `RISK` → 주의
- `NEUTRAL` → 관망
- `FAVORABLE` → 우호적
- `STRONG_FAVORABLE` → 강한 우호

### Home 화면 반영

Home 상단 Morning Brief에 다음을 표시합니다.

- APEX Macro Score
- Market Signal
- 데이터 기준 시간
- 지표별 성공/실패 상태

Macro Market Cards에는 지표명, 현재값, 등락률, 상태 아이콘, 갱신 시간을 표시합니다.

### Chart UI

주요 지표 차트는 1개월 / 6개월을 선택할 수 있습니다.

표시 대상:

- KOSPI
- S&P500
- NASDAQ
- USD/KRW

차트 데이터가 없으면 해당 카드에 `차트 데이터 조회 실패`를 표시하고 앱은 계속 실행됩니다.

### Fear & Greed / News Demo

이번 Sprint에서는 실제 CNN Fear & Greed API와 뉴스 API를 연동하지 않습니다.

- `modules/market/sentiment_provider.py`는 placeholder sentiment 구조만 제공합니다.
- News 영역은 `오늘의 주요 이슈 Demo`로 명확히 표시합니다.
- 샘플 이슈는 실제 뉴스처럼 오해되지 않도록 Demo 문구를 함께 표시합니다.

## Data Freshness

Home 상단과 Sidebar에 다음 기준 시간을 표시합니다.

- 앱 버전
- 데이터 기준 시간
- 가격 데이터 갱신 시간
- 환율 데이터 갱신 시간
- Macro 데이터 갱신 시간
- KRX Master DB 갱신 날짜
- AI 분석 실행 시간

## USD/KRW 환율

Sidebar의 Cash / Currency 영역에서 수동 환율 입력과 자동 환율 최신화를 모두 지원합니다.

- 자동 조회: yfinance `KRW=X`, `USDKRW=X`
- 실패 시 기존 입력값 유지
- 기본 fallback: 1380

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

- `modules/portfolio_engine/asset_models.py`: 표준 Asset 모델
- `modules/portfolio_engine/cash_manager.py`: KRW Cash, USD Cash, USD/KRW 관리
- `modules/portfolio_engine/calculator.py`: 총자산, 현금비중, 통화별 비중, 시장별 비중, 지역 노출 계산

평균단가는 종목 거래통화 기준으로 입력합니다.

- 삼성전자 평균단가 75000 → KRW
- MU 평균단가 120 → USD
- KORU 평균단가 25 → USD
- TIGER 미국S&P500 평균단가 20000 → KRW

## Cloud 배포 주의사항

- Streamlit Cloud 컨테이너는 재시작될 수 있으므로 포트폴리오는 JSON 다운로드/업로드 사용을 권장합니다.
- 외부 시세, 환율, KRX 데이터 조회가 실패하면 기존 캐시 또는 fallback 데이터를 사용합니다.
- 서버에 저장한 `portfolio.json`은 로컬 사용에는 편리하지만 Cloud에서는 영구 보존을 보장하지 않습니다.

## 아직 미구현

- 실제 뉴스 API 연동
- Fear & Greed API 연동
- OpenAI API 기반 자연어 분석
- 백테스트
- 자동매매
- 로그인/사용자별 저장소
