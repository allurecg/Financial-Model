# EDGE Financial Model — v60-1

This repository holds the EDGE distributed-solar financial underwriting model, version **v60-1**, restructured to match the Boundless v2.6 term sheet.

## What's in here

| File | Purpose |
|---|---|
| [60-1.html](60-1.html) | The model — a self-contained React SPA (~2.8 MB). Open in a browser. |
| [60-1-OVERNIGHT-LOG.md](60-1-OVERNIGHT-LOG.md) | Detailed work log from the 2026-05-22 → 2026-05-23 build session, including audit/accounting/UX/analysis agent findings and the fixes applied. |
| [60-1-MORNING-REVIEW.md](60-1-MORNING-REVIEW.md) | Morning judgment-call doc summarizing the 7 user-decision points. |
| [60-snapshot-diff.py](60-snapshot-diff.py) | Diff helper for regression testing engine output across versions. Default tolerance 1%. |
| [launch.json.example](launch.json.example) | Example Claude Code launch config — `python3 -m http.server` for local preview. |

## Running the model locally

```bash
# From this directory
python3 -m http.server 3000

# Then open http://localhost:3000/60-1.html in a browser
```

Login credentials are gated — use `bgi` for the Boundless default (Mode 1), `castle` for Castle Pines (Mode 3), `chase` for traditional LTV (Mode 4).

## What v60-1 implements

**Phase A.1 — engine consolidation**
- Monthly loop shortened 126 → 120
- `weeklyEngineActive` forced true
- Weekly engine extended 520 → 532 weeks (12-week tail buffer for WC sizing)
- All 3 financing modes byte-identical to baseline at 1e-9 tolerance

**Phase A.3 — Boundless v2.6 (Mode 1 only)**
- 3% per-draw transaction fee
- $100K arrangement fee at first drawdown ($250K already paid pre-model)
- $25K/qtr management fee (classified as cost of capital)
- 60-mo financing-fee amortization (matches 5-yr term)
- **M60 bullet** sized via NPV solver to deliver **30% XIRR** on actual BGI cash flows
- Top-up paid in cash by EDGE at M60 (per user direction; not equity-classified)
- Warehouse facility @ 7% / 5-yr SL amortization from M61+
- Phase 1: $500M Y1 with M1-M8 $30M/mo + M9-M12 $65M/mo
- Phase 2: $3.0B Y2-Y4 with annual sub-caps (gated on `phase2Approved` toggle)
- Tax equity gap-fill when Boundless capped @ 10% cost of capital (accrued weekly)

**Phase A.3 audit fixes applied**
- Tax equity → `accumulatedCapital` (not retainedEarnings) — preserves ΔRE = ΣNI identity
- Mgmt fee gated to M1-M60 (no post-bullet erroneous BGI fees)
- MOIC top-up uses accrued interest correctly (avoids double-counting at month boundary)
- MOIC top-up doesn't inflate `cumulativeInterestPaidM1` tracker

## Default-scenario verified outcomes (Mode 1)

| Milestone | Value |
|---|---|
| M3 cumulative Boundless drawn | $90M (Phase 1 $30M/mo binding) |
| M12 cumulative Boundless | $402M |
| M60 cumulative Boundless | $1.78B (smart-draw conservative; lender's planned $3.5B not fully utilized) |
| M60 bullet top-up (premium) | $1.54B (cash payment to BGI) |
| M60 cash | $386M |
| M120 cumulative units deployed | 278,430 |
| M120 cash | $6.53B |

## Open items (from agent reviews)

See [60-1-OVERNIGHT-LOG.md](60-1-OVERNIGHT-LOG.md) for full detail. Critical items needing investigation:

1. **§6418 transfer rate** appears at 98.6% net not 85.4% (potential $1.2B economic overstatement) — likely because depreciation monetization commingled with ITC transfer in the same line
2. **Monthly cash goes negative M70-M95** (weekly clean) — aggregation bug
3. **Monthly `actualDebtInterestPaid` = $0** for Mode 1 — interest doesn't propagate to monthly view
4. **Monthly DSCR = None** — covenant gate broken
5. **Weekly tail buffer W521-W532** continues real operations instead of frozen forecast

Plus ASC compliance items deferred for design discussion:
- MOIC top-up classification (loss on extinguishment per ASC 470-50-40-17?)
- Tax equity classification (mezzanine per ASR 268?)
- §163(j) interest limitation modeling for the M60 top-up tax timing

## Phase B (next major work — not yet started)

The original v3 spec called for **5 entity P&Ls + per-entity income tax tracking**:
- EDGE TopCo (C-corp)
- EDGE Master HoldCo (pass-through)
- Project JV (partnership, Form 1065)
- Project SPE (disregarded LLC)
- DSE (C-corp pending confirmation)
- Pref Equity (Eric WY entity, Phase 2 only)

The existing TopCo ASC 740 tax provision (lines 7400-7421) and SPE 2 ecosystem ledger (lines 7423-7438) are the template. Generalizing to 5 entities requires user input on tax characters, transfer pricing, and inter-entity flows.

## Project history

This is v60-1, succeeding v50-77 from the previous numbering scheme. The full v50-1 through v50-77 series captured 6 weeks of evolution and now lives in `/Users/paulchristodoulou/Documents/Claude/Projects/Financial Model/` (not in this repo — too noisy with intermediate files).
