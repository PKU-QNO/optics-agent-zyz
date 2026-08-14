# -*- coding: utf-8 -*-
"""
params.py — mie-f 复现 step04 第一阶段公共参数（Layer1 Mie 基准用）
=========================================================================
本文件是 step04 代码的「单一物理输入源」之一（配合 formalization/alaee2018-fig1.yaml
spec 消费，不消费论文 prose）。所有 Mie 基准相关参数集中在这里，便于 gate③ 逐项核对。

物理来源：
  - formalization/alaee2018-fig1.yaml（gate② 定稿，2026-08-05）
  - gate① 用户裁决：ε_r=6.25（=2.5²，n=2.5）、横轴 2a/λ、y=linear C_sca/(λ²/2π)

关键换算（⚠️ gate③ 硬性要求，详见 size_param_to_x_mie 注释）：
  - Alaee 横轴是无量纲 2a/λ；
  - Mie 系数用 B&H 记号 x_mie = ka（host 波数 × 半径）；
  - host=air（ε_d=1, n_d=1）时 k = 2π/λ ⇒ x_mie = ka = 2πa/λ = π·(2a/λ)。
    绝不能把 2a/λ 直接当 x_mie 用，否则 Mie 共振峰位全偏 π 倍。
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# 材料参数（Alaee 2018 Fig.1(a)，介电球，host=air）
# ---------------------------------------------------------------------------

#: 介电球相对介电常数 ε_r = 2.5² = 6.25（实标量、无色散、无吸收；PDF 提取丢上标
#: "2.5²"→"2.52" 已由 opus 审查 R1 纠正）
EPS_R = 6.25

#: host（背景）相对介电常数（air）
HOST_EPS_R = 1.0

#: 介电球相对折射率 n = √ε_r = √6.25 = 2.5（对 host=air，m = n/n_d = n）
N_REFRACTIVE = 2.5

# ---------------------------------------------------------------------------
# 扫描范围（Alaee Fig.1(a) 横轴，无量纲尺寸参数 2a/λ）
# ---------------------------------------------------------------------------

#: Alaee 横轴 2a/λ 扫描区间 [0.2, 1.0]（gate② 待澄清1 定稿：像素统计曲线延伸到 x≈1.0，
#: 原 [0.2,0.8] 上限偏小；0.75 验证点留余量）
SIZE_PARAM_RANGE = (0.2, 1.0)

#: 横轴采样点数（与 formalization spec 一致）
N_POINTS = 200


def size_param_to_x_mie(size_param_2a_over_lambda: float) -> float:
    """把 Alaee 横轴 2a/λ 换算成 B&H Mie 尺寸参数 x_mie = ka。

    host=air（ε_d=1, n_d=1）时：
        k = 2π/λ,  x_mie = ka = 2πa/λ = π·(2a/λ)

    所以 x_mie = π · (2a/λ)。

    参数
    ----
    size_param_2a_over_lambda : float
        Alaee 横轴无量纲尺寸参数 2a/λ（论文 Fig.1(a) x 轴）。

    返回
    ----
    float
        B&H Mie 尺寸参数 x_mie = ka（无单位）。

    注意
    ----
    这是 gate③ 强调的翻车点：**不得拿 2a/λ 直接当 x_mie 用**。锚点校验：
    介电球 n=2.5 第一磁偶极 Mie 共振峰应落在 2a/λ≈0.5–0.7（x_mie≈1.6–2.2）；
    若峰位偏 π 倍即此换算错误。
    """
    return math.pi * size_param_2a_over_lambda


def wiscombe_nmax(x_mie: float) -> int:
    """Wiscombe 截断阶数：谱求和所需最大多极阶 n_max。

    采用 Wiscombe (1980) 经验公式：
        n_max = ceil(x + 4·x^(1/3) + 2)
    这是 Mie 计算的教材惯例（formalization spec 截断标准），保证总散射/消光
    截面求和收敛到机器精度量级。

    参数
    ----
    x_mie : float
        B&H Mie 尺寸参数 ka（注意：是 ka，不是 Alaee 横轴 2a/λ）。

    返回
    ----
    int
        最小足够截断阶数 n_max（≥1）。
    """
    return int(math.ceil(x_mie + 4.0 * x_mie ** (1.0 / 3.0) + 2.0))
