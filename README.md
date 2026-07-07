# Project APEX

Project APEX는 한국/미국 주식과 ETF를 검색하고, 포트폴리오 비중, 리스크, 기술적 지표, 거시 시장 흐름을 함께 확인하는 Streamlit 기반 투자 의사결정 대시보드입니다.

현재 MVP는 모든 기능을 제한 없이 사용할 수 있도록 구성되어 있습니다. 별도 사용 등급 화면은 사용하지 않습니다.

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

## 핵심 기능

- 한국/미국 주식 및 ETF 검색
- 포트폴리오에 추가하지 않고 종목 상세 판단 확인
- KOSPI/NASDAQ 시장 주도주 대시보드
- KRX 전체 종목과 특수 단축코드 검색
- 포트폴리오 저장, 불러오기, JSON 업로드/다운로드
- KRW/USD 통화 분리 및 USD 자산 KRW 환산
- RSI, 이동평균선, MACD, 거래량, 52주 위치 분석
- Decision, Risk, Portfolio AI Summary
- Morning Brief와 Macro Dashboard
- 오늘의 관심 후보 표시

## Sprint 6.4 - Stock Detail Search UX + Market Leaders

### 종목 판단 보기

`종목 판단 보기` 메뉴에서는 종목을 포트폴리오에 추가하지 않아도 다음 항목을 확인할 수 있습니다.

- 종목명, 티커, 시장, 거래통화
- 현재가
- RSI, MACD, 추세, 거래량 상태, 52주 위치
- APEX Score와 판단 신호
- rule-based AI 투자판단 요약
- 선택 종목을 포트폴리오에 추가하는 입력 폼

포트폴리오 추가는 선택 사항입니다. 먼저 종목을 분석하고, 필요할 때 수량과 평균단가를 입력해 보유종목으로 추가할 수 있습니다.

### 시장 주도주

`시장 주도주` 메뉴에서는 다음 그룹을 표시합니다.

- KOSPI 시가총액 Top 10
- KOSPI 거래대금 Top 10
- NASDAQ 시가총액 Top 10
- NASDAQ 거래대금 Top 10

KOSPI 데이터는 pykrx를 우선 사용합니다. 조회 실패 시 앱이 종료되지 않고 fallback 데이터를 표시합니다.

NASDAQ은 무료 데이터 제약이 있어 현재 MVP 대표 대형주 유니버스 기준으로 표시합니다. 전체 NASDAQ 실시간 랭킹이 아니며, 향후 정식 데이터 소스 연동을 위한 자리입니다.

## Sprint 6.6 - Live Data + Theme News Intelligence Foundation

### 최근 조회 기준 데이터 정책

Project APEX는 무료 데이터 소스를 우선 사용합니다.

- 한국 주식: pykrx 우선
- 미국 주식/지수/원자재: yfinance 우선
- USD/KRW: yfinance `KRW=X` 또는 `USDKRW=X`
- 뉴스: 현재는 Demo/Fallback 구조

데이터는 완전한 실시간 시세가 아닙니다. 화면에서는 항상 `최근 조회 기준`, `데이터 기준 시간`, `fallback 여부`를 표시합니다.

### Live Data Layer

`modules/data_providers`는 공통 result object를 반환합니다.

- `LivePriceResult`
- `FxRateResult`
- `MarketIndexResult`

모든 결과에는 `updated_at`, `source`, `success`, `is_fallback`, `error_message`가 포함됩니다. 조회 실패 시 앱은 종료되지 않고 fallback 결과를 반환합니다.

### 테마 레이더

`테마 레이더` 메뉴에서는 테마별 관련 종목의 최근 등락률을 기반으로 강세/약세를 계산합니다.

강도 기준:

- `+1.5% 이상`: 강한 강세
- `+0.3% ~ +1.5%`: 강세
- `-0.3% ~ +0.3%`: 중립
- `-1.5% ~ -0.3%`: 약세
- `-1.5% 이하`: 강한 약세

테마 흐름은 매수 신호가 아니라 시장 흐름 참고자료입니다.

### Theme News

뉴스 계층은 `modules/news`에 준비되어 있습니다. 현재 Sprint에서는 실제 뉴스 API를 필수로 사용하지 않으며, 실패 또는 미연동 시 Demo/Sample 뉴스로 명확히 표시합니다.

뉴스는 사용자 참고자료이며 매수 추천이 아닙니다.

## 기능 제한 정책

현재 MVP에서는 포트폴리오 종목 수 제한이 없습니다.

- 5개 초과 종목 추가 가능
- 10개 이상 종목 추가 가능
- 관심 후보 전체 표시
- 잠금 카드 미사용
- 사용 등급 안내 미사용

관련 설정은 `modules/settings.py`에서 중앙 관리합니다.

기본값:

```python
{
    "max_portfolio_items": None,
    "enable_paid_plan_limit": False,
    "cash_warning_ratio": 20,
    "single_position_warning_ratio": 30,
}
```

`max_portfolio_items`가 `None`이면 포트폴리오 종목 수 제한이 없습니다.
`enable_paid_plan_limit`가 `False`이면 모든 기능을 제한 없이 사용할 수 있습니다.

## Product UI

Project APEX의 Home 화면과 주요 섹션은 금융 SaaS 제품처럼 보이도록 정리되어 있습니다.

- `app/styles/theme.css`: 컬러, 타이포그래피, 카드, 버튼, metric, badge 스타일
- `app/ui/design_system.py`: CSS 로더, 섹션 제목, KPI 카드, 상태 badge helper
- `.streamlit/config.toml`: Streamlit 기본 theme 설정

초보자 모드에서는 오늘 시장 상태, AI 총평, 오늘 해야 할 행동, 관심 후보를 먼저 보여줍니다.
고급자 모드에서는 Macro 지표, RSI, MACD, 52주 위치, 종목별 판단과 리스크 상세를 함께 보여줍니다.

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

- 삼성전자 평균단가 75000 -> KRW
- MU 평균단가 120 -> USD
- KORU 평균단가 25 -> USD
- TIGER 미국S&P500 평균단가 20000 -> KRW

## Data Freshness

Home 상단과 Sidebar에 다음 기준 시간을 표시합니다.

- 앱 버전
- 데이터 기준 시간
- 가격 데이터 갱신 시간
- 환율 데이터 갱신 시간
- Macro 데이터 갱신 시간
- KRX Master DB 갱신 날짜
- AI 분석 실행 시간

## 아직 미구현

- 로그인/회원가입
- 실제 뉴스 API 연동
- Fear & Greed API 연동
- OpenAI API 기반 자연어 분석
- 백테스트
- 자동매매
