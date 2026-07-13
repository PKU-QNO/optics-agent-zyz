#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fig6_compare.py — Akimov Fig6 Layer3 量化对比 (step08, 粗粒度形貌对比)

**方法论声明 (务必读，与 fig3_compare.py 的本质区别)**：
Fig3 数字化点带 branch_id，可与复现曲线族逐分支精确比对 (归一化距离 median<0.01
量级)。Fig6 数字化 (`fig6_digitized.csv`) 是 `fig6_digitize.py` docstring 已声明的
**粗粒度降级方法**——每面板 ~10-12 条同色曲线密集分布，数字化点没有跨 Re/Im 子图
配对、没有分支编号 (1-12) 对齐，只能做"点到复现曲线族(不分支)的最近邻距离"这种
形貌层面粗对比。

因此本脚本输出的 median/p95 数值 **不能直接套用 Fig3 的 SEPR 自定阈值
(median<0.01, p95<0.03) 来下 PASS/FAIL 结论**——沿用同一套阈值仅作参考基准，
是否合理由 main-agent 结合 Fig6 方法论强度权衡，本脚本不下最终 verdict。

指标定义：
  对每个数字化点 p=(q_e, value)，在同 (pol,l,component) 面板的复现曲线点集
  (来自 fig6_loci_{pol}_l{l}.csv 的 eps_re 或 eps_im 列，按 component 选取，
  不区分 branch_id，即该面板全部分支点混在一起建 KDTree) 里找最近点，
  归一化欧氏距离 d(p) = sqrt( (dq_e/qe_span)^2 + (dvalue/value_span)^2 )。
  qe_span = 10 (轴跨度 [0,10])；value_span 按面板/分量而变 (与 fig6_digitize.py
  的 Y_RANGES 一致，见下方 VALUE_SPAN 常量)。

不自行声明 physical_reproduction_success / PASS / FAIL (需 main-agent + Gate4 人审)。
"""

import csv
import os

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "data"))
FIG_DIR = os.path.abspath(os.path.join(CODE_DIR, "..", "figures"))
CASE_DIR = r"C:\Users\27370\Desktop\project\self-evo-paper-repro\.work\.todo\2401.04146\0707-02-akimov-mie-v1"
REPORT_DIR = os.path.join(CASE_DIR, "08-physical_verification")

QE_SPAN = 10.0

# 与 fig6_digitize.py 的 Y_RANGES / imranges 保持一致 (未做 import 耦合, 手动同步,
# 若 fig6_digitize.py 的范围调整需同步改这里)
VALUE_SPAN = {
    ("TM", 1, "Re"): 20.0,  # [-5,15]
    ("TM", 2, "Re"): 20.0,
    ("TM", 3, "Re"): 20.0,
    ("TE", 1, "Re"): 20.0,
    ("TE", 2, "Re"): 20.0,
    ("TE", 3, "Re"): 20.0,
    ("TM", 1, "Im"): 3.0,   # [0,3]
    ("TM", 2, "Im"): 4.0,   # [0,4]
    ("TM", 3, "Im"): 4.0,   # [0,4]
    ("TE", 1, "Im"): 1.2,   # [0,1.2]
    ("TE", 2, "Im"): 0.8,   # [0,0.8]
    ("TE", 3, "Im"): 0.6,   # [0,0.6]
}

# SEPR Fig3 自定阈值, 仅作参考基准 (不代表 Fig6 直接适用, 见模块 docstring)
REF_THRESHOLD_MEDIAN = 0.01
REF_THRESHOLD_P95 = 0.03

PANELS = [("TM", 1), ("TM", 2), ("TM", 3), ("TE", 1), ("TE", 2), ("TE", 3)]
COMPONENTS = ["Re", "Im"]


def load_digitized(pol: str, l: int, comp: str) -> np.ndarray:
    path = os.path.join(DATA_DIR, "fig6_digitized.csv")
    df = pd.read_csv(path)
    mask = (df["pol"] == pol) & (df["l"] == l) & (df["component"] == comp)
    sub = df[mask]
    return sub[["q_e", "value"]].to_numpy(dtype=float)


def load_repro_curve(pol: str, l: int, comp: str) -> np.ndarray:
    """读 fig6_loci_{pol}_l{l}.csv, 取 (q_e, eps_re 或 eps_im), 不分 branch_id
    (Fig6 数字化点无分支编号对齐凭据, 故复现侧也不按分支拆, 混合建树)."""
    path = os.path.join(DATA_DIR, f"fig6_loci_{pol}_l{l}.csv")
    df = pd.read_csv(path)
    col = "eps_re" if comp == "Re" else "eps_im"
    return df[["q_e", col]].to_numpy(dtype=float)


def nearest_norm_dist(dig_pts: np.ndarray, repro_pts: np.ndarray,
                       qe_span: float, value_span: float) -> np.ndarray:
    if len(dig_pts) == 0 or len(repro_pts) == 0:
        return np.full(len(dig_pts), np.nan)
    scale = np.array([qe_span, value_span])
    repro_n = repro_pts / scale
    dig_n = dig_pts / scale
    tree = cKDTree(repro_n)
    dist, _ = tree.query(dig_n, k=1)
    return dist


def _stats(d: np.ndarray) -> dict:
    d = d[np.isfinite(d)]
    if len(d) == 0:
        return {"median": None, "p95": None, "max": None, "n": 0}
    return {
        "median": float(np.median(d)),
        "p95": float(np.percentile(d, 95)),
        "max": float(np.max(d)),
        "n": int(len(d)),
    }


def panel_metrics(pol: str, l: int, comp: str) -> dict:
    dig = load_digitized(pol, l, comp)
    repro = load_repro_curve(pol, l, comp)
    value_span = VALUE_SPAN[(pol, l, comp)]
    d = nearest_norm_dist(dig, repro, QE_SPAN, value_span)
    st = _stats(d)
    st["_dist"] = d
    st["n_dig"] = len(dig)
    st["n_repro"] = len(repro)
    st["value_span"] = value_span
    return st


def build_all_metrics() -> dict:
    per_panel = {}
    all_dist = []
    for (pol, l) in PANELS:
        key = f"{pol}{l}"
        per_panel[key] = {}
        for comp in COMPONENTS:
            st = panel_metrics(pol, l, comp)
            all_dist.append(st["_dist"])
            per_panel[key][comp] = st
    glob_d = np.concatenate([d[np.isfinite(d)] for d in all_dist]) if all_dist else np.array([])
    glob = _stats(glob_d)
    return per_panel, glob


def build_metrics_csv(per_panel: dict) -> pd.DataFrame:
    rows = []
    for key, d in per_panel.items():
        pol = key[:2]
        l = int(key[2:])
        for comp in COMPONENTS:
            r = d[comp]
            med = r["median"]
            p95 = r["p95"]
            rows.append({
                "panel": key, "pol": pol, "l": l, "component": comp,
                "n_dig": r["n_dig"], "n_repro": r["n_repro"],
                "value_span": r["value_span"],
                "median": med, "p95": p95, "max": r["max"],
                "ref_pass_median": (med is not None and med < REF_THRESHOLD_MEDIAN),
                "ref_pass_p95": (p95 is not None and p95 < REF_THRESHOLD_P95),
            })
    return pd.DataFrame(rows)


def main():
    per_panel, glob = build_all_metrics()

    df = build_metrics_csv(per_panel)
    df_glob = pd.DataFrame([{
        "panel": "GLOBAL", "pol": "ALL", "l": 0, "component": "Re+Im",
        "n_dig": glob["n"], "n_repro": None, "value_span": None,
        "median": glob["median"], "p95": glob["p95"], "max": glob["max"],
        "ref_pass_median": (glob["median"] is not None and glob["median"] < REF_THRESHOLD_MEDIAN),
        "ref_pass_p95": (glob["p95"] is not None and glob["p95"] < REF_THRESHOLD_P95),
    }])
    df_out = pd.concat([df, df_glob], ignore_index=True)
    csv_path = os.path.join(DATA_DIR, "fig6_layer3_metrics.csv")
    df_out.to_csv(csv_path, index=False, float_format="%.6f")
    print("wrote", csv_path)

    print("\n=== 全局 (12 panel x component 混合, 无分支对齐, 粗粒度形貌对比) ===")
    print(f"  median={glob['median']:.5f} (Fig3 参考阈值<{REF_THRESHOLD_MEDIAN}, 非 Fig6 专用标准)")
    print(f"  p95   ={glob['p95']:.5f} (Fig3 参考阈值<{REF_THRESHOLD_P95}, 非 Fig6 专用标准)")
    print(f"  max   ={glob['max']:.5f}  n={glob['n']}")
    print("\n=== 逐面板 (median / p95 / n_dig / n_repro) ===")
    for key, d in per_panel.items():
        for comp in COMPONENTS:
            r = d[comp]
            print(f"  {key:5s} {comp}: median={r['median']:.5f} p95={r['p95']:.5f} "
                  f"max={r['max']:.5f} n_dig={r['n_dig']} n_repro={r['n_repro']}")
    return per_panel, glob, df_out


if __name__ == "__main__":
    main()
