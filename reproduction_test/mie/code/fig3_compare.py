#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fig3_compare.py — Akimov Fig3 Layer3 量化对比 (step08)

按 step08_compare_interface.md §四签名实现:
  数字化取样点 -> 复现曲线族 的最近归一化距离, 逐面板 sr/nr 统计 + 全局 verdict.

指标定义 (接口 md §一):
  对每个数字化点 p=(q_e, eps), 在同面板同类型的复现曲线点集里找最近点,
  归一化欧氏距离 d(p) = sqrt( ((dq_e)/10)^2 + ((d_eps)/25)^2 ).
  归一化: q_e 除以轴跨度 10, eps 除以轴跨度 25 ([-10,15]).
  方向: 数字化点(带主观误差) -> 复现曲线(密采样真值参照).

阈值 (接口 md §二, SEPR 自定, 非社区标准):
  归一化距离 中位数 < 0.01, 95分位 < 0.03.
  另加 Gate2 强制附加判据: 曲线支数逐面板一致 (已在 T4 PASS, 本步引用).

不自行声明 physical_reproduction_success (需 Gate4 人审).
"""

import json
import os

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

# --- 路径 (相对本文件定位到 reproduction_test/mie) ---
_HERE = os.path.dirname(os.path.abspath(__file__))
_MIE = os.path.dirname(_HERE)  # reproduction_test/mie
DATA_DIR = os.path.join(_MIE, "data")
FIG_DIR = os.path.join(_MIE, "figures")

# 归一化轴跨度
QE_SPAN = 10.0
EPS_SPAN = 25.0

# SEPR 自定阈值 (非社区标准)
THRESHOLD_MEDIAN = 0.01
THRESHOLD_P95 = 0.03

PANELS = [("TM", 1), ("TM", 2), ("TM", 3), ("TE", 1), ("TE", 2), ("TE", 3)]
TYPES = ["sr", "nr"]


def load_repro_curve(pol: str, l: int, typ: str) -> np.ndarray:
    """读 fig3_loci_{pol}_l{l}.csv, 过滤 type==typ, 返回 (N,2) 数组 [q_e, eps].
    nr 含 branch_id=0 平凡线 (原图 eps=1 有该蓝实线), 全部纳入对比."""
    path = os.path.join(DATA_DIR, f"fig3_loci_{pol}_l{l}.csv")
    df = pd.read_csv(path)
    sub = df[df["type"] == typ]
    return sub[["q_e", "eps_ratio"]].to_numpy(dtype=float)


def load_digitized(pol: str, l: int, typ: str) -> np.ndarray:
    """读 fig3_digitized.csv, 过滤 (pol,l,type), 返回 (M,2) 数组 [q_e, eps]."""
    path = os.path.join(DATA_DIR, "fig3_digitized.csv")
    df = pd.read_csv(path)
    mask = (df["pol"] == pol) & (df["l"] == l) & (df["type"] == typ)
    sub = df[mask]
    return sub[["q_e", "eps_ratio"]].to_numpy(dtype=float)


def nearest_norm_dist(dig_pts: np.ndarray, repro_pts: np.ndarray,
                      qe_span: float = QE_SPAN, eps_span: float = EPS_SPAN) -> np.ndarray:
    """对每个 dig 点算到 repro 点集的最近归一化距离, 返回 (M,) 距离数组.
    归一化: dq/qe_span, deps/eps_span. 用 cKDTree 对归一化 repro 点集建树."""
    if len(dig_pts) == 0 or len(repro_pts) == 0:
        return np.full(len(dig_pts), np.nan)
    scale = np.array([qe_span, eps_span])
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


def panel_metrics(pol: str, l: int) -> dict:
    """对一个面板算 sr/nr 的 {median, p95, max, n} 归一化距离统计.
    返回 {'sr': {...}, 'nr': {...}} 并附原始距离数组供画图."""
    out = {}
    for typ in TYPES:
        dig = load_digitized(pol, l, typ)
        repro = load_repro_curve(pol, l, typ)
        d = nearest_norm_dist(dig, repro)
        st = _stats(d)
        st["_dist"] = d  # 供画图, 序列化前剔除
        out[typ] = st
    return out


def layer3_verdict(threshold_median: float = THRESHOLD_MEDIAN,
                   threshold_p95: float = THRESHOLD_P95) -> dict:
    """聚合六面板 sr+nr, 判 median<阈值 且 p95<阈值; 结合完备性(已PASS)出 Layer3 verdict.
    返回逐面板 + 全局统计 + verdict. 不自行声明 physical_reproduction_success (需 Gate4)."""
    per_panel = {}
    all_dist = []
    for (pol, l) in PANELS:
        pm = panel_metrics(pol, l)
        key = f"{pol}{l}"
        per_panel[key] = {}
        for typ in TYPES:
            st = pm[typ]
            all_dist.append(st["_dist"])
            med = st["median"]
            p95 = st["p95"]
            pass_med = (med is not None and med < threshold_median)
            pass_p95 = (p95 is not None and p95 < threshold_p95)
            per_panel[key][typ] = {
                "pol": pol, "l": l, "type": typ,
                "median": med, "p95": p95, "max": st["max"], "n": st["n"],
                "pass_median": bool(pass_med),
                "pass_p95": bool(pass_p95),
                "pass": bool(pass_med and pass_p95),
            }

    glob = np.concatenate([d[np.isfinite(d)] for d in all_dist])
    g_med = float(np.median(glob))
    g_p95 = float(np.percentile(glob, 95))
    g_max = float(np.max(glob))
    g_pass_med = g_med < threshold_median
    g_pass_p95 = g_p95 < threshold_p95
    completeness_pass = True  # Gate2 强制附加判据, T4 已 PASS (引用 completeness_check.txt)

    global_pass = bool(g_pass_med and g_pass_p95 and completeness_pass)

    # 逐面板超标清单
    over = []
    for key, d in per_panel.items():
        for typ in TYPES:
            if not d[typ]["pass"]:
                over.append({
                    "panel": key, "type": typ,
                    "median": d[typ]["median"], "p95": d[typ]["p95"],
                    "pass_median": d[typ]["pass_median"],
                    "pass_p95": d[typ]["pass_p95"],
                })

    verdict = {
        "layer3_metric": "nearest normalized distance (digitized -> repro curve)",
        "normalization": {"qe_span": QE_SPAN, "eps_span": EPS_SPAN},
        "thresholds": {
            "median": threshold_median,
            "p95": threshold_p95,
            "note": "SEPR 自定阈值, loci 图无社区先例 RMSE/距离标准; 最终由 Gate4 用户认可后生效, 不得自行放宽",
        },
        "global": {
            "median": g_med, "p95": g_p95, "max": g_max, "n": int(len(glob)),
            "pass_median": bool(g_pass_med), "pass_p95": bool(g_pass_p95),
        },
        "completeness": {
            "status": "PASS",
            "source": ".work/.todo/2401.04146/0703-01-akimov-mie-v1/06-run_and_monitor/completeness_check.txt",
            "note": "Gate2 强制附加判据, 切片法 vs contour 支数逐面板一致, contour 覆盖 >99.8%",
        },
        "per_panel": per_panel,
        "over_threshold_items": over,
        "layer3_verdict": "PASS" if global_pass else "CONDITIONAL",
        "verdict_note": (
            "全局 median 与 p95 均达标 + 完备性 PASS -> Layer3 PASS"
            if global_pass else
            "全局或部分面板 median/p95 超 SEPR 自定阈值; 需 Gate4 人审裁决 "
            "(接受为数字化误差 / 微调阈值 / sr 区域加密重测), 不自行判 FAIL 也不自行放宽"
        ),
        "result_class_max": "partial_physical_match (待 Gate4 人审; 本步不声明 physical_reproduction_success)",
    }
    return verdict, per_panel


def build_metrics_csv(per_panel: dict) -> pd.DataFrame:
    """逐面板 sr/nr 12 行 + 全局聚合行 -> DataFrame."""
    rows = []
    for key, d in per_panel.items():
        for typ in TYPES:
            r = d[typ]
            rows.append({
                "panel": key, "pol": r["pol"], "l": r["l"], "type": typ,
                "n": r["n"], "median": r["median"], "p95": r["p95"], "max": r["max"],
                "pass_median": r["pass_median"], "pass_p95": r["pass_p95"], "pass": r["pass"],
            })
    return pd.DataFrame(rows)


def main():
    verdict, per_panel = layer3_verdict()

    # 1) metrics CSV
    df = build_metrics_csv(per_panel)
    # 追加全局聚合行
    g = verdict["global"]
    df_glob = pd.DataFrame([{
        "panel": "GLOBAL", "pol": "ALL", "l": 0, "type": "sr+nr",
        "n": g["n"], "median": g["median"], "p95": g["p95"], "max": g["max"],
        "pass_median": g["pass_median"], "pass_p95": g["pass_p95"],
        "pass": bool(g["pass_median"] and g["pass_p95"]),
    }])
    df_out = pd.concat([df, df_glob], ignore_index=True)
    csv_path = os.path.join(DATA_DIR, "fig3_layer3_metrics.csv")
    df_out.to_csv(csv_path, index=False, float_format="%.6f")
    print("wrote", csv_path)

    # 2) verdict JSON
    verdict_path = os.path.join(
        _MIE, "..", "..", ".work", ".todo", "2401.04146",
        "0703-01-akimov-mie-v1", "08-physical_verification", "layer3_verdict.json")
    verdict_path = os.path.abspath(verdict_path)
    os.makedirs(os.path.dirname(verdict_path), exist_ok=True)
    with open(verdict_path, "w", encoding="utf-8") as f:
        json.dump(verdict, f, ensure_ascii=False, indent=2)
    print("wrote", verdict_path)

    # 打印摘要
    print("\n=== 全局 ===")
    print(f"  median={g['median']:.5f} (阈值<{THRESHOLD_MEDIAN}) "
          f"{'PASS' if g['pass_median'] else 'OVER'}")
    print(f"  p95   ={g['p95']:.5f} (阈值<{THRESHOLD_P95}) "
          f"{'PASS' if g['pass_p95'] else 'OVER'}")
    print(f"  verdict={verdict['layer3_verdict']}")
    print("\n=== 逐面板 (median / p95) ===")
    for key, d in per_panel.items():
        for typ in TYPES:
            r = d[typ]
            flag = "OK" if r["pass"] else "OVER"
            print(f"  {key:5s} {typ}: median={r['median']:.5f} "
                  f"p95={r['p95']:.5f} max={r['max']:.5f} n={r['n']} [{flag}]")
    return verdict, per_panel


if __name__ == "__main__":
    main()
