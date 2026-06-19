# MEP Polarisation and Population Dynamics Pipeline

This repository contains an end-to-end notebook pipeline from parliamentary speeches to final descriptive and regression analysis on MEP polarisation and demographic-country context.

## Project Structure

- 1 Speeches
- 2 MEP List
- 3 Wikipedia
- 4 LDA Topic Analysis
- 5 LLM Wikipedia analysis
- 6 Country level variables
- 7 Final Analysis
- data
- src
- outputs

## Data Flow

```text
Speeches + MEP list
        ↓
Wikipedia scraping
        ↓
LLM biography extraction
        ↓
LDA speech topics + polarisation score
        ↓
Country-year controls
        ↓
Final regression analysis
```

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

   pip install -r requirements.txt

3. Create environment file from template:

   copy .env.example .env

4. Add API keys to .env when running LLM steps:
   - OPENAI_API_KEY
   - OPENROUTER_API_KEY

## Reproducibility Notes

- Notebooks are designed to run top-to-bottom from a fresh kernel.
- Shared paths and folder creation are centralized in src/config.py.
- Validation helpers are centralized in src/validation.py.
- Keep folder numbering exactly as listed above to avoid path mismatch.

## Run Order

1. 3 Wikipedia/Scraping_wikipedia.ipynb
2. 4 LDA Topic Analysis/LDA_Analysis.ipynb
3. 5 LLM Wikipedia analysis/Wikipedia_extracting_info.ipynb
4. 6 Country level variables/country_level_variables.ipynb
5. 7 Final Analysis/final_regression_analysis.ipynb

## Expected Inputs

- Speech files in 1 Speeches
- MEP master list in 2 MEP List
- Prior intermediate tables when re-running later stages

## Expected Outputs

- Wikipedia outputs in 3 Wikipedia outputs tables
- LDA and polarisation outputs in 4 LDA Topic Analysis outputs tables
- Final extraction file in 5 LLM Wikipedia analysis
- Country-year panel in 6 Country level variables
- Final tables and figures in outputs/tables and outputs/figures

## Important Operational Notes

- Some input folders may arrive zipped; unzip before execution.
- Do not commit API keys or private credentials.
- Do not commit large generated outputs or raw private data.
- If Excel files are open/locked, close them before export.

## Data Availability and Privacy

- This repository may reference data files that are not publicly distributable.
- Keep sensitive or restricted raw data outside version control.
- Share only derived, non-sensitive outputs when policy allows.

## GitHub Safety Checklist

- .env is ignored.
- outputs and caches are ignored.
- raw zipped files are ignored.
- absolute local paths have been replaced with project-relative configuration.
