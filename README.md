# Project APEX

Project APEX is a Streamlit-based investment decision dashboard for Korean and US investors.

## Sprint 5.0 - Investment Operating System Architecture

Dashboard Header:

- 총자산
- 총투자금
- 총현금
- 현금비중
- KRW Cash
- USD Cash
- KRW 비중
- USD 비중
- 한국 노출
- 미국 노출
- 추가투자가능금액
- Recommended Cash Ratio

Market Database:

- `modules/market/market_database.py` owns canonical database access.
- `modules/market/ticker_search.py` owns autocomplete/search API usage.
- `modules/market/master_loader.py` builds caches from pykrx, US sources, and fallback data.

Portfolio Engine:

- `modules/portfolio_engine/asset_models.py` defines the standard Asset model.
- `modules/portfolio_engine/cash_manager.py` separates KRW cash, USD cash, and USD/KRW FX.
- `modules/portfolio_engine/calculator.py` calculates total assets, cash ratio, currency weights, market weights, and region exposure.

Version Management:

- `modules/config/version.py` centralizes app version metadata.
- Sidebar shows Project APEX, Investment Operating System, and version information.

## Sprint 4.0 - Portfolio AI Summary

Project APEX generates a portfolio-level AI-style summary without using any external AI API.

## MVP Sprint 3.9 - Portfolio JSON Download / Upload

For Streamlit Cloud, JSON download/upload is recommended because server-side files may disappear when the container restarts.

## MVP Sprint 3.8 - Portfolio Save & Load

Portfolio controls:

- 포트폴리오 저장: writes the current holdings to JSON.
- 포트폴리오 불러오기: loads the saved JSON into the current session.
- 포트폴리오 초기화: clears the current session portfolio and deletes the saved JSON when possible.

## MVP Sprint 3.7 - KOSPI Full Search + Today Candidate Stocks

Required KOSPI names included in fallback data:

- 삼성전자
- 삼성전기
- SK하이닉스
- SK스퀘어
- 현대차
- NAVER
- 카카오
- POSCO홀딩스
- LG에너지솔루션

Sidebar update:

- `KRX 종목 DB 새로고침` refreshes KOSPI/KOSDAQ/KONEX and ETF cache.

## MVP Sprint 3.5 - Master Search Engine

Updating market data:

- Use the sidebar button `시장 데이터 갱신`.
- If internet refresh fails, the app keeps using the existing cache.

## MVP Sprint 3.4 - Beginner Onboarding UX

First-use workflow:

1. 종목 검색
2. 수량/평균단가 입력
3. 포트폴리오에 추가
4. 오늘의 투자판단 확인

Quick start options:

- `샘플 포트폴리오 불러오기`: loads built-in Korean/US sample holdings.
- `내 포트폴리오 직접 입력하기`: starts from an empty portfolio and uses the search/add flow.

## Portfolio UX

Supported examples:

- Korean stock name: `삼성전자`, `SK하이닉스`, `미래에셋벤처투자`, `넥슨게임즈`
- Korean six-digit ticker: `005930`, `000660`
- Korean ETF name: `TIGER 미국S&P500`
- US ticker: `KORU`, `MU`, `AAPL`, `TSLA`
- US name alias: `마이크론`, `Micron`, `Apple`, `테슬라`, `Broadcom`

## Run

```bash
python -m streamlit run app/main.py
```

## Test

```bash
python -m compileall app modules tests
python -m pytest
```
