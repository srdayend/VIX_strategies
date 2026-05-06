# Data Sources

This project uses already-collected local Excel files as source data.

## `VIX_futures_term_structure.xlsx`

Primary analysis table.

Sheet: `Term Structure`

Important columns:

- `Trade Date`
- `Available Maturities`
- `Complete 9-Maturity Curve`
- `M1 Sheet`, `M1 Month`, `M1 Settle`
- ... through `M9 Sheet`, `M9 Month`, `M9 Settle`

Best uses:

- Daily term-structure slope analysis
- Contango/backwardation regimes
- Constant-rank futures strategy prototypes
- VIX index regime merge

## `VIX_futures_by_maturity (1).xlsx`

Contract-by-contract futures history.

Sheet: `Trading Periods`

Maturity sheets such as `2004-05 K4`, `2026-06 M6`, etc. have:

- `Trade Date`
- `Open`, `High`, `Low`, `Close`, `Settle`
- `Change`
- `Total Volume`
- `EFP`
- `Open Interest`

Best uses:

- Liquidity and open-interest analysis
- Contract-level validation
- Roll mechanics and maturity lifecycle studies
- More realistic transaction and roll timing assumptions

## `CBOE_VIX_Index_Daily_OHLC.xlsx`

VIX index daily OHLC from Cboe.

Sheet: `VIX_Index_Daily`

Important columns:

- `Date`
- `Open`, `High`, `Low`, `Close`

Best uses:

- Volatility regime filters
- Crisis and spike detection
- Strategy exposure gating
- Term-structure behavior conditional on spot VIX level
