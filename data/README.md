# Data Provenance Manifest

Large binary source files are intentionally not committed through the ChatGPT GitHub connector. Their immutable SHA-256 checksums are recorded here so the thesis data snapshot can be verified.

| File | SHA-256 |
|---|---|
| VIX_futures_term_structure.xlsx | `1cb94036e60e34c01407cd149b9439db45c04572437c408823fb803de3894081` |
| VIX_futures_by_maturity.xlsx | `9bb4a0422dde67613517289a6cd1a7c777cfcede73c64a6f13daa971c610bf21` |
| CBOE_VIX_Index_Daily_OHLC.xlsx | `08326602694abf32a61d33b276d779832fe33e971bd77b2430b8cb39f6401bd1` |
| VIX.zip | `d77566f5c88936686dea8713909873b5b31e75a7ed3be4393339d9377946bdd8` |
| FIXERS evidence ZIP | `69695e930c82de5661465da930bdeafbda165a62d697be57a2ebeb66e38cdaff` |
| FIXERS presentation PPTX | `f31155728b129414849e7bae04ada03d68343c54b9331e4235bc7b7e2c9b986e` |

## Canonicalization rule

The thesis pipeline must read from explicit paths/configuration and must never infer which duplicated workbook is the authoritative copy based on filename alone.

A future data-ingestion step should:
1. verify checksums,
2. copy raw files into a local `data/raw/` directory,
3. produce cleaned / derived files into separate directories,
4. write row-count/date-range/data-quality diagnostics.
