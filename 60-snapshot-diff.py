"""
Compare a new model snapshot against the 60-baseline-snapshot.json baseline.

Usage:
    python3 60-snapshot-diff.py <new_snapshot.json> [--baseline <file>] [--tol 0.01] [--top 30]

Default baseline: 60-baseline-snapshot-mode1.json (Mode 1 / Boundless / bgi).
Default tolerance: 1% — i.e. abs > 1% AND rel > 1% before reporting.
Use --tol 1e-6 for "must be byte-identical" refactor verification.

Exit code 0 if all fields within tolerance; 1 otherwise.
"""
import json
import sys
import math
from pathlib import Path

HERE = Path(__file__).parent
DEFAULT_BASELINE = HERE / '60-baseline-snapshot-mode1.json'


def cmp_array(name, a, b, tol):
    """Return list of (key, idx, base, new, abs_diff, rel_diff) where field differs.
    Lengths can differ: compares overlap = min(len(a), len(b)); length mismatch reported
    as informational diff (not an error), since v60-1 may extend horizon."""
    diffs = []
    if len(a) != len(b):
        # Informational entry — overlap still gets compared below
        diffs.append((name + '.LENGTH', None, len(a), len(b), abs(len(a) - len(b)), None))
    n = min(len(a), len(b))
    for i in range(n):
        ra, rb = a[i], b[i]
        keys = set(ra.keys()) | set(rb.keys())
        for k in keys:
            va = ra.get(k)
            vb = rb.get(k)
            if va == vb:
                continue
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                if math.isnan(va) and math.isnan(vb):
                    continue
                ad = abs(va - vb)
                rd = ad / max(abs(va), abs(vb), 1e-12)
                if ad > tol and rd > tol:
                    diffs.append((f'{name}.{k}', i, va, vb, ad, rd))
            else:
                diffs.append((f'{name}.{k}', i, va, vb, None, None))
    return diffs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    new_path = Path(sys.argv[1])
    tol = 0.01
    top = 30
    baseline_path = DEFAULT_BASELINE
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--tol':
            tol = float(args[i + 1]); i += 2
        elif a == '--top':
            top = int(args[i + 1]); i += 2
        elif a == '--baseline':
            baseline_path = Path(args[i + 1]); i += 2
        else:
            i += 1
    base = json.loads(baseline_path.read_text())
    new = json.loads(new_path.read_text())

    print(f'baseline: {baseline_path.name} ({base["meta"]["modelVersion"]}, mode {base["meta"]["financingMode"]}, {base["meta"]["capturedAt"]})')
    print(f'new:      {new_path.name} ({new["meta"].get("modelVersion", "?")}, mode {new["meta"].get("financingMode", "?")}, {new["meta"].get("capturedAt", "?")})')
    print(f'tolerance: abs > {tol} AND rel > {tol}')
    print()

    total = 0
    # Length-only diffs (informational) tracked separately
    length_diffs = 0
    for arr in ('weekly', 'monthly', 'reconciled'):
        diffs = cmp_array(arr, base[arr], new[arr], tol)
        length_only = [d for d in diffs if d[0].endswith('.LENGTH')]
        field_diffs = [d for d in diffs if not d[0].endswith('.LENGTH')]
        if length_only:
            d = length_only[0]
            print(f'=== {arr}: length {d[2]} -> {d[3]} (informational; comparing overlap of {min(d[2], d[3])}) ===')
        print(f'=== {arr}: {len(field_diffs)} field diffs in overlap ===')
        by_field = {}
        for d in field_diffs:
            by_field.setdefault(d[0], []).append(d)
        for field, entries in sorted(by_field.items(), key=lambda x: -len(x[1]))[:top]:
            sample = entries[0]
            max_rel = max((e[5] for e in entries if e[5] is not None), default=0)
            max_abs = max((e[4] for e in entries if e[4] is not None), default=0)
            print(f'  {field:<50} hits={len(entries):4} max_abs={max_abs:.3g} max_rel={max_rel:.3g}  idx{sample[1]}: {sample[2]!r} -> {sample[3]!r}')
        total += len(field_diffs)
        length_diffs += len(length_only)
        print()

    print(f'TOTAL FIELD DIFFS: {total}  (length-only diffs ignored: {length_diffs})')
    sys.exit(0 if total == 0 else 1)


if __name__ == '__main__':
    main()
