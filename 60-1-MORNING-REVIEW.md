# v60-1 — Status (updated 2026-05-22, mid-day after AM review)

## What's in 60-1.html now

`60-1.html` is the canonical deliverable. Phase A.1 (engine consolidation) + Phase A.3 Waves 1-4 (Boundless v2.6) all applied and verified. Baseline `50-77.html` untouched.

### Phase A.1 — Engine consolidation (verified byte-identical, all 3 modes)
- Monthly engine loop shortened from 126 → 120 iterations
- `weeklyEngineActive` forced to constant `true`
- Weekly engine extended 520 → **532 weeks** (12-week tail buffer for WC sizing)
- Outputs byte-identical for the 520-week overlap across Modes 1, 3, 4

### Phase A.3 — Boundless v2.6 (Mode 1 only; all waves verified)

**Wave 1:** Constant 3% per-draw transaction fee. Y1/Y2+ split eliminated.

**Wave 2:** $350K arrangement fee at first drawdown, capitalized. Mode 1 amortization horizon **60 months** (was 120) to match the 5-year Boundless term per ASC 470-50.

**Wave 3:**
- **$25K quarterly management fee** (every 13 weeks, expensed via retainedEarnings)
- **M61 bullet** (5-year term end) — corrected from initial M72 assumption per user
- **2.5x MOIC top-up at M61** ≈ $2.28B (formula: `max(0, cumulativeDrawn × 1.5 − cumInterestPaid − cumFeesPaid)`)
- **Third-party warehouse facility funds the M61 top-up** (no cash shock at M61; termLoanBal grows by the top-up amount)
- **Warehouse facility: 7.0% rate, 5-year straight-line amortization** from M62 → M121

**Wave 4:**
- **Phase 1 cap $500M Y1** with $30M/mo cap M1-M3
- **Phase 2 cap $3.0B Y2-Y4**, gated on `boundlessPhase2Approved` (default true)
- **M49-M61 frozen** — no new Boundless draws (bullet window)
- **Tax equity auto-fills the Boundless gap** during Y1-Y4 when smart-draw needs more than the cap allows

### Verified default-scenario milestones (Mode 1)

| Month | cumDebt | cumTaxEquity | termBal | Units | Comment |
|---|---|---|---|---|---|
| M3 last | $90M | $0 | $90M | 373 | Phase 1 M1-M3 cap ($30M/mo) binding ✓ |
| M12 last | $500M | $166M | $500M | 4,905 | Phase 1 cap maxed; tax equity gap-filling ✓ |
| M48 last | $1.9B | $211M | $1.9B | 50,389 | Phase 2 partial use (under-utilized) |
| M61 last | $1.9B | $299M | $4.18B (post-bullet) | 83,108 | M61 bullet fires; $2.28B top-up |
| M120 | $2.5B (all-in) | $299M | $680M | 279,421 | Warehouse amortized down from $4.18B |

## Pending / deferred to future sessions

### Wave 5 — UI label updates (cosmetic)
- "Pledge Backed Loan" labels still appear in ~18 JSX locations
- The engine math is correct; only display strings need updating
- Low-risk, mechanical change

### Phase A.4 — Multi-source draw refactor (next phase)
- Current tax equity gap-fill is a simple "shortfall plug" — adds cash but doesn't model the partnership flip economics (depreciation allocation, ITC sharing, Class A returns)
- Phase A.4 would generalize this to multiple supply sources (Boundless, Pref Equity, Warehouse, Tax Equity Raises) with each source having its own cost-of-capital
- Currently the model treats tax equity as "free cash" — fine for Y1-Y4 financing-gap modeling but understates the long-term cost

### Phase A — Step E (dead-branch cleanup)
- ~40 `weeklyEngineActive ?` ternaries and `if (!weeklyEngineActive)` branches in the engine
- All unreachable now (the constant is `true`), but visually clutters the source
- Cosmetic; doesn't affect runtime

## Remaining judgment calls — your input still needed

### Q5: Management fee P&L treatment (low priority)
- Current: `cash -= $25K; retainedEarnings -= $25K` directly, bypassing P&L line items
- Alternative: dedicated "Boundless Mgmt Fee" line in opex, flowing through EBITDA → NI → RE properly
- Effect on numbers: identical. Only difference is how it presents in income-statement view.
- **Recommend:** keep current implementation for v60-1; add proper P&L line if/when needed for reporting

### Q6: Arrangement fee refundability (trivial)
- Current: modeled as non-refundable, paid at first drawdown
- Term sheet: refundable through 2026-06-15
- Effect on numbers: irrelevant — first drawdown is at week 1 (well before June 2026)
- **Recommend:** keep current implementation; non-refundable is the right base-case assumption

### Q8: Tax equity cost-of-capital
- Current: tax equity is "free" cash inflow (cumulativeTaxEquityRaisedM1 = $299M by program end)
- Reality: tax equity investor gets depreciation + (in some structures) a portion of ITC
- The model's existing `taxEquityMix` mechanism handles vintage-by-vintage flip economics for the underlying deployments. But the *additional* tax equity raised to fill the Boundless gap doesn't get a cost-of-capital line.
- **Recommend (for Phase A.4):** Phase A.4 should add proper tax equity cost-of-capital. For v60-1, the model gives EDGE a free $299M which slightly overstates economics. Acceptable for "Boundless gap-fill in Y1-Y4" framing.

## Implementation file summary

| File | Purpose |
|---|---|
| [60-1.html](Financial%20Model/60-1.html) | **Canonical v60-1 deliverable.** Phase A.1 + A.3 (Waves 1-4) applied and verified. |
| [60-1-engine-only.html](Financial%20Model/60-1-engine-only.html) | Pre-Wave-2 working copy (kept for archeology — Wave 2 onwards diverges from this) |
| [50-77.html](Financial%20Model/50-77.html) | Original baseline, untouched |
| [60-baseline-snapshot-mode{1,3,4}.json](Financial%20Model/) | Pre-Phase-A baselines (520-week) |
| [60-baseline-stepG-mode{1,3,4}.json](Financial%20Model/) | Post-engine-consolidation baselines (532-week) — references for Phase A.3 diffs |
| [60-1-wave{1,2,3,4}-mode{1,3,4}.json](Financial%20Model/) | Intermediate verification snapshots |
| [60-1-warehouse-amort-mode{1,3}.json](Financial%20Model/) | Wave 3 final snapshots before Wave 4 |
| [60-1-M61-mode1.json](Financial%20Model/) | M61 correction snapshot |
| [60-snapshot-diff.py](Financial%20Model/60-snapshot-diff.py) | Diff helper |

## Suggested next steps

1. **Spot-check the M61 bullet flow** in the actual model UI to make sure the milestones above ring true
2. **Discuss Q5, Q6, Q8** in context — these are small but worth aligning on
3. **Wave 5 (UI labels)** — quick cosmetic pass
4. **Phase A.4 (multi-source draw refactor)** — bigger architectural improvement with tax equity cost-of-capital
5. **Phase B (entity P&Ls + income tax for all 5 entities)** — the next major substantive phase
