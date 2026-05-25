from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def _apply_style(config: dict[str, Any]) -> None:
    plt.rcParams.update(
        {
            "figure.dpi": config["visualization"]["dpi"],
            "savefig.dpi": config["visualization"]["dpi"],
            "font.size": config["visualization"]["font_size"],
            "axes.titlesize": config["visualization"]["font_size"] + 2,
            "axes.labelsize": config["visualization"]["font_size"],
        }
    )
    sns.set_theme(style="whitegrid", context="notebook")


def save_topic_year_heatmap(
    prevalence_df: pd.DataFrame,
    topic_labels: dict[str, str],
    output_path: Path,
    title: str,
    config: dict[str, Any],
    xlabel: str = "Year",
    ylabel: str = "Topic",
) -> None:
    _apply_style(config)
    matrix = prevalence_df.pivot(index="period", columns="topic", values="prevalence").fillna(0.0)
    matrix = matrix.sort_index()
    renamed = {col: topic_labels.get(col, col) for col in matrix.columns}
    matrix = matrix.rename(columns=renamed)

    # matrix.T: rows=topics, cols=periods (years). Width scales with years;
    # height follows a fixed aspect ratio so all journals render at similar size in LaTeX.
    n_periods = len(matrix.index)
    n_topics = len(matrix.columns)
    width = max(5.5, 0.18 * n_periods + 2.0)
    height = width * 0.48
    fig, ax = plt.subplots(figsize=(width, height))
    sns.heatmap(
        matrix.T,
        cmap=config["visualization"]["cmap_heatmap"],
        ax=ax,
        cbar_kws={"label": "Normalized topic prevalence", "location": "bottom", "shrink": 0.55, "pad": 0.02},
        linewidths=0.2,
        linecolor="#f0f0f0",
    )
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    fig.savefig(output_path, format=config["visualization"]["fig_format"], bbox_inches="tight")
    plt.close(fig)


def save_topic_year_lineplot(
    prevalence_df: pd.DataFrame,
    topic_labels: dict[str, str],
    output_path: Path,
    title: str,
    config: dict[str, Any],
) -> None:
    _apply_style(config)
    fig, ax = plt.subplots(figsize=(11, 6))
    for topic in sorted(prevalence_df["topic"].unique()):
        frame = prevalence_df[prevalence_df["topic"] == topic].copy()
        frame["period_num"] = frame["period"].astype(int)
        frame = frame.sort_values("period_num")
        label = topic_labels.get(topic, topic)
        ax.plot(
            frame["period_num"],
            frame["prevalence"],
            linewidth=config["visualization"]["line_width"],
            label=label[:40],
        )

    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel("Normalized topic prevalence")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, format=config["visualization"]["fig_format"], bbox_inches="tight")
    plt.close(fig)


def save_topic_month_heatmap(
    prevalence_df: pd.DataFrame,
    topic_labels: dict[str, str],
    output_path: Path,
    title: str,
    config: dict[str, Any],
) -> None:
    _apply_style(config)
    matrix = prevalence_df.pivot(index="period", columns="topic", values="prevalence").fillna(0.0)
    matrix = matrix.sort_index()
    renamed = {col: topic_labels.get(col, col) for col in matrix.columns}
    matrix = matrix.rename(columns=renamed)

    plot_matrix = matrix.T
    n_periods = plot_matrix.shape[1]
    n_topics = plot_matrix.shape[0]
    width = max(5.5, 0.18 * n_periods + 2.0)
    height = width * 0.48
    fig, ax = plt.subplots(figsize=(width, height))
    sns.heatmap(
        plot_matrix,
        cmap=config["visualization"]["cmap_heatmap"],
        ax=ax,
        cbar_kws={"label": "Normalized topic prevalence", "location": "bottom", "shrink": 0.55, "pad": 0.02},
        linewidths=0.0,
    )
    ax.set_title(title)
    ax.set_xlabel("Year-Month")
    ax.set_ylabel("Topic")
    fig.tight_layout()
    fig.savefig(output_path, format=config["visualization"]["fig_format"], bbox_inches="tight")
    plt.close(fig)


def save_similarity_clustermap(
    similarity_df: pd.DataFrame,
    output_path: Path,
    title: str,
    config: dict[str, Any],
    metric_label: str,
) -> None:
    _apply_style(config)
    n = len(similarity_df.index)
    size = max(9, 0.5 * n + 2.5)
    font_size = config["visualization"]["font_size"]
    title_fs = font_size + 2
    cg = sns.clustermap(
        similarity_df,
        cmap=config["visualization"]["cmap_similarity"],
        figsize=(size * 1.18, size * 1.06),
        linewidths=0.4,
        annot=False,
        cbar=False,
        xticklabels=True,
        yticklabels=True,
        dendrogram_ratio=0.12,
    )
    for ax in list(cg.fig.axes):
        if ax in (cg.ax_heatmap, cg.ax_col_dendrogram, cg.ax_row_dendrogram):
            continue
        if not ax.collections and not ax.lines and not ax.images and not ax.patches:
            ax.remove()
    cg.ax_heatmap.set_xticklabels(
        cg.ax_heatmap.get_xticklabels(),
        rotation=90,
        ha="right",
        va="top",
        fontsize=font_size,
    )
    cg.ax_heatmap.set_yticklabels(
        cg.ax_heatmap.get_yticklabels(),
        rotation=0,
        ha="left",
        va="center",
        fontsize=font_size,
    )
    cg.ax_heatmap.tick_params(axis="both", labelsize=font_size, pad=2)
    # Vertical colorbar at bottom-left, shifted right to clear the row dendrogram.
    cbar_ax = cg.fig.add_axes([0.08, 0.045, 0.018, 0.20])
    colorbar = cg.fig.colorbar(
        cg.ax_heatmap.collections[0],
        cax=cbar_ax,
        orientation="vertical",
    )
    colorbar.set_label(metric_label, fontsize=font_size, labelpad=4)
    colorbar.ax.tick_params(labelsize=font_size, length=3, pad=2)
    cg.fig.subplots_adjust(left=0.10, right=0.80, top=0.90, bottom=0.24)
    cg.fig.suptitle(title, y=0.98, fontsize=title_fs)
    cg.savefig(
        output_path,
        format=config["visualization"]["fig_format"],
        dpi=config["visualization"]["dpi"],
        bbox_inches="tight",
        pad_inches=0.14,
    )
    plt.close(cg.fig)


def save_specialization_barplot(
    specialization: pd.Series,
    output_path: Path,
    title: str,
    config: dict[str, Any],
) -> None:
    _apply_style(config)
    ordered = specialization.sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10, max(5, 0.35 * len(ordered) + 1.5)))
    ax.barh(ordered.index, ordered.values, color="#4C72B0")
    ax.set_title(title)
    ax.set_xlabel("Specialization index (KL divergence from global profile)")
    fig.tight_layout()
    fig.savefig(output_path, format=config["visualization"]["fig_format"], bbox_inches="tight")
    plt.close(fig)


def save_distinctive_heatmap(
    distinctive_df: pd.DataFrame,
    output_path: Path,
    title: str,
    config: dict[str, Any],
) -> None:
    _apply_style(config)
    if distinctive_df.empty:
        return

    matrix = distinctive_df.pivot_table(
        index="journal",
        columns="topic_label",
        values="zscore",
        aggfunc="max",
        fill_value=0.0,
    )
    size = max(8, 0.45 * len(matrix.index) + 2)
    fig, ax = plt.subplots(figsize=(max(10, 0.5 * len(matrix.columns) + 3), size))
    sns.heatmap(
        matrix,
        cmap="Reds",
        ax=ax,
        cbar_kws={"label": "Distinctiveness z-score"},
        linewidths=0.2,
    )
    ax.set_title(title)
    ax.set_xlabel("Journal")
    ax.set_ylabel("Topic label")
    fig.tight_layout()
    fig.savefig(output_path, format=config["visualization"]["fig_format"], bbox_inches="tight")
    plt.close(fig)


def save_temporal_divergence_barplot(
    divergence_df: pd.DataFrame,
    output_path: Path,
    title: str,
    config: dict[str, Any],
) -> None:
    _apply_style(config)
    if divergence_df.empty:
        return

    ordered = divergence_df.sort_values("temporal_jsd", ascending=True)
    fig, ax = plt.subplots(figsize=(10, max(5, 0.35 * len(ordered) + 1.5)))
    ax.barh(ordered["journal"], ordered["temporal_jsd"], color="#DD8452")
    ax.set_title(title)
    ax.set_xlabel("Temporal JSD (early vs late period)")
    fig.tight_layout()
    fig.savefig(output_path, format=config["visualization"]["fig_format"], bbox_inches="tight")
    plt.close(fig)
