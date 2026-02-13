# baf_report.py
from __future__ import annotations

import os
import math
import numpy as np
import pandas as pd


# -----------------------------
# Config
# -----------------------------
CSV_PATH = "dataset\Base.csv"
OUT_DIR = "report"

TARGET = "fraud_bool"
TIME_COL = "month"  # exists in Base.csv
ID_COL = "device_id"  # example, not required

# Categorical candidates (adjust if your schema differs)
CAT_COLS = [
    "payment_type",
    "housing_status",
    "employment_status",
    "source",
    "device_os",
]

# Numeric candidates (adjust if your schema differs)
NUM_COLS = [
    "customer_age",
    "income",
    "name_email_similarity",
    "credit_risk_score",
    "proposed_credit_limit",
    "keep_alive_session",
    "prev_address_months_count",
    "current_address_months_count",
    "velocity_6h",
    "velocity_24h",
    "velocity_4w",
    "date_of_birth_distinct_emails_4w",
    "device_distinct_emails_8w",
]

# Columns where -1 likely means "unknown" (common in this dataset)
NEG1_AS_UNKNOWN = [
    "prev_address_months_count",
    "current_address_months_count",
]

# Some columns might be constant and can be dropped
POSSIBLE_CONSTANTS = ["device_fraud_count"]  # often all zeros in Base.csv


# -----------------------------
# Helpers
# -----------------------------
def ensure_outdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def safe_rate(num: float, den: float) -> float:
    return float(num) / float(den) if den else 0.0

def lift(rate: float, base_rate: float) -> float:
    return (rate / base_rate) if base_rate > 0 else np.nan

def describe_missing(df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    miss = df.isna().sum()
    out = pd.DataFrame({
        "missing_count": miss,
        "missing_rate": (miss / n).astype(float),
        "dtype": df.dtypes.astype(str),
        "nunique": df.nunique(dropna=True),
    }).sort_values(["missing_rate", "nunique"], ascending=[False, True])
    return out

def segment_table(
    df: pd.DataFrame,
    col: str,
    target: str,
    base_rate: float,
    min_count: int = 500,
    top_n: int = 25,
) -> pd.DataFrame:
    g = df.groupby(col, dropna=False)[target].agg(["count", "sum", "mean"]).rename(
        columns={"sum": "fraud_count", "mean": "fraud_rate"}
    )
    g["lift"] = g["fraud_rate"].apply(lambda r: lift(r, base_rate))
    g["nonfraud_count"] = g["count"] - g["fraud_count"]
    # filter small groups
    g = g[g["count"] >= min_count].copy()
    g = g.sort_values(["lift", "fraud_rate", "fraud_count"], ascending=False).head(top_n)
    g.insert(0, "feature", col)
    g = g.reset_index().rename(columns={col: "value"})
    return g

def numeric_effects(
    df: pd.DataFrame,
    col: str,
    target: str,
) -> dict:
    # robust effect size proxy: difference in medians + Cohen's d (approx)
    x = df[col]
    y = df[target].astype(int)

    x0 = x[y == 0].dropna()
    x1 = x[y == 1].dropna()

    if len(x0) < 100 or len(x1) < 50:
        return {}

    med0, med1 = float(x0.median()), float(x1.median())
    mean0, mean1 = float(x0.mean()), float(x1.mean())
    std0, std1 = float(x0.std(ddof=1)), float(x1.std(ddof=1))
    # pooled std
    pooled = math.sqrt(((len(x0)-1)*std0*std0 + (len(x1)-1)*std1*std1) / (len(x0)+len(x1)-2)) if (len(x0)+len(x1)-2) > 0 else np.nan
    cohend = (mean1 - mean0) / pooled if pooled and pooled > 0 else np.nan

    # quantiles by class (gives intuition)
    qs = [0.05, 0.25, 0.50, 0.75, 0.95]
    q0 = x0.quantile(qs).to_dict()
    q1 = x1.quantile(qs).to_dict()

    return {
        "feature": col,
        "n0": int(len(x0)),
        "n1": int(len(x1)),
        "median_nonfraud": med0,
        "median_fraud": med1,
        "median_diff": med1 - med0,
        "mean_nonfraud": mean0,
        "mean_fraud": mean1,
        "cohen_d": cohend,
        **{f"q{int(k*100):02d}_nonfraud": float(v) for k, v in q0.items()},
        **{f"q{int(k*100):02d}_fraud": float(v) for k, v in q1.items()},
    }

def binned_lift_table(
    df: pd.DataFrame,
    col: str,
    target: str,
    base_rate: float,
    bins: int = 10,
) -> pd.DataFrame:
    # Quantile bins on non-missing; keep missing as its own bucket
    s = df[col]
    mask = s.notna()
    if mask.sum() < 1000:
        return pd.DataFrame()

    try:
        qbin = pd.qcut(s[mask], q=bins, duplicates="drop")
    except ValueError:
        return pd.DataFrame()

    tmp = df.loc[mask, [target]].copy()
    tmp["bin"] = qbin.astype(str)
    agg = tmp.groupby("bin")[target].agg(["count", "sum", "mean"]).rename(
        columns={"sum": "fraud_count", "mean": "fraud_rate"}
    )
    agg["lift"] = agg["fraud_rate"].apply(lambda r: lift(r, base_rate))
    agg.insert(0, "feature", col)
    agg = agg.reset_index()

    # Missing bucket
    miss = df.loc[~mask, target]
    if len(miss) > 0:
        miss_row = {
            "feature": col,
            "bin": "MISSING",
            "count": int(len(miss)),
            "fraud_count": int(miss.sum()),
            "fraud_rate": safe_rate(int(miss.sum()), int(len(miss))),
            "lift": lift(safe_rate(int(miss.sum()), int(len(miss))), base_rate),
        }
        agg = pd.concat([agg, pd.DataFrame([miss_row])], ignore_index=True)

    return agg.sort_values(["lift", "fraud_rate"], ascending=False)

def rule_candidates_from_top_segments(
    seg_df: pd.DataFrame,
    min_lift: float = 2.0,
    max_rules: int = 30,
) -> list[tuple[str, str]]:
    """
    Create simple rule strings like: (feature == value)
    from top segments with high lift.
    """
    rules = []
    for _, r in seg_df.iterrows():
        if pd.isna(r["lift"]) or r["lift"] < min_lift:
            continue
        feat = r["feature"]
        val = r["value"]
        if pd.isna(val):
            rule = f"{feat}.isna()"
        else:
            # pandas-safe equality
            rule = f"({feat} == {repr(val)})"
        rules.append((feat, rule))
        if len(rules) >= max_rules:
            break
    return rules

def eval_rules(df: pd.DataFrame, rules: list[tuple[str, str]], target: str, base_rate: float) -> pd.DataFrame:
    rows = []
    for feat, expr in rules:
        try:
            mask = df.eval(expr) if "isna" not in expr else df[feat].isna()
        except Exception:
            continue

        n = int(mask.sum())
        if n < 500:
            continue
        fraud = int(df.loc[mask, target].sum())
        rate = safe_rate(fraud, n)
        rows.append({
            "rule": expr,
            "count": n,
            "fraud_count": fraud,
            "fraud_rate": rate,
            "lift": lift(rate, base_rate),
        })
    out = pd.DataFrame(rows).sort_values(["lift", "fraud_count", "count"], ascending=False)
    return out


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    ensure_outdir(OUT_DIR)

    # Read with minimal assumptions
    df = pd.read_csv(CSV_PATH)

    # Basic sanity
    if TARGET not in df.columns:
        raise ValueError(f"Target column '{TARGET}' not found. Columns: {list(df.columns)[:10]} ...")

    # Drop constant columns if truly constant
    for c in POSSIBLE_CONSTANTS:
        if c in df.columns and df[c].nunique(dropna=False) <= 1:
            df = df.drop(columns=[c])

    # Convert target to int 0/1 if needed
    df[TARGET] = df[TARGET].astype(int)

    # Treat -1 as unknown for selected columns: add flags + set to NaN
    for c in NEG1_AS_UNKNOWN:
        if c in df.columns:
            df[c + "_unknown"] = (df[c] == -1).astype(int)
            df.loc[df[c] == -1, c] = np.nan

    # Base rate
    n = len(df)
    fraud_n = int(df[TARGET].sum())
    base_rate = safe_rate(fraud_n, n)

    # ---- Summary
    summary = pd.DataFrame([{
        "rows": n,
        "fraud_count": fraud_n,
        "fraud_rate": base_rate,
        "n_features": df.shape[1],
    }])
    summary.to_csv(os.path.join(OUT_DIR, "00_summary.csv"), index=False)

    # ---- Missingness
    miss = describe_missing(df)
    miss.to_csv(os.path.join(OUT_DIR, "01_missingness.csv"))

    # ---- Drift by month (if present)
    if TIME_COL in df.columns:
        drift = df.groupby(TIME_COL)[TARGET].agg(["count", "sum", "mean"]).rename(
            columns={"sum": "fraud_count", "mean": "fraud_rate"}
        )
        drift["lift_vs_overall"] = drift["fraud_rate"].apply(lambda r: lift(r, base_rate))
        drift = drift.reset_index().sort_values(TIME_COL)
        drift.to_csv(os.path.join(OUT_DIR, "02_drift_by_month.csv"), index=False)

    # ---- Segment risk tables
    seg_tables = []
    for c in CAT_COLS:
        if c in df.columns:
            seg_tables.append(segment_table(df, c, TARGET, base_rate, min_count=500, top_n=50))
    if seg_tables:
        seg_all = pd.concat(seg_tables, ignore_index=True)
        seg_all.to_csv(os.path.join(OUT_DIR, "03_top_segments.csv"), index=False)
    else:
        seg_all = pd.DataFrame()

    # ---- Numeric effects (rank by |cohen_d| then median_diff)
    eff_rows = []
    for c in NUM_COLS:
        if c in df.columns:
            d = numeric_effects(df, c, TARGET)
            if d:
                eff_rows.append(d)
    eff = pd.DataFrame(eff_rows)
    if not eff.empty:
        eff["abs_cohen_d"] = eff["cohen_d"].abs()
        eff = eff.sort_values(["abs_cohen_d", "median_diff"], ascending=False)
        eff.to_csv(os.path.join(OUT_DIR, "04_numeric_effects.csv"), index=False)

    # ---- Binned lift tables for top numeric features (take top 8)
    if not eff.empty:
        top_num = eff["feature"].head(8).tolist()
        bin_tables = []
        for c in top_num:
            bt = binned_lift_table(df, c, TARGET, base_rate, bins=10)
            if not bt.empty:
                bin_tables.append(bt)
        if bin_tables:
            bins_all = pd.concat(bin_tables, ignore_index=True)
            bins_all.to_csv(os.path.join(OUT_DIR, "05_numeric_binned_lift.csv"), index=False)

    # ---- Rule candidates (simple single-feature rules from top segments)
    if not seg_all.empty:
        rules = rule_candidates_from_top_segments(seg_all, min_lift=2.0, max_rules=50)
        rules_eval = eval_rules(df, rules, TARGET, base_rate)
        rules_eval.to_csv(os.path.join(OUT_DIR, "06_rule_candidates.csv"), index=False)

    # ---- Quick "top-k lift" sanity (how many fraud in top 1% by a numeric proxy if exists)
    # This is NOT a model, just a sanity check for a strong score if present.
    proxy = None
    for cand in ["credit_risk_score", "proposed_credit_limit", "velocity_4w"]:
        if cand in df.columns:
            proxy = cand
            break
    if proxy is not None:
        s = df[proxy]
        mask = s.notna()
        tmp = df.loc[mask, [TARGET, proxy]].copy()
        tmp = tmp.sort_values(proxy, ascending=False)
        k = max(1, int(0.01 * len(tmp)))
        top = tmp.head(k)
        top_rate = safe_rate(int(top[TARGET].sum()), len(top))
        topk = pd.DataFrame([{
            "proxy": proxy,
            "k_fraction": 0.01,
            "k_rows": k,
            "topk_fraud_rate": top_rate,
            "topk_lift": lift(top_rate, base_rate),
            "topk_fraud_captured": int(top[TARGET].sum()),
            "total_fraud": fraud_n,
            "recall_at_k": safe_rate(int(top[TARGET].sum()), fraud_n),
        }])
        topk.to_csv(os.path.join(OUT_DIR, "07_topk_sanity.csv"), index=False)

    print(f"Done. Outputs in: {OUT_DIR}")


if __name__ == "__main__":
    main()
