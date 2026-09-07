"""FIXERS-template styled matplotlib chart helpers.

Matches the chart conventions in the FIXERS 19기 PPT template (slides 10–12):

- NanumSquare for body, NanumSquare Bold only for the unit label
- Title: NanumSquare 12pt regular, dark gray, centered
- Unit label (e.g. ``(%)`` , ``(Pt)``): NanumSquare Bold 10pt, dark gray,
  placed next to the top of the y-axis (not in the upper-right corner)
- Axis tick labels: NanumSquare 10pt, dark gray, raw numbers (no ``%`` suffix)
- No tick marks on the axis lines (only the labels remain)
- Axis spines drawn in light gray with arrowheads at the y-top and x-right ends
- No gridlines, top/right spines hidden, no source caption
- Legend at the bottom (only when more than one series), 10pt, no frame
- Color palette: navy primary, light/pale blue secondary, gray tertiary,
  wine red as the accent
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter, LogLocator, MaxNLocator, NullFormatter


FIXERS_COLORS = {
    "navy": "#10253F",
    "blue": "#8FAADC",
    "pale_blue": "#B9CDE5",
    "gray": "#8D8D8D",
    "light_gray": "#D9D9D9",
    "wine": "#C00000",
    "text_dark": "#333333",
    "text_axis": "#595959",
    "spine": "#BFBFBF",
}

SERIES_PALETTE: list[str] = [
    FIXERS_COLORS["navy"],
    FIXERS_COLORS["blue"],
    FIXERS_COLORS["pale_blue"],
    FIXERS_COLORS["gray"],
    FIXERS_COLORS["light_gray"],
]
ACCENT = FIXERS_COLORS["wine"]

_FONT_DIR = Path.home() / "Library" / "Fonts"
_FONT_REGULAR = _FONT_DIR / "NanumSquareR.ttf"
_FONT_BOLD = _FONT_DIR / "NanumSquareB.ttf"

_STYLE_APPLIED = False


def apply_style() -> None:
    """Register NanumSquare fonts and set FIXERS-friendly matplotlib defaults."""
    global _STYLE_APPLIED
    if _STYLE_APPLIED:
        return

    for path in (_FONT_REGULAR, _FONT_BOLD):
        if path.exists():
            font_manager.fontManager.addfont(str(path))

    mpl.rcParams.update({
        "font.family": "NanumSquare",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.edgecolor": FIXERS_COLORS["spine"],
        "axes.labelcolor": FIXERS_COLORS["text_axis"],
        "xtick.color": FIXERS_COLORS["text_axis"],
        "ytick.color": FIXERS_COLORS["text_axis"],
        "axes.grid": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.0,
        "ytick.major.width": 0.0,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "xtick.minor.width": 0.0,
        "ytick.minor.width": 0.0,
        "xtick.minor.size": 0,
        "ytick.minor.size": 0,
        "lines.linewidth": 1.5,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })
    _STYLE_APPLIED = True


def _plain_number_formatter(x: float, _pos) -> str:
    if abs(x - round(x)) < 1e-9:
        return f"{int(round(x))}"
    return f"{x:.1f}"


def _percent_value_formatter(x: float, _pos) -> str:
    val = x * 100
    if abs(val - round(val)) < 1e-9:
        return f"{int(round(val))}"
    return f"{val:.1f}"


def _format_axis(ax: Axes, unit: str | None) -> None:
    """Set y-tick formatter according to the unit string (no '%' suffix)."""
    unit_norm = (unit or "").lower()
    if unit_norm in {"%", "pct", "percent"}:
        ax.yaxis.set_major_formatter(FuncFormatter(_percent_value_formatter))
    else:
        ax.yaxis.set_major_formatter(FuncFormatter(_plain_number_formatter))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))


def _draw_unit_label(ax: Axes, unit: str | None) -> None:
    if not unit:
        return
    ax.text(
        0.0,
        1.04,
        f"({unit})",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
        fontweight="bold",
        color=FIXERS_COLORS["text_axis"],
    )


def _draw_x_label(ax: Axes, label: str | None) -> None:
    if not label:
        return
    ax.set_xlabel(
        label,
        fontsize=10,
        fontweight="bold",
        color=FIXERS_COLORS["text_axis"],
        labelpad=8,
    )


def _draw_title(ax: Axes, title: str, subtitle: str | None = None) -> None:
    pad = 22 if subtitle else 10
    ax.set_title(
        title,
        loc="center",
        fontsize=12,
        fontweight="bold",
        color=FIXERS_COLORS["text_axis"],
        pad=pad,
    )
    if subtitle:
        ax.text(
            0.5, 1.02, subtitle,
            transform=ax.transAxes,
            ha="center", va="bottom",
            fontsize=9, fontweight="normal",
            color=FIXERS_COLORS["gray"],
        )


def _draw_axis_arrows(ax: Axes) -> None:
    arrow_color = FIXERS_COLORS["spine"]
    spine_lw = mpl.rcParams["axes.linewidth"]
    props = dict(
        arrowstyle="-|>",
        color=arrow_color,
        linewidth=spine_lw,
        mutation_scale=10,
        shrinkA=0,
        shrinkB=0,
    )
    ax.annotate("", xy=(0, 1.05), xytext=(0, 0.99), xycoords="axes fraction", arrowprops=props)
    ax.annotate("", xy=(1.05, 0), xytext=(0.99, 0), xycoords="axes fraction", arrowprops=props)


def _add_y_top_margin(ax: Axes, frac: float = 0.06, y_max: float | None = None) -> None:
    y0, y1 = ax.get_ylim()
    new_top = y1 + (y1 - y0) * frac
    if y_max is not None:
        new_top = min(new_top, y_max)
    ax.set_ylim(y0, new_top)


def _coerce_series(values: Iterable, kind: str) -> np.ndarray:
    if kind == "datetime":
        return pd.to_datetime(list(values)).to_numpy()
    return np.asarray(list(values), dtype=float)


def _format_date_axis(ax: Axes, fmt: str) -> None:
    if fmt == "'yy.mm":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("'%y.%m"))
    elif fmt == "mm.dd":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m.%d"))
    elif fmt == "'yy":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("'%y"))
    elif fmt == "yyyy":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(MaxNLocator(nbins=8))


def make_line_chart(
    data: pd.DataFrame,
    *,
    x_col: str,
    y_cols: Sequence[str],
    title: str,
    save_path: Path,
    subtitle: str | None = None,
    y_unit: str | None = None,
    x_label: str | None = None,
    legend_labels: Sequence[str] | None = None,
    accent_index: int | None = None,
    x_kind: str = "numeric",
    date_format: str = "'yy.mm",
    y_log: bool = False,
    y_max: float | None = None,
    y_min: float | None = None,
    figsize: tuple[float, float] = (8.0, 4.5),
) -> Path:
    apply_style()
    fig, ax = plt.subplots(figsize=figsize)

    x = _coerce_series(data[x_col], x_kind)
    labels = list(legend_labels) if legend_labels else list(y_cols)

    for i, col in enumerate(y_cols):
        color = ACCENT if i == accent_index else SERIES_PALETTE[i % len(SERIES_PALETTE)]
        ax.plot(x, data[col].astype(float).to_numpy(), color=color, linewidth=1.5, label=labels[i])

    _draw_title(ax, title, subtitle)
    _draw_unit_label(ax, y_unit)
    if y_log:
        ax.set_yscale("log")
        ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
        ax.yaxis.set_major_formatter(FuncFormatter(_plain_number_formatter))
        ax.yaxis.set_minor_locator(LogLocator(base=10, subs=tuple(np.arange(2, 10) * 0.1), numticks=12))
        ax.yaxis.set_minor_formatter(NullFormatter())
    else:
        _format_axis(ax, y_unit)
    if x_kind == "datetime":
        _format_date_axis(ax, date_format)
    else:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=8))
    _draw_x_label(ax, x_label)
    ax.set_ylabel("")
    ax.margins(x=0.02)
    if not y_log:
        auto_cap: float | None = None
        if y_max is None and y_unit and y_unit.lower() in {"%", "pct", "percent"}:
            try:
                stacked = np.concatenate([data[c].astype(float).to_numpy() for c in y_cols])
                if float(np.nanmax(stacked)) <= 1.0:
                    auto_cap = 1.0
            except (TypeError, ValueError):
                pass
        _add_y_top_margin(ax, y_max=y_max if y_max is not None else auto_cap)
        if y_min is not None:
            _, top = ax.get_ylim()
            ax.set_ylim(y_min, top)

    if len(y_cols) > 1:
        legend_y = -0.20 if x_label else -0.08
        leg = ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, legend_y),
            ncol=min(len(y_cols), 4),
            frameon=False,
        )
        for text in leg.get_texts():
            text.set_color(FIXERS_COLORS["text_dark"])

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)
    return save_path


def make_bar_chart(
    data: pd.DataFrame,
    *,
    x_col: str,
    y_col: str,
    title: str,
    save_path: Path,
    subtitle: str | None = None,
    y_unit: str | None = None,
    x_label: str | None = None,
    accent_mask: Sequence[bool] | None = None,
    xaxis_at_zero: bool = False,
    xtick_rotation: float = 0.0,
    value_labels: bool = False,
    y_max: float | None = None,
    figsize: tuple[float, float] = (8.0, 4.5),
) -> Path:
    apply_style()
    fig, ax = plt.subplots(figsize=figsize)

    x_labels = [str(v) for v in data[x_col].tolist()]
    values = data[y_col].astype(float).to_numpy()
    colors = [
        ACCENT if (accent_mask is not None and accent_mask[i]) else FIXERS_COLORS["navy"]
        for i in range(len(values))
    ]

    bars = ax.bar(x_labels, values, color=colors, width=0.65)

    _draw_title(ax, title, subtitle)
    _draw_unit_label(ax, y_unit)
    _format_axis(ax, y_unit)
    _draw_x_label(ax, x_label)
    ax.set_ylabel("")
    if xaxis_at_zero:
        ax.spines["bottom"].set_visible(False)
        ax.axhline(0, color=FIXERS_COLORS["spine"], linewidth=mpl.rcParams["axes.linewidth"], zorder=0)
    plt.setp(ax.get_xticklabels(), rotation=xtick_rotation, ha="right" if xtick_rotation else "center")

    auto_cap: float | None = None
    if y_unit and y_unit.lower() in {"%", "pct", "percent"} and float(np.nanmax(values)) <= 1.0:
        auto_cap = 1.0
    _add_y_top_margin(ax, y_max=y_max if y_max is not None else auto_cap)

    if value_labels:
        unit_norm = (y_unit or "").lower()
        for bar, val in zip(bars, values):
            if unit_norm in {"%", "pct", "percent"}:
                pct = val * 100
                label = f"{pct:.1f}%" if abs(pct - round(pct)) > 1e-9 else f"{int(round(pct))}%"
            else:
                label = f"{val:.2f}" if abs(val - round(val)) > 1e-9 else f"{int(round(val))}"
            height = bar.get_height()
            offset = 0.01 * (ax.get_ylim()[1] - ax.get_ylim()[0])
            if val >= 0:
                y_pos = height + offset
                va = "bottom"
            else:
                y_pos = height - offset
                va = "top"
            ax.text(
                bar.get_x() + bar.get_width() / 2, y_pos, label,
                ha="center", va=va,
                fontsize=10, fontweight="bold",
                color=FIXERS_COLORS["text_axis"],
            )

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path)
    plt.close(fig)
    return save_path
