# Project APEX

Project APEX is a Streamlit-based investment decision dashboard for Korean and US investors.


## MVP Sprint 3.5 - Master Search Engine

Project APEX now uses a Master Search Engine for one search box across Korean and US markets.

Supported search scope:

- KOSPI, KOSDAQ, KONEX stocks through pykrx when available
- KRX ETFs, including TIGER, KODEX, ACE, KOSEF, SOL, HANARO, RISE, PLUS
- US listed symbols from Nasdaq Trader source when available
- Representative US ETFs such as SPY, QQQ, SOXL, TQQQ, SQQQ, KORU

Search behavior:

- Searches ticker, Korean name, and English name
- Partial match supported
- Case-insensitive
- Space-insensitive
- Returns up to 30 results sorted by score
- Exact name or ticker matches are ranked first

Cache structure:

- `data/market/krx_master.parquet`
- `data/market/krx_etf.parquet`
- `data/market/us_master.parquet`

The app creates the Master Database on first use. Later runs use the local cache so search does not hit the internet every time. If parquet support is unavailable, the app stores a safe local fallback under the same cache path and continues running.

Updating market data:

- Use the sidebar button `?? ??? ??`.
- If internet refresh fails, the app keeps using the existing cache.
- If no cache exists, built-in fallback symbols keep the app usable.

## MVP Sprint 3.4 - Beginner Onboarding UX

Project APEX now opens with a beginner-friendly guide so first-time users can start in about three minutes.

First-use workflow:

1. Search a stock or ETF.
2. Enter quantity and average price.
3. Add it to the portfolio.
4. Check today's investment decision.

Quick start options:

- `?? ????? ????`: loads built-in Korean/US sample holdings.
- `? ????? ?? ????`: starts from an empty portfolio and uses the search/add flow.

Dashboard order on Home:

1. Today's investment decision
2. Today's action card
3. Risk Alert
4. Portfolio Summary
5. Portfolio Table
6. Portfolio input/edit area

Beginner and advanced modes:

- Beginner mode is the default. It shows more explanations and focuses on the main decision.
- Advanced mode keeps raw data expanders and detailed indicators such as RSI, MACD, and 52-week position.

## Score Meanings

- Portfolio Score: average portfolio-level decision quality from current holdings.
- Market Score: technical market condition score from indicators such as RSI, trend, MACD, and volume.
- Risk Score: score after concentration, cash, leverage, and averaging-down risks are considered.
- Final Score: combined score used to map the portfolio to the final decision.

## Decision Meanings

- STRONG_BUY / BUY: technical flow is favorable, but entries should still be split and risk-checked.
- HOLD: holding is reasonable now; avoid adding more if concentration or cash risk is high.
- REDUCE: concentration or risk is elevated; consider reducing part of the position.
- SELL: risk is high; prioritize preventing further loss expansion.

## Portfolio UX

Supported examples:

- Korean stock name: `????`, `SK????`, `????????`, `?????`
- Korean six-digit ticker: `005930`, `000660`
- Korean ETF name: `TIGER ??S&P500`
- US ticker: `KORU`, `MU`, `AAPL`, `TSLA`
- US name alias: `????`, `Micron`, `Apple`

Portfolio state:

- `st.session_state["portfolio_df"]` keeps holdings during the browser session.
- Duplicate tickers are blocked.
- Quantity must be greater than zero.
- Average price can be zero, but cannot be negative.
- The editable table remains for quantity and average-price updates.
- A delete selector removes holdings from the current session portfolio.

## Korean Stock Support

KRX support:

- stock name to ticker
- ticker to stock name
- built-in fallback for core names
- pykrx listing support when available

ETF brands recognized:

- TIGER
- KODEX
- ACE
- KOSEF
- SOL
- RISE
- HANARO
- PLUS

Data source selection:

- US tickers use yfinance
- Korean names/tickers use pykrx first, then yfinance-compatible `.KS` / `.KQ` fallback
- provider failures return safe sample data so the app does not stop

## Troubleshooting

- No search result: check the stock name or enter a ticker directly.
- Price data missing: check the ticker or try again later. The app should continue running with safe fallback data.
- Empty dashboard: add a holding or load the sample portfolio.
- Duplicate ticker warning: the holding already exists; edit quantity or average price in the table instead.
- Negative average price: use zero if you do not know the average price yet.

## Run

```bash
python -m streamlit run app/main.py
```

## Test

```bash
python -m compileall app modules tests
python -m pytest
```

## Requirements

Important packages:

- streamlit
- pandas
- yfinance
- pykrx
- openpyxl
- pytest
