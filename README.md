# Project APEX

Project APEX는 한국/미국 주식과 ETF를 검색하고, 포트폴리오 비중·리스크·기술적 지표를 함께 확인하는 Streamlit 기반 투자 의사결정 대시보드입니다.

## 현재 버전

- Project APEX v0.9.0 Beta
- Build: Investment Operating System
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

## Sprint 5.2 - Data Freshness + FX Auto Refresh + Product UI Polish

### 데이터 기준 시간

Home 상단과 Sidebar에 다음 기준 시간을 표시합니다.

- 데이터 기준 시간
- 가격 데이터 조회 상태
- 환율 데이터 기준 시간
- KRX Master DB 갱신 날짜
- AI 분석 실행 시간

이 정보는 사용자가 현재 화면의 가격, 환율, 분석 결과가 언제 기준인지 빠르게 확인하기 위한 장치입니다.

### USD/KRW 환율 자동 갱신

Sidebar의 Cash / Currency 영역에서 다음을 사용할 수 있습니다.

- `KRW Cash`: 원화 현금
- `USD Cash`: 달러 현금
- `환율 최신화`: yfinance의 `KRW=X` 또는 `USDKRW=X` 기준으로 USD/KRW 환율 조회
- `USD/KRW`: 수동 환율 입력

자동 환율 조회가 실패하면 앱은 종료되지 않고 기존 입력값을 유지합니다. Streamlit Cloud에서는 네트워크 상황에 따라 환율 조회가 실패할 수 있으므로 수동 입력값을 함께 제공합니다.

### Cloud 배포 주의사항

- Streamlit Cloud 컨테이너는 재시작될 수 있으므로 포트폴리오는 JSON 다운로드/업로드 사용을 권장합니다.
- 외부 시세, 환율, KRX 데이터 조회가 일시적으로 실패하면 기존 캐시 또는 fallback 데이터를 사용합니다.
- 서버에 저장한 `portfolio.json`은 로컬 사용에는 편리하지만 Cloud에서는 영구 보존을 보장하지 않습니다.

## Investment Operating System 구조

### Dashboard Header

- 총자산
- 총투자금
- 총현금
- 현금비중
- 원화 평가금액
- 달러 평가금액
- 총 평가금액(KRW 환산)
- KRW 비중
- USD 비중
- 한국 노출
- 미국 노출
- 추가투자가능금액
- Recommended Cash Ratio

### Market Database

- `modules/market/master_loader.py`: pykrx, 미국 심볼, ETF, 외부 fallback master를 병합합니다.
- `modules/market/ticker_search.py`: 검색 API를 제공합니다.
- `modules/market/external_fallback_loader.py`: pykrx에 늦게 반영되는 신규/특수 KRX 단축코드를 fallback master로 병합합니다.

지원 예시:

- 삼성전자, 삼성전기, 삼성에피스홀딩스, SK하이닉스, SK스퀘어
- TIGER 미국S&P500, KODEX, ACE, SOL 등 한국 ETF
- AAPL, MU, KORU, SOXL, QQQ, SPY 등 미국 주식/ETF

### Portfolio Engine

- `modules/portfolio_engine/asset_models.py`: 표준 Asset 모델
- `modules/portfolio_engine/cash_manager.py`: KRW Cash, USD Cash, USD/KRW 관리
- `modules/portfolio_engine/calculator.py`: 총자산, 현금비중, 통화별 비중, 시장별 비중, 지역 노출 계산

평균단가는 종목 거래통화 기준으로 입력합니다.

- 삼성전자 평균단가 75000 → KRW
- MU 평균단가 120 → USD
- KORU 평균단가 25 → USD
- TIGER 미국S&P500 평균단가 20000 → KRW

## 포트폴리오 저장

- 로컬 저장/불러오기 버튼을 제공합니다.
- Streamlit Cloud에서는 JSON 다운로드/업로드를 권장합니다.
- 잘못된 JSON 파일을 업로드하면 친절한 오류 메시지를 표시하고 앱은 종료되지 않습니다.

## 아직 미구현

- OpenAI API 기반 자연어 분석
- 뉴스 분석
- 백테스트
- 자동매매
- 로그인/사용자별 저장소
