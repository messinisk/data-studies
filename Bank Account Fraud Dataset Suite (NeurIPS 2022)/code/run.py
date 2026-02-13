import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from textwrap import fill

def short_label(s: str, width: int = 28) -> str:
    s = str(s)
    return fill(s, width=width)

def read_file(path:Path)->pd.DataFrame:
    return pd.read_csv(path)

def savefig(name: str) -> Path:
    p = f"figures/image/{name}"
    plt.tight_layout()
    plt.savefig(p, dpi=300)
    plt.close()
    return p


def grafical1(title:str, labels:list[str],
            values:list[str], ylabel:str, save_out:str  ):
    plt.figure()
    plt.bar(labels, values)
    plt.title(title)
    plt.ylabel(ylabel)
    savefig(save_out)

def grafical2(title:str, labels:pd.DataFrame,
            values:pd.DataFrame, xlabel:str, ylabel:str, save_out:str  ):
     plt.figure()
     plt.plot(labels, values, marker="o")
     plt.title(title)
     plt.xlabel(xlabel)
     plt.ylabel(ylabel)
     savefig(save_out)

def grafical3(title:str, labels:pd.DataFrame,
            values:pd.DataFrame, xlabel:str, save_out:str  ):
     plt.figure()
     plt.plot(labels, values)
     plt.title(title)
     plt.xlabel(xlabel)
     savefig(save_out)


if __name__ == "__main__":
    pass
    # -------------------------
    # 00_summary.csv -> μικρό “tile” (bar)
    # -------------------------
    # summary  = read_file("report\\00_summary.csv").iloc[0]
    # fraud_rate = float(summary["fraud_rate"])
    # nonfraud_rate = 1.0 - fraud_rate
    # plt.figure(figsize=(6, 5))
    # wedges, _ = plt.pie([nonfraud_rate, fraud_rate], startangle=90)
    # # donut hole
    # centre = plt.Circle((0, 0), 0.65, fc="white")
    # plt.gca().add_artist(centre)
    # plt.title("Fraud vs Non-fraud (share)")
    # plt.legend(wedges, [f"Non-fraud: {nonfraud_rate*100:.2f}%", f"Fraud: {fraud_rate*100:.2f}%"],
    #            loc="center left", bbox_to_anchor=(1, 0.5))
    # savefig("00_summary_fraud_share_donut_v3.png")

   
    # -------------------------
    # 02_drift_by_month.csv -> line (fraud_rate ανά month)
    # -------------------------
    # drift_by_month = read_file("report\\02_drift_by_month.csv")

    # if "month" in drift_by_month.columns and "fraud_rate" in drift_by_month.columns:
    #     d = drift_by_month.sort_values("month")
    #     grafical2("Fraud rate ανά month (drift)", d["month"], d["fraud_rate"], "month", "fraud_rate", "02_drift_fraud_rate.png")
    # if "month" in drift_by_month.columns and "lift_vs_overall" in drift_by_month.columns:
    #     d = d.sort_values("month")
    #     grafical2("Lift vs overall ανά month", d["month"], d["lift_vs_overall"], "month", "lift", "02_drift_lift.png")
    
    # if "month" in drift_by_month.columns and "fraud_rate" in d.columns:
    #         d = drift_by_month.sort_values("month")
    #         plt.figure()
    #         plt.plot(d["month"], d["fraud_rate"], marker="o")
    #         plt.title("Fraud rate ανά month (drift)")
    #         plt.xlabel("month")
    #         plt.ylabel("fraud_rate")
    #         savefig("02_drift_fraud_rate1.png")

    # -------------------------
    # 03_top_segments.csv -> bar (top lifts)
    # -------------------------
    # top_segments = read_file("report\\03_top_segments.csv")
    # ---------- 03_top_segments: 2-panel chart (lift + fraud_rate) ----------
    # need = {"feature", "value", "lift", "count", "fraud_rate"}
    # if need.issubset(top_segments.columns):
    #     top = top_segments.sort_values("lift", ascending=False).head(15).copy()
    #     top["label"] = top["feature"].astype(str) + "=" + top["value"].astype(str)
    #     top = top.iloc[::-1]  # for barh bottom->top

    #     fig, ax = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    #     # left: lift
    #     ax[0].barh(top["label"], top["lift"])
    #     ax[0].set_title("Lift vs overall")
    #     ax[0].set_xlabel("lift")

    #     # right: fraud_rate (%)
    #     ax[1].barh(top["label"], top["fraud_rate"] * 100.0)
    #     ax[1].set_title("Fraud rate")
    #     ax[1].set_xlabel("fraud_rate (%)")

    #     plt.suptitle("Top 15 segments")
    #     plt.tight_layout()
    #     plt.savefig("figures\\image\\03_top_segments_2panel_v3.png", dpi=300)
    #     plt.close()
    # # ---------- 03_top_segments: συνοδευτικός πίνακας Top 15 ----------
    # need = {"feature", "value", "lift", "count", "fraud_rate", "fraud_count"}
    # if need.issubset(top_segments.columns):
    #     top = top_segments.sort_values("lift", ascending=False).head(15).copy()
    #     top["fraud_rate_pct"] = top["fraud_rate"] * 100.0
    #     cols = ["feature", "value", "lift", "count", "fraud_count", "fraud_rate_pct"]
    #     top[cols].to_csv("figures\\table\\03_top_segments_top15_table_v3.csv", index=False)






    # -------------------------
    # 04_numeric_effects.csv -> bar (abs cohen_d) + median_diff
    # -------------------------
    # numeric_effects = read_file("report\\04_numeric_effects.csv")
    # if {"feature", "cohen_d"}.issubset(numeric_effects.columns):
    #     numeric_effects["abs_cohen_d"] = numeric_effects["cohen_d"].abs()
    #     top = numeric_effects.sort_values("abs_cohen_d", ascending=False).head(15)

    #     plt.figure()
    #     plt.barh(top["feature"][::-1], top["abs_cohen_d"][::-1])
    #     plt.title("Top numeric drivers (|Cohen's d|)")
    #     plt.xlabel("|cohen_d|")
    #     savefig("04_numeric_abs_cohen_d_top15.png")

    # if {"feature", "median_diff"}.issubset(numeric_effects.columns):
    #     top = numeric_effects.reindex(numeric_effects["median_diff"].abs().sort_values(ascending=False).index).head(15)
    #     plt.figure()
    #     plt.barh(top["feature"][::-1], top["median_diff"][::-1])
    #     plt.title("Top numeric drivers (median_diff fraud - nonfraud)")
    #     plt.xlabel("median_diff")
    #     savefig("04_numeric_median_diff_top15.png")



    # -------------------------
    # 05_numeric_binned_lift.csv -> line/bar ανά feature
    # -------------------------
    # numeric_binned_lift = read_file("report\\05_numeric_binned_lift.csv")
    #     # expected columns: feature, bin, count, fraud_count, fraud_rate, lift
    # if {"feature", "bin", "lift"}.issubset(numeric_binned_lift.columns):
    #     for feat in numeric_binned_lift["feature"].dropna().unique():
    #         sub = numeric_binned_lift[numeric_binned_lift["feature"] == feat].copy()
    #         if len(sub) == 0:
    #             continue

    #         # προσπάθησε να κρατήσεις λογική σειρά bin:
    #         # αν υπάρχει MISSING βάλ'το τελευταίο
    #         sub["is_missing"] = sub["bin"].astype(str).eq("MISSING")
    #         sub = sub.sort_values(["is_missing", "bin"], ascending=[True, True])

    #         plt.figure()
    #         plt.plot(range(len(sub)), sub["lift"], marker="o")
    #         plt.title(f"Lift ανά bins — {feat}")
    #         plt.xlabel("bin index")
    #         plt.ylabel("lift vs overall")
    #         savefig(f"05_bins_lift_{feat}.png")


    # -------------------------
    # 06_rule_candidates.csv -> bar top rules by lift
    # -------------------------
    # rule_candidates = read_file("report\\06_rule_candidates.csv")
    # # expected columns: rule, count, fraud_count, fraud_rate, lift
    # if {"rule", "lift"}.issubset(rule_candidates.columns) and len(rule_candidates) > 0:
    #     top = rule_candidates.sort_values("lift", ascending=False).head(15).copy()

    #     plt.figure()
    #     plt.barh(top["rule"][::-1], top["lift"][::-1])
    #     plt.title("Top rule candidates by lift")
    #     plt.xlabel("lift vs overall")
    #     savefig("06_rule_candidates_top15.png")

    # -------------------------
    # 07_topk_sanity.csv -> single bar: topk_lift + recall_at_k
    # -------------------------
    # topk_sanity = read_file("report\\07_topk_sanity.csv")
    # # ---------- 07_topk_sanity: donut captured vs missed fraud ----------
    # row = topk_sanity.iloc[0]
    # captured = float(row.get("topk_fraud_captured", np.nan))
    # total_fraud = float(row.get("total_fraud", np.nan))

    # if np.isfinite(captured) and np.isfinite(total_fraud) and total_fraud > 0:
    #     missed = total_fraud - captured

    #     plt.figure(figsize=(6, 5))
    #     wedges, _ = plt.pie([missed, captured], startangle=90)
    #     centre = plt.Circle((0, 0), 0.65, fc="white")
    #     plt.gca().add_artist(centre)

    #     k = row.get("k_fraction", "")
    #     proxy = row.get("proxy", "")
    #     plt.title(f"Fraud captured vs missed (top-k) — proxy={proxy}, k={k}")
    #     plt.legend(
    #         wedges,
    #         [f"Missed: {missed:.0f}", f"Captured: {captured:.0f}"],
    #         loc="center left", bbox_to_anchor=(1, 0.5),
    #         )
    #     savefig("07_topk_captured_vs_missed_donut_v3.png")


  



