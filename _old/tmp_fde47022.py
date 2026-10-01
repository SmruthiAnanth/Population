



# --- Correlation visualization ---















FIGURE_OUTPUT_DIR = globals().get("FIGURE_OUTPUT_DIR", PROJECT_ROOT / "8 Final regression" / "figures")







FIGURE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)















def _compact_fig_name(filename):



    stem = Path(filename).stem.lower()



    stem = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")



    token_map = {



        "descriptive": "desc", "polarisation": "pol", "correlation": "corr",



        "random": "rf", "forest": "rf", "association": "assoc", "strength": "str",



        "feature": "feat", "importance": "imp", "cluster": "cl", "country": "cty",



        "topic": "tp", "group": "grp", "party": "pty", "profile": "prof",



        "interaction": "int", "interactions": "ints", "composition": "comp",



        "prevalence": "prev", "outcome": "out", "outcomes": "outs",



        "distribution": "dist", "distributions": "dists", "heatmap": "hm",



        "scatter": "scat", "ranking": "rank", "silhouette": "sil",



        "high": "hi", "low": "lo", "absolute": "abs", "professional": "prof",



        "background": "bg",



    }



    parts = [token_map.get(p, p[:4]) for p in stem.split("_") if p]



    compact = "_".join(parts)



    compact = (compact[:48].rstrip("_") or "fig")



    return f"{compact}.png"







def save_figure(filename):



    plt.savefig(FIGURE_OUTPUT_DIR / _compact_fig_name(filename), dpi=300, bbox_inches="tight")















if "correlation_table" not in globals():







    raise RuntimeError("Please run the correlation table cell first.")















sns.set_theme(style="whitegrid", context="notebook")

def pretty_display_name(value):

    text = str(value)

    text = re.sub(r"^z_", "", text)

    text = text.replace("_x_", " x ").replace("__", " ").replace("_", " ")

    text = re.sub(r"\s+", " ", text).strip()

    return text.title()















# Pivot the long-form table into an outcome-by-predictor matrix.







correlation_heatmap_df = correlation_table.pivot_table(







    index="predictor",







    columns="outcome",







    values="correlation",







    aggfunc="mean",







)















# Keep the strongest overall correlations for readability.







if not correlation_heatmap_df.empty:







    top_n = min(20, len(correlation_heatmap_df))







    strongest_predictors = correlation_heatmap_df.abs().mean(axis=1).sort_values(ascending=False).head(top_n).index







    correlation_heatmap_df = correlation_heatmap_df.loc[strongest_predictors]

    correlation_heatmap_df = correlation_heatmap_df.copy()

    correlation_heatmap_df.index = [pretty_display_name(v) for v in correlation_heatmap_df.index]

    correlation_heatmap_df.columns = [pretty_display_name(v) for v in correlation_heatmap_df.columns]















    plt.figure(figsize=(10, max(6, 0.35 * len(correlation_heatmap_df))))







    sns.heatmap(







        correlation_heatmap_df,







        cmap="RdBu_r",







        center=0,







        linewidths=0.3,







        cbar_kws={"label": "Pearson correlation"},







    )







    plt.title("Correlation Heatmap: Outcomes vs Direct / Topic / Interaction Variables")







    plt.xlabel("Outcome")







    plt.ylabel("Predictor")







    plt.tight_layout()







    save_figure("correlation_heatmap.png")







    plt.show()















# Also show a compact bar chart of the strongest absolute correlations.







plot_df = correlation_table.head(25).copy()







if not plot_df.empty:







    plot_df["outcome_label"] = plot_df["outcome"].map(pretty_display_name)

    plot_df["label"] = plot_df["predictor"].map(pretty_display_name) + " (" + plot_df["outcome_label"] + ")"







    plot_df = plot_df.sort_values("abs_correlation", ascending=True)















    plt.figure(figsize=(12, max(6, 0.35 * len(plot_df))))







    sns.barplot(data=plot_df, x="correlation", y="label", hue="outcome_label", dodge=False)







    plt.title("Top Absolute Correlations")







    plt.xlabel("Pearson correlation")







    plt.ylabel("Predictor / Outcome pair")







    plt.legend(title="Outcome", loc="lower right")







    plt.tight_layout()







    save_figure("correlation_top_absolute_bars.png")







    plt.show()