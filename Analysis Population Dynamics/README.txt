MEP Project - Folder Structure and Workflow

Purpose
This project builds an end-to-end pipeline from raw parliamentary speech data to final descriptive and regression analysis outputs on polarisation and demographic context.

Recommended run order
1) 1 Speeches
2) 2 MEP List
3) 3 Wikipedia
4) 4 LDA Topic Analysis
5) 5 LLM Wikipedia analysis
6) 6 Country level variables
7) 7 Final Analysis

Folder-by-folder guide

1 Speeches
	- What it contains:
		raw and/or preprocessed speech texts plus the matching Python scripts. Note 		that these are in a ZIP folder and need to be unzipped first.
	- Output role:
		this is the core text input for all downstream modelling.

2 MEP List
	- What it contains:
		the Excel list of MEPs and baseline characteristics. Note that these are in 		a ZIP folder and need to be unzipped first.
	- Output role:
		this is the master reference table for identity and merge consistency.

3 Wikipedia
	- What it does:
		collects and repairs Wikipedia information for MEPs (native-language pages and English pages where available).
	- Main substeps:
		1) Generate candidate page names/URLs from the MEP reference table.
		2) Scrape biography content and metadata fields.
		3) Run fallback/repair logic where page titles or links fail.
		4) Save consolidated text/metadata files for later extraction.
	- Output role:
		creates the raw biographical corpus used by LLM extraction.

4 LDA Topic Analysis
	- What it does:
		models speech content into interpretable topic structure and related measures.
	- Main substeps:
		1) Prepare text features from the cleaned speeches.
		2) Fit topic model(s) and inspect coherence/interpretability.
		3) Assign dominant topic and/or topic shares per unit.
		4) Build intermediate topic/polarisation-oriented tables for joins.
	- Output role:
		provides topic-based explanatory and descriptive variables used later in the final analysis.

5 LLM Wikipedia analysis
	- What it does:
		extracts structured person-level variables from Wikipedia biographies using LLM prompts.
	- Main substeps:
		1) Load scraped Wikipedia text and prepare prompt/input batches.
		2) Extract standardized fields (background, education, experience, etc.).
		3) Run quality checks and matching diagnostics against the MEP list.
		4) Apply manual corrections for known edge cases (for example country irregularities).
		5) Save the final hand-in file:
		 	extracted_polarisation_final_manually_improved_1906.xlsx
	- Output role:
		delivers the main enriched MEP-level dataset for modelling.

6 Country level variables
	- What it does:
		builds the country-year context panel (mostly Eurostat-based indicators).
	- Main substeps:
		1) Pull/assemble demographic and macro indicators by country and year.
		2) Standardize country codes and time coverage.
		3) Clean types, handle missingness, and generate analysis-ready variables.
		4) Save country-year table(s) used in the merge with MEP-level records.
	- Output role:
		provides the contextual controls for cross-country analysis.

7 Final Analysis
	- What it does:
		combines all prepared inputs into the final analytical workflow.
	- Main substeps:
		1) Load MEP-level enriched file (folder 5) and country-year controls (folder 6).
		2) Harmonize country/group labels and perform merge diagnostics.
		3) Build cleaned analysis dataframe (flags, grouped variables, standardized categories).
		4) Run descriptive outputs (tables, distributions, heatmaps, profile plots).
		5) Run association/regression blocks and interaction screening.
		6) Export final tables and figures for thesis/reporting.
	- Output role:
		produces the submission-ready analytical results and visual material.

Outputs convention
- Each analysis folder is structured to save outputs in local outputs/tables and outputs/figures subfolders.
- This keeps reruns reproducible and avoids scattering result files across notebooks.

Notes
- Keep path setup cells at the top of notebooks and run notebooks top-to-bottom.
- API-dependent steps (LLM calls, external endpoints) should be run only when credentials and connectivity are available.
- If files are locked (for example by Excel), use fallback file names already provided in the notebooks.
