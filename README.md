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
- KRX 전체 종목과 특수 단축코드 검색
- 포트폴리오 저장, 불러오기, JSON 업로드/다운로드
- KRW/USD 통화 분리 및 USD 자산 KRW 환산
- RSI, 이동평균선, MACD, 거래량, 52주 위치 분석
- Decision, Risk, Portfolio AI Summary
- Morning Brief와 Macro Dashboard
- 오늘의 관심 후보 표시

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
