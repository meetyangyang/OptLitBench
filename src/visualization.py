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
) -> None:
    _apply_style(config)
    matrix = prevalence_df.pivot(index="period", columns="topic", values="prevalence").fillna(0.0)
    matrix = matrix.sort_index()
    renamed = {col: topic_labels.get(col, col) for col in matrix.columns}
    matrix = matrix.rename(columns=renamed)

    height = max(4.5, 0.35 * len(matrix.index) + 2.5)
    width = max(8.0, 0.55 * len(matrix.columns) + 3.0)
    fig, ax = plt.subplots(figsize=(width, height))
    sns.heatmap(
        matrix.T,
        cmap=config["visualization"]["cmap_heatmap"],
        ax=ax,
        cbar_kws={"label": "Normalized topic prevalence"},
        linewidths=0.2,
        linecolor="#f0f0f0",
    )
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel("Topic")
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

    height = max(5.0, 0.18 * len(matrix.index) + 3.0)
    width = max(10.0, 0.55 * len(matrix.columns) + 3.0)
    fig, ax = plt.subplots(figsize=(width, height))
    sns.heatmap(
        matrix.T,
        cmap=config["visualization"]["cmap_heatmap"],
        ax=ax,
        cbar_kws={"label": "Normalized topic prevalence"},
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
    size = max(8, 0.45 * len(similarity_df.index) + 2)
    cg = sns.clustermap(
        similarity_df,
        cmap=config["visualization"]["cmap_similarity"],
        figsize=(size, size),
        linewidths=0.4,
        annot=False,
        cbar_kws={"label": metric_label},
    )
    cg.fig.suptitle(title, y=1.02)
    cg.savefig(output_path, format=config["visualization"]["fig_format"], bbox_inches="tight")
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
