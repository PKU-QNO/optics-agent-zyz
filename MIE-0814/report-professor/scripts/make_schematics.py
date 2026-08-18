#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate physical-model schematic figures for the professor report.

Outputs (into ../figs/):
  schematic_sphere.png       -- plane-wave scattering by a single sphere
  schematic_double_disk.png  -- two coupled gold nanodisks (Alaee 2018 Fig.3)

Labels are in English (standard for physics figures); geometry is illustrative
(not to scale).  Run:  python make_schematics.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "figs")
os.makedirs(OUT, exist_ok=True)

GOLD = "#c9a227"
GOLD_DARK = "#8a6d1d"
BLUE = "#2e6fa8"
RED = "#c0392b"
GRAY = "#555555"


def _arrow(ax, xy, dxy, color, width=0.004, head=0.05, lw=1.4):
    a = FancyArrowPatch(xy, (xy[0] + dxy[0], xy[1] + dxy[1]),
                        arrowstyle="-|>", mutation_scale=16,
                        color=color, linewidth=lw)
    ax.add_patch(a)


def schematic_sphere(path):
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.set_aspect("equal")
    ax.axis("off")

    a = 1.0  # sphere radius (normalized)
    sphere = Circle((0, 0), a, facecolor="#dbe9f5", edgecolor=BLUE, lw=2, zorder=3)
    ax.add_patch(sphere)
    ax.text(0, 0, r"sphere\n$\varepsilon_r$", ha="center", va="center",
            fontsize=11, color=BLUE)

    # incident plane wave: parallel arrows from the left, propagating +z (drawn as +x here)
    for y in np.linspace(-2.2, 2.2, 7):
        _arrow(ax, (-3.2, y), (1.3, 0), GRAY)
    ax.annotate("incident plane wave\n$E_0\\,e^{-ik_0 z}$ (x-pol)",
                xy=(-3.2, 2.7), xytext=(-3.2, 3.1),
                fontsize=10, color=GRAY, ha="left", va="bottom")

    # scattered field: radial arrows around the sphere
    for th in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        dx, dy = np.cos(th), np.sin(th)
        _arrow(ax, ((a + 0.05) * dx, (a + 0.05) * dy), (0.9 * dx, 0.9 * dy), RED)
    ax.text(2.6, 2.0, "scattered\nfield", fontsize=10, color=RED, ha="left")

    # axes
    _arrow(ax, (-3.0, -2.9), (0.6, 0), BLUE)
    _arrow(ax, (-3.0, -2.9), (0, 0.6), BLUE)
    ax.text(-2.35, -3.15, "$x$", fontsize=10, color=BLUE)
    ax.text(-3.15, -2.25, "$z$", fontsize=10, color=BLUE)

    ax.set_xlim(-3.6, 3.6)
    ax.set_ylim(-3.4, 3.4)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


def schematic_double_disk(path):
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    ax.set_aspect("equal")
    ax.axis("off")

    # normalised geometry: a = radius, t = height, g = gap
    a, t, g = 1.0, 0.55, 0.9
    # lower disk: centred at z = -(g/2 + t/2), upper at +(g/2 + t/2)
    ylo = -(g / 2 + t)
    yhi = g / 2
    for y0, tag in ((ylo, "lower"), (yhi, "upper")):
        ax.add_patch(Rectangle((-a, y0), 2 * a, t, facecolor=GOLD,
                               edgecolor=GOLD_DARK, lw=2, zorder=3))
        ax.text(0, y0 + t / 2, "Au", ha="center", va="center",
                fontsize=11, color="white", zorder=4)

    # dimension annotations
    # radius a (horizontal)
    ax.annotate("", xy=(-a, ylo - 0.35), xytext=(0, ylo - 0.35),
                arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1.2))
    ax.text(-a / 2, ylo - 0.62, "$a=250$ nm", ha="center", va="top",
            fontsize=10, color=GRAY)
    # height t (vertical, on the right of lower disk)
    ax.annotate("", xy=(a + 0.3, ylo), xytext=(a + 0.3, ylo + t),
                arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1.2))
    ax.text(a + 0.42, ylo + t / 2, "$t=80$ nm", ha="left", va="center",
            fontsize=10, color=GRAY)
    # gap g (vertical, between the disks)
    ax.annotate("", xy=(a + 0.3, ylo + t), xytext=(a + 0.3, yhi),
                arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1.2))
    ax.text(a + 0.42, (ylo + t + yhi) / 2, "$g=120$ nm", ha="left", va="center",
            fontsize=10, color=GRAY)

    # incident wave from the left (propagating +z drawn as +x), x-polarized
    for y in np.linspace(ylo - 0.1, yhi + t + 0.1, 5):
        _arrow(ax, (-2.6, y), (0.9, 0), GRAY)
    ax.annotate("incident\n$E_0 e^{-ik_0 z}$", xy=(-2.6, yhi + t + 0.6),
                xytext=(-2.6, yhi + t + 1.1), fontsize=9.5, color=GRAY,
                ha="left", va="bottom")

    # z axis
    _arrow(ax, (-2.6, ylo - 1.1), (0, 0.7), BLUE)
    ax.text(-2.72, ylo - 0.5, "$z$", fontsize=10, color=BLUE)

    ax.set_xlim(-3.0, 3.0)
    ax.set_ylim(ylo - 1.4, yhi + t + 1.6)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


if __name__ == "__main__":
    schematic_sphere(os.path.join(OUT, "schematic_sphere.png"))
    schematic_double_disk(os.path.join(OUT, "schematic_double_disk.png"))
