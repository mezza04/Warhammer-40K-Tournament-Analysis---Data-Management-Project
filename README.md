# Warhammer 40K Tournament Analysis
### Does Army Cost Impact Competitive Performance?

Data management and analysis project on the **Warhammer 40,000 World Championship 2025** (Atlanta, GA). Tournament results for 402 players are collected via REST API, integrated with retail miniature prices, stored in a relational SQLite database and analysed to find out whether money buys victory.

Developed for the Data Management course, MSc in Data Science, **University of Milano-Bicocca**.
Full methodology and results are available in the project report.

## Research Questions

- **Economic impact:** does army cost influence results? Is a high budget needed to reach the top tier?
- **Meta analysis:** do popular factions perform better? Does detachment choice matter?
- **Unit analysis:** do indispensable units exist? Do elite armies beat horde armies?
- **Faction dynamics:** is there a "rock-paper-scissors" dynamic between factions?

## Key Findings

- Army cost has a weak but statistically significant positive correlation with performance (cost vs. wins: r = 0.131, p = 0.0086).
- Top 25 and bottom 25 players spent statistically the same amount (p = 0.3082): reaching the elite level does not require a bigger budget.
- Faction popularity is unrelated to win rate (r = 0.0007), while detachment choice is a key strategic factor within a faction.
- No global advantage for elite or horde lists; only 3 of 40 faction matchups are significant hard counters.

**Warhammer 40,000 is not pay-to-win:** money gives a marginal advantage, but success is driven mainly by player skill, strategy and preparation.

## Data Sources

| Dataset | Source | Availability |
|---|---|---|
| Tournament data | [ListEngine](https://listengine-v3-be.onrender.com) REST API (JSON) | Processed files included |
| Pricing data | Official price list provided by **ArsManufactorea** (XLSX, November 2025) | Private, not included |

## Repository Structure

```
.
├── README.md
|
├── DM_project__warhammer_40k.pdf       # Report
│
├── 1_Data Aquisition/
│   ├── API_acquisition.py              # Extracts raw tournament data from the ListEngine API
│   ├── parser.py                       # First parsing of the raw JSON
│   ├── reparser.py                     # Second parsing pass for failed lists
│   ├── merger.py                       # Merges parsed lists with manually compiled ones
│   ├── validator.py                    # Validation helpers used across the pipeline
│   └── warhammer_manual_lists.json     # 19 manually compiled army lists
│
├── 2_Data Integration/
│   ├── Input/
│   │   ├── warhammer_final_cleaned.json
│   │   └── warhammer_final_valid.json
│   ├── cleaner.py                      # Final cleaning and standardisation
│   ├── Warhammer_SQL.py                # Creates and loads the SQLite database
│   └── warhammer_tournaments.db        # Final relational database
│
├── 3_Data Quality/
│   └── data_quality_assessment.ipynb   # Data quality metrics before/after integration
│
└── 4_Data Analysis/
    └── warhammer_analysis.ipynb        # EDA, statistical tests and visualisations
```

## Pipeline

`API_acquisition.py` → `parser.py` → `reparser.py` → `merger.py` → `cleaner.py` → `Warhammer_SQL.py` → `data_quality_assessment.ipynb` → `warhammer_analysis.ipynb`

## Limitations

- Single tournament (November 2025 meta), so results may not generalise.
- Army costs are estimates from a rule-based price-scaling function, not actual player spending.
- Small samples in matchup and detachment analyses limit statistical significance.

## Authors

- **Chiara Mezzanzanica:** data acquisition and parsing pipeline
- **Ilaria Cesaratto:** data cleaning, integration and database
- **Andrea Porro:** statistical analysis and interpretation

*Warhammer 40,000 is a trademark of Games Workshop. This is an independent academic project, not affiliated with or endorsed by Games Workshop.*
