# Interaction diagnostics figures



if "interaction_block_summary" not in globals():



    raise RuntimeError("Run the interaction model block first.")







sns.set_theme(style="whitegrid", context="notebook")

def pretty_display_name(value):
    text = str(value)
    text = re.sub(r"^z_", "", text)
    text = text.replace("_x_", " x ").replace("__", " ").replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text.title()







# 1) CV R2 by block and outcome



plot_summary = interaction_block_summary.dropna(subset=["cv_r2_mean"]).copy()
plot_summary["outcome_label"] = plot_summary["outcome"].map(pretty_display_name)



if not plot_summary.empty:



    plt.figure(figsize=(11, 5.5))



    sns.barplot(



        data=plot_summary,



        x="outcome_label",



        y="cv_r2_mean",



        hue="model_block",



        errorbar=None,



    )



    plt.axhline(0.0, color="black", linestyle="--", linewidth=1)



    plt.title("Block-wise Model Fit (CV R2, Associational)")



    plt.xlabel("Outcome")



    plt.ylabel("Cross-validated R2")



    plt.xticks(rotation=20, ha="right")



    plt.tight_layout()



    plt.savefig(FIGURES_DIR / "interaction_block_cv_r2.png", dpi=300, bbox_inches="tight")



    plt.show()







# 2) Heatmap of interaction coefficients in the final block



if "interaction_block_coefs" in globals() and not interaction_block_coefs.empty:



    heat_df = interaction_block_coefs[



        interaction_block_coefs["model_block"].eq("block_3_plus_topic_interactions")



    ].copy()



    if not heat_df.empty:



        heat_pivot = heat_df.pivot_table(



            index="feature",



            columns="outcome",



            values="coef",



            aggfunc="mean",



        )



        heat_pivot = heat_pivot.dropna(how="all")



        if not heat_pivot.empty:



            # Keep the most informative interactions for readability.



            order = heat_pivot.abs().mean(axis=1).sort_values(ascending=False).head(12).index



            heat_pivot = heat_pivot.loc[order]
            heat_pivot = heat_pivot.copy()
            heat_pivot.index = [pretty_display_name(v) for v in heat_pivot.index]
            heat_pivot.columns = [pretty_display_name(v) for v in heat_pivot.columns]







            plt.figure(figsize=(11, max(5, 0.45 * len(heat_pivot))))



            sns.heatmap(heat_pivot, cmap="RdBu_r", center=0, linewidths=0.25)



            plt.title("Interaction Coefficients in Final Block (Associational)")



            plt.xlabel("Outcome")



            plt.ylabel("Interaction term")



            plt.tight_layout()



            plt.savefig(FIGURES_DIR / "interaction_coefficients_heatmap.png", dpi=300, bbox_inches="tight")



            plt.show()







# 3) Scatter diagnostics for top available interactions vs polarisation_score



if "polarisation_score" in analysis_df.columns and "interaction_creation_table" in globals():



    available_ints = interaction_creation_table.loc[



        interaction_creation_table["created"], "interaction"



    ].tolist()



    if available_ints:



        ranked = []



        for col in available_ints:



            pair = analysis_df[[col, "polarisation_score"]].copy()



            pair[col] = pd.to_numeric(pair[col], errors="coerce")



            pair["polarisation_score"] = pd.to_numeric(pair["polarisation_score"], errors="coerce")



            pair = pair.dropna()



            if len(pair) >= 20:



                corr = pair[col].corr(pair["polarisation_score"])



                ranked.append((col, abs(corr) if pd.notna(corr) else 0.0, len(pair)))







        top_interactions = [x[0] for x in sorted(ranked, key=lambda t: t[1], reverse=True)[:6]]



        if top_interactions:



            n = len(top_interactions)



            ncols = 2



            nrows = int(np.ceil(n / ncols))



            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12, 4.2 * nrows), squeeze=False)



            axes_flat = axes.flatten()



            for i, inter_col in enumerate(top_interactions):



                pair = analysis_df[[inter_col, "polarisation_score"]].copy()



                pair[inter_col] = pd.to_numeric(pair[inter_col], errors="coerce")



                pair["polarisation_score"] = pd.to_numeric(pair["polarisation_score"], errors="coerce")



                pair = pair.dropna()



                ax = axes_flat[i]



                sns.regplot(data=pair, x=inter_col, y="polarisation_score", scatter_kws={"alpha": 0.6, "s": 24}, line_kws={"color": "#1f77b4"}, ax=ax)



                ax.set_title(f"{pretty_display_name(inter_col)} vs {pretty_display_name('polarisation_score')}")



                ax.set_xlabel(pretty_display_name(inter_col))



                ax.set_ylabel(pretty_display_name("polarisation_score"))



            for j in range(n, len(axes_flat)):



                axes_flat[j].axis("off")



            fig.suptitle("Interaction Diagnostics (Associational Scatter)", y=1.01)



            fig.tight_layout()



            fig.savefig(FIGURES_DIR / "interaction_scatter_diagnostics.png", dpi=300, bbox_inches="tight")



            plt.show()







print("Saved figures: interaction_block_cv_r2.png, interaction_coefficients_heatmap.png, interaction_scatter_diagnostics.png")