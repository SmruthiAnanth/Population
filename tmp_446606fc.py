# Exploratory interaction screening (separate from main analysis).



# This block is intentionally hypothesis-generating and correlational.











if "analysis_df" not in globals():



    raise RuntimeError("analysis_df is missing. Run the main pipeline cells first.")







TABLES_DIR = globals().get("TABLES_DIR", Path.cwd() / "outputs" / "tables")



FIGURES_DIR = globals().get("FIGURES_DIR", Path.cwd() / "outputs" / "figures")



TABLES_DIR.mkdir(parents=True, exist_ok=True)



FIGURES_DIR.mkdir(parents=True, exist_ok=True)







expl_df = analysis_df.copy()







# --- Topic aliases (keep original columns, add code-friendly duplicates) ---



topic_alias_map = {



    "Ageing & Pensions": "topic_ageing_pensions",



    "Fertility, Families & Gender": "topic_fertility_family_gender",



    "Health & Care Services": "topic_health_care_services",



    "Migration & Population Change": "topic_migration_population_change",



    "Population Growth & Sustainability": "topic_population_growth_sustainability",



    "Regional Depopulation & Territorial Cohesion": "topic_regional_depopulation",



    "Youth & Future Generations": "topic_youth_future_generations",



    "Borderline: Labour market and social policy": "topic_labour_market_social_policy",



    "Borderline: Youth / demographic future (weak signal)": "topic_youth_demographic_future_weak",



}







expl_warnings = []



for original_col, alias_col in topic_alias_map.items():



    if original_col in expl_df.columns:



        expl_df[alias_col] = pd.to_numeric(expl_df[original_col], errors="coerce")



    else:



        expl_warnings.append(f"Missing topic column skipped: {original_col}")







# --- Outcome variables (confidence intentionally excluded as a main outcome) ---



outcome_candidates = [



    "polarisation_score",



    "us_vs_them",



    "emotional_intensity",



    "moral_absolutism",



    "hostility_to_opponents",



]



detected_outcomes = [c for c in outcome_candidates if c in expl_df.columns]







if not detected_outcomes:



    raise RuntimeError("No requested outcome variables available for exploratory screening.")







# --- Family variable lists ---



family1_topics = [



    "topic_ageing_pensions",



    "topic_fertility_family_gender",



    "topic_health_care_services",



    "topic_migration_population_change",



    "topic_population_growth_sustainability",



    "topic_regional_depopulation",



    "topic_youth_future_generations",



    "topic_labour_market_social_policy",



    "topic_youth_demographic_future_weak",



]







family1_country = [



    "fertility_rate",



    "old_age_dependency_ratio",



    "median_age",



    "life_expectancy",



    "net_migration",



    "population_change",



    "debt_to_gdp",



    "employment_rate_55_64",



    "youth_unemployment",



    "age_started_receiving_old_age_pension",



    "labour_force_participation_55_64",



    "old_age_poverty_rate",



    "projected_old_age_dependency_ratio_2050",



    "foreign_born_population_share",



]







family2_mep = [



    "gender_bucket",



    "education_level_bucket",



    "education_field_clean",



    "professional_background_clean",



    "migration_background_flag",



    "international_experience_flag",



    "military_background_flag",



    "parental_status_known",



    "has_children_if_known",



    "religion_mentioned_flag",



    "prior_political_level_bucket",



    "demography_expertise_bucket",



]







family2_topics = [



    "topic_ageing_pensions",



    "topic_fertility_family_gender",



    "topic_health_care_services",



    "topic_migration_population_change",



    "topic_youth_future_generations",



    "topic_regional_depopulation",



]







family3_mep = [



    "gender_bucket",



    "education_level_bucket",



    "professional_background_clean",



    "migration_background_flag",



    "international_experience_flag",



    "has_children_if_known",



    "prior_political_level_bucket",



    "demography_expertise_bucket",



]







family3_country = [



    "fertility_rate",



    "old_age_dependency_ratio",



    "debt_to_gdp",



    "foreign_born_population_share",



    "net_migration",



    "employment_rate_55_64",



    "youth_unemployment",



    "old_age_poverty_rate",



]







# --- Helpers ---



def _safe_slug(text: str) -> str:



    text = str(text).strip().lower()



    text = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in text)



    while "__" in text:



        text = text.replace("__", "_")



    return text.strip("_") or "x"











def _to_binary_if_possible(series: pd.Series):



    s = series.copy()



    if pd.api.types.is_numeric_dtype(s):



        s_num = pd.to_numeric(s, errors="coerce")



        uniq = sorted([v for v in s_num.dropna().unique().tolist()])



        if len(uniq) == 2 and set(uniq).issubset({0, 1}):



            return s_num, True



        return s_num, False







    s_str = s.astype("string").str.strip().str.lower()



    map_dict = {



        "yes": 1, "y": 1, "true": 1, "1": 1,



        "no": 0, "n": 0, "false": 0, "0": 0,



    }



    mapped = s_str.map(map_dict)



    uniq = sorted([v for v in mapped.dropna().unique().tolist()])



    if len(uniq) == 2 and set(uniq).issubset({0, 1}):



        return mapped.astype(float), True



    return s, False











def _zscore(series: pd.Series) -> pd.Series:



    x = pd.to_numeric(series, errors="coerce")



    mu = x.mean(skipna=True)



    sd = x.std(skipna=True, ddof=0)



    if pd.isna(sd) or sd == 0:



        return x - mu



    return (x - mu) / sd











def _prepare_continuous_var(df: pd.DataFrame, col: str, missing_threshold: float = 0.75):



    if col not in df.columns:



        return None, f"missing column: {col}"



    x = pd.to_numeric(df[col], errors="coerce")



    miss = x.isna().mean()



    uniq = x.dropna().nunique()



    if miss > missing_threshold:



        return None, f"too much missingness ({miss:.2%}): {col}"



    if uniq < 2:



        return None, f"fewer than two unique values: {col}"



    z_col = f"z_{col}"



    df[z_col] = _zscore(x)



    return z_col, None











# Prepare standardized country/topic vars



continuous_candidates = sorted(set(family1_topics + family1_country + family3_country + [



    "n_relevant_speeches", "n_documents", "confidence"



]))







standardized_map = {}



for col in continuous_candidates:



    new_col, warn = _prepare_continuous_var(expl_df, col)



    if new_col is not None:



        standardized_map[col] = new_col



    elif warn is not None:



        expl_warnings.append(warn)







# Prepare MEP variables (binary keep; >2 categories to dummies, drop first)



mep_model_cols = {}



for mep_col in sorted(set(family2_mep + family3_mep)):



    if mep_col not in expl_df.columns:



        expl_warnings.append(f"missing MEP variable: {mep_col}")



        mep_model_cols[mep_col] = []



        continue







    raw = expl_df[mep_col]



    maybe_bin, is_binary = _to_binary_if_possible(raw)



    if is_binary:



        model_col = f"mep_{mep_col}"



        expl_df[model_col] = pd.to_numeric(maybe_bin, errors="coerce")



        if expl_df[model_col].dropna().nunique() >= 2:



            mep_model_cols[mep_col] = [model_col]



        else:



            mep_model_cols[mep_col] = []



            expl_warnings.append(f"binary MEP variable has <2 unique values: {mep_col}")



        continue







    cat = raw.astype("string").str.strip()



    cat = cat.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})



    nunique = cat.dropna().nunique()



    if nunique < 2:



        mep_model_cols[mep_col] = []



        expl_warnings.append(f"categorical MEP variable has <2 unique values: {mep_col}")



        continue







    dummies = pd.get_dummies(cat, prefix=f"mep_{mep_col}", drop_first=True, dtype=float)



    if dummies.shape[1] == 0:



        mep_model_cols[mep_col] = []



        expl_warnings.append(f"no dummies created (drop_first) for: {mep_col}")



        continue







    expl_df = pd.concat([expl_df, dummies], axis=1)



    mep_model_cols[mep_col] = dummies.columns.tolist()







# Controls (continuous standardized controls, plus optional confidence)



control_cols = [c for c in [



    standardized_map.get("n_relevant_speeches"),



    standardized_map.get("n_documents"),



    standardized_map.get("confidence"),



] if c is not None]







# Optional fixed effects columns



fe_candidates = [c for c in ["country_clean_final", "ep_group_clean"] if c in expl_df.columns]











# --- Regression engine ---



def _fit_single_interaction(



    df: pd.DataFrame,



    outcome: str,



    x1_col: str,



    x2_col: str,



    interaction_family: str,



    var1_label: str,



    var2_label: str,



    min_n: int = 35,



):



    warning_msgs = []







    use_cols = [outcome, x1_col, x2_col] + control_cols + fe_candidates



    work = df[use_cols].copy()



    work[outcome] = pd.to_numeric(work[outcome], errors="coerce")







    # Ensure x terms are numeric where possible.



    work[x1_col] = pd.to_numeric(work[x1_col], errors="coerce")



    work[x2_col] = pd.to_numeric(work[x2_col], errors="coerce")







    # FE kept as categorical strings.



    for fe_col in fe_candidates:



        work[fe_col] = work[fe_col].astype("string").str.strip()



        work[fe_col] = work[fe_col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})







    work = work.dropna(subset=[outcome, x1_col, x2_col] + control_cols)







    if work.shape[0] < min_n:



        return {



            "outcome_variable": outcome,



            "interaction_family": interaction_family,



            "variable_1": var1_label,



            "variable_2": var2_label,



            "interaction_name": f"{var1_label} x {var2_label}",



            "coefficient": np.nan,



            "standard_error": np.nan,



            "p_value": np.nan,



            "ci_lower": np.nan,



            "ci_upper": np.nan,



            "n_observations": int(work.shape[0]),



            "adjusted_r2": np.nan,



            "model_status": "skipped",



            "warning": f"too few observations (<{min_n})",



        }







    X = work[[x1_col, x2_col] + control_cols].copy()



    inter_col = f"int__{_safe_slug(x1_col)}__{_safe_slug(x2_col)}"



    X[inter_col] = X[x1_col] * X[x2_col]







    # Optional FE if stable (enough rows per dummy burden)



    fe_used = []



    if fe_candidates:



        fe_dummies_all = []



        for fe_col in fe_candidates:



            valid_fe = work[fe_col].dropna().nunique()



            if valid_fe >= 2:



                d = pd.get_dummies(work[fe_col], prefix=f"fe_{fe_col}", drop_first=True, dtype=float)



                if d.shape[1] > 0:



                    fe_dummies_all.append(d)



        if fe_dummies_all:



            fe_mat = pd.concat(fe_dummies_all, axis=1)



            prospective_k = X.shape[1] + fe_mat.shape[1] + 1



            if work.shape[0] >= max(45, 4 * prospective_k):



                X = pd.concat([X, fe_mat], axis=1)



                fe_used = fe_mat.columns.tolist()



            else:



                warning_msgs.append("fixed effects skipped due limited sample size")







    # Final complete-case matrix



    model_df = pd.concat([work[[outcome]], X], axis=1).dropna()



    n_obs = int(model_df.shape[0])







    if n_obs < min_n:



        return {



            "outcome_variable": outcome,



            "interaction_family": interaction_family,



            "variable_1": var1_label,



            "variable_2": var2_label,



            "interaction_name": f"{var1_label} x {var2_label}",



            "coefficient": np.nan,



            "standard_error": np.nan,



            "p_value": np.nan,



            "ci_lower": np.nan,



            "ci_upper": np.nan,



            "n_observations": n_obs,



            "adjusted_r2": np.nan,



            "model_status": "skipped",



            "warning": "too few complete cases after controls/FE",



        }







    y = model_df[outcome]



    X_model = sm.add_constant(model_df.drop(columns=[outcome]), has_constant="add")







    try:



        fit = sm.OLS(y, X_model).fit(cov_type="HC3")



        if inter_col not in fit.params.index:



            return {



                "outcome_variable": outcome,



                "interaction_family": interaction_family,



                "variable_1": var1_label,



                "variable_2": var2_label,



                "interaction_name": f"{var1_label} x {var2_label}",



                "coefficient": np.nan,



                "standard_error": np.nan,



                "p_value": np.nan,



                "ci_lower": np.nan,



                "ci_upper": np.nan,



                "n_observations": n_obs,



                "adjusted_r2": float(fit.rsquared_adj) if np.isfinite(fit.rsquared_adj) else np.nan,



                "model_status": "error",



                "warning": "interaction term dropped/singular",



            }







        ci = fit.conf_int().loc[inter_col]



        if fe_used:



            warning_msgs.append("fixed effects included")







        return {



            "outcome_variable": outcome,



            "interaction_family": interaction_family,



            "variable_1": var1_label,



            "variable_2": var2_label,



            "interaction_name": f"{var1_label} x {var2_label}",



            "coefficient": float(fit.params[inter_col]),



            "standard_error": float(fit.bse[inter_col]),



            "p_value": float(fit.pvalues[inter_col]),



            "ci_lower": float(ci.iloc[0]),



            "ci_upper": float(ci.iloc[1]),



            "n_observations": n_obs,



            "adjusted_r2": float(fit.rsquared_adj) if np.isfinite(fit.rsquared_adj) else np.nan,



            "model_status": "ok",



            "warning": " | ".join(warning_msgs) if warning_msgs else "",



        }



    except Exception as ex:



        return {



            "outcome_variable": outcome,



            "interaction_family": interaction_family,



            "variable_1": var1_label,



            "variable_2": var2_label,



            "interaction_name": f"{var1_label} x {var2_label}",



            "coefficient": np.nan,



            "standard_error": np.nan,



            "p_value": np.nan,



            "ci_lower": np.nan,



            "ci_upper": np.nan,



            "n_observations": n_obs,



            "adjusted_r2": np.nan,



            "model_status": "error",



            "warning": f"model error: {str(ex)[:180]}",



        }











# --- Build interaction attempts ---



attempt_specs = []







# Family 1: topic x country



for t in family1_topics:



    t_col = standardized_map.get(t)



    if t_col is None:



        continue



    for c in family1_country:



        c_col = standardized_map.get(c)



        if c_col is None:



            continue



        attempt_specs.append(("topic_x_country", t, c, t_col, c_col))







# Family 2: mep background x topic



for m in family2_mep:



    m_cols = mep_model_cols.get(m, [])



    if not m_cols:



        continue



    for t in family2_topics:



        t_col = standardized_map.get(t)



        if t_col is None:



            continue



        for mc in m_cols:



            attempt_specs.append(("mep_x_topic", mc, t, mc, t_col))







# Family 3: mep background x country



for m in family3_mep:



    m_cols = mep_model_cols.get(m, [])



    if not m_cols:



        continue



    for c in family3_country:



        c_col = standardized_map.get(c)



        if c_col is None:



            continue



        for mc in m_cols:



            attempt_specs.append(("mep_x_country", mc, c, mc, c_col))







# --- Run all models (one interaction per model per outcome) ---



rows = []



for out in detected_outcomes:



    for fam, v1_label, v2_label, x1_col, x2_col in attempt_specs:



        rows.append(_fit_single_interaction(



            df=expl_df,



            outcome=out,



            x1_col=x1_col,



            x2_col=x2_col,



            interaction_family=fam,



            var1_label=v1_label,



            var2_label=v2_label,



        ))







results_df = pd.DataFrame(rows)







# Multiple-testing diagnostics



results_df["raw_significant_5pct"] = results_df["p_value"].lt(0.05)



results_df["p_value_fdr"] = np.nan



results_df["fdr_significant_10pct"] = False







mask_ok = results_df["p_value"].notna() & results_df["model_status"].eq("ok")



if mask_ok.any():



    _, p_adj, _, _ = multipletests(results_df.loc[mask_ok, "p_value"].values, alpha=0.10, method="fdr_bh")



    results_df.loc[mask_ok, "p_value_fdr"] = p_adj



    results_df.loc[mask_ok, "fdr_significant_10pct"] = results_df.loc[mask_ok, "p_value_fdr"].lt(0.10)







results_df["exploratory_only"] = True







# Signed interaction score: sign(coef) * -log10(p)



safe_p = pd.to_numeric(results_df["p_value"], errors="coerce").clip(lower=1e-300)



results_df["signed_score"] = np.sign(pd.to_numeric(results_df["coefficient"], errors="coerce")) * (-np.log10(safe_p))



results_df.loc[results_df["coefficient"].isna() | results_df["p_value"].isna(), "signed_score"] = np.nan







# Save full results



all_outcomes_path = TABLES_DIR / "exploratory_interaction_screening_all_outcomes.csv"



results_df.to_csv(all_outcomes_path, index=False)







# --- Heatmaps ---



sns.set_theme(style="white", context="notebook")







figure_paths = []

def pretty_display_name(value):
    text = str(value)
    text = re.sub(r"^z_", "", text)
    text = text.replace("_x_", " x ").replace("__", " ").replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text.title()











def _save_heatmap(df_sub, rows_order, cols_order, title, out_path):



    if df_sub.empty:



        return False



    piv = df_sub.pivot_table(index="variable_1", columns="variable_2", values="signed_score", aggfunc="mean")



    # Keep intended order where present



    r_keep = [r for r in rows_order if r in piv.index]



    c_keep = [c for c in cols_order if c in piv.columns]



    if not r_keep or not c_keep:



        return False



    piv = piv.loc[r_keep, c_keep]

    piv = piv.copy()
    piv.index = [pretty_display_name(v) for v in piv.index]
    piv.columns = [pretty_display_name(v) for v in piv.columns]



    if piv.dropna(how="all").empty:



        return False







    plt.figure(figsize=(max(8, 0.55 * len(c_keep)), max(5, 0.45 * len(r_keep))))



    sns.heatmap(piv, cmap="RdBu_r", center=0, linewidths=0.25)



    plt.title(title)



    plt.xlabel("Variable 2")



    plt.ylabel("Variable 1")



    plt.xticks(rotation=40, ha="right")



    plt.tight_layout()



    plt.savefig(out_path, dpi=300, bbox_inches="tight")



    plt.show()



    figure_paths.append(str(out_path))



    return True











# Compact outcome slugs



outcome_short = {



    "polarisation_score": "pol",



    "us_vs_them": "uvt",



    "emotional_intensity": "emo",



    "moral_absolutism": "mor",



    "hostility_to_opponents": "hos",



}







# Family 1 heatmaps



for out in detected_outcomes:



    sub = results_df[(results_df["outcome_variable"] == out) & (results_df["interaction_family"] == "topic_x_country") & (results_df["model_status"] == "ok")]



    fname = f"expl_hm_tc_{outcome_short.get(out, _safe_slug(out)[:4])}.png"



    _save_heatmap(



        sub,



        rows_order=family1_topics,



        cols_order=family1_country,



        title=f"Exploratory Topic x Country Interactions: {pretty_display_name(out)}",



        out_path=FIGURES_DIR / fname,



    )







# Family 2 heatmaps (rows may be dummies)



fam2_rows = sorted(results_df.loc[results_df["interaction_family"].eq("mep_x_topic"), "variable_1"].dropna().unique().tolist())



for out in detected_outcomes:



    sub = results_df[(results_df["outcome_variable"] == out) & (results_df["interaction_family"] == "mep_x_topic") & (results_df["model_status"] == "ok")]



    fname = f"expl_hm_mt_{outcome_short.get(out, _safe_slug(out)[:4])}.png"



    _save_heatmap(



        sub,



        rows_order=fam2_rows,



        cols_order=family2_topics,



        title=f"Exploratory MEP x Topic Interactions: {pretty_display_name(out)}",



        out_path=FIGURES_DIR / fname,



    )







# Family 3 heatmaps (rows may be dummies)



fam3_rows = sorted(results_df.loc[results_df["interaction_family"].eq("mep_x_country"), "variable_1"].dropna().unique().tolist())



for out in detected_outcomes:



    sub = results_df[(results_df["outcome_variable"] == out) & (results_df["interaction_family"] == "mep_x_country") & (results_df["model_status"] == "ok")]



    fname = f"expl_hm_mc_{outcome_short.get(out, _safe_slug(out)[:4])}.png"



    _save_heatmap(



        sub,



        rows_order=fam3_rows,



        cols_order=family3_country,



        title=f"Exploratory MEP x Country Interactions: {pretty_display_name(out)}",



        out_path=FIGURES_DIR / fname,



    )







# Outcome-comparison heatmap (top 20 by absolute signed_score across outcomes)



ok_scores = results_df[results_df["model_status"].eq("ok")].copy()



if not ok_scores.empty:



    agg = ok_scores.groupby("interaction_name", as_index=False)["signed_score"].apply(lambda s: np.nanmax(np.abs(s.values)) if s.notna().any() else np.nan)



    agg = agg.rename(columns={"signed_score": "max_abs_signed_score"}).sort_values("max_abs_signed_score", ascending=False)



    top20_names = agg["interaction_name"].head(20).tolist()







    top_by_outcome = ok_scores[ok_scores["interaction_name"].isin(top20_names)].copy()



    top_by_outcome_tbl = top_by_outcome[[



        "interaction_family", "interaction_name", "outcome_variable", "coefficient", "p_value", "p_value_fdr", "signed_score", "n_observations"



    ]].sort_values(["interaction_name", "outcome_variable"])



    top_by_outcome_path = TABLES_DIR / "exploratory_top_interactions_by_outcome.csv"



    top_by_outcome_tbl.to_csv(top_by_outcome_path, index=False)







    piv = top_by_outcome.pivot_table(index="interaction_name", columns="outcome_variable", values="signed_score", aggfunc="mean")



    # Keep top20 order and present outcomes



    keep_rows = [r for r in top20_names if r in piv.index]



    keep_cols = [c for c in detected_outcomes if c in piv.columns]



    if keep_rows and keep_cols:



        piv = piv.loc[keep_rows, keep_cols]

        piv = piv.copy()
        piv.index = [pretty_display_name(v) for v in piv.index]
        piv.columns = [pretty_display_name(v) for v in piv.columns]



        plt.figure(figsize=(max(8, 1.2 * len(keep_cols)), max(6, 0.35 * len(keep_rows))))



        sns.heatmap(piv, cmap="RdBu_r", center=0, linewidths=0.25)



        plt.title("Exploratory Top Interactions by Outcome")



        plt.xlabel("Outcome")



        plt.ylabel("Interaction")



        plt.tight_layout()



        top_hm_path = FIGURES_DIR / "expl_hm_top_by_out.png"



        plt.savefig(top_hm_path, dpi=300, bbox_inches="tight")



        plt.show()



        figure_paths.append(str(top_hm_path))



else:



    top_by_outcome_tbl = pd.DataFrame(columns=[



        "interaction_family", "interaction_name", "outcome_variable", "coefficient", "p_value", "p_value_fdr", "signed_score", "n_observations"



    ])



    top_by_outcome_path = TABLES_DIR / "exploratory_top_interactions_by_outcome.csv"



    top_by_outcome_tbl.to_csv(top_by_outcome_path, index=False)







# Ranked top interactions table with prioritisation



priority_pairs = [



    "topic_ageing_pensions x old_age_dependency_ratio",



    "topic_ageing_pensions x age_started_receiving_old_age_pension",



    "topic_ageing_pensions x projected_old_age_dependency_ratio_2050",



    "topic_migration_population_change x foreign_born_population_share",



    "topic_migration_population_change x net_migration",



    "topic_fertility_family_gender x fertility_rate",



    "topic_youth_future_generations x youth_unemployment",



    "mep_migration_background_flag x topic_migration_population_change",



    "mep_has_children_if_known x topic_fertility_family_gender",



    "demography_expertise_bucket x topic_ageing_pensions",



]







ranked = results_df[results_df["model_status"].eq("ok")].copy()



ranked["priority_flag"] = ranked["interaction_name"].isin(priority_pairs)



ranked = ranked.sort_values(["priority_flag", "signed_score"], ascending=[False, False])



ranked = ranked[[



    "interaction_family",



    "interaction_name",



    "outcome_variable",



    "coefficient",



    "p_value",



    "p_value_fdr",



    "signed_score",



    "n_observations",



]].head(120)



ranked["interpretation_note"] = "Exploratory, correlational interaction signal; not causal evidence."







ranked_path = TABLES_DIR / "exploratory_top_interactions_ranked.csv"



ranked.to_csv(ranked_path, index=False)







# Store summary objects for final print cell



exploratory_summary = {



    "detected_outcomes": detected_outcomes,



    "n_attempted_models": int(len(rows)),



    "n_successful_models": int(results_df["model_status"].eq("ok").sum()),



    "n_skipped_models": int(results_df["model_status"].isin(["skipped", "error"]).sum()),



    "tables_saved": [



        str(all_outcomes_path),



        str(top_by_outcome_path),



        str(ranked_path),



    ],



    "figures_saved": figure_paths,



    "warnings": expl_warnings,



}







# Display small diagnostics previews



print("Exploratory screening complete (hypothesis-generating only).")



print("Detected outcomes:", detected_outcomes)



print("Attempted models:", exploratory_summary["n_attempted_models"])



print("Successful models:", exploratory_summary["n_successful_models"])



print("Skipped/error models:", exploratory_summary["n_skipped_models"])







if expl_warnings:



    print("\nWarnings (first 20):")



    for w in expl_warnings[:20]:



        print("-", w)







display(results_df.head(10))



display(ranked.head(15))