import pandas as pd
from pathlib import Path

# === US States List ===
US_STATES = [
    "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
    "Delaware","District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois",
    "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts",
    "Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
    "New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota",
    "Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota",
    "Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"
]

RAW_FILTERED_DIR = Path("data/raw_filtered")
PREPROCESSED_DIR = Path("data/preprocessed")
MERGED_DIR = Path("data/merged")

PREPROCESSED_DIR.mkdir(exist_ok=True)
MERGED_DIR.mkdir(exist_ok=True)

def read_kff(file_path: Path) -> pd.DataFrame:
    """
    Read a KFF CSV where the first 2 rows are metadata, the 3rd row is the header.
    Falls back to header auto-detect if needed.
    """
    # First attempt: skip first 2 rows and treat the next row as header
    try:
        df = pd.read_csv(
            file_path,
            engine="python",   # robust parser
            sep=None,          # auto-detect delimiter
            skiprows=2,        # <-- skip metadata rows
            header=0,
            encoding="utf-8",
            on_bad_lines="skip"
        )
    except Exception:
        # Fallback: read a few lines to detect header row
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        header_idx = None
        header_markers_any = ["Location", "State", "Location Name", "location", "state"]
        other_cols_any = [
            "Employer", "Uninsured", "Medicaid", "Medicare",
            "Non-Group", "Military", "Total", "Other Public", "Other Private"
        ]
        for i, line in enumerate(lines[:50]):
            if any(m in line for m in header_markers_any) and any(m in line for m in other_cols_any):
                header_idx = i
                break
        if header_idx is None:
            for i, line in enumerate(lines[:50]):
                if any(m in line for m in header_markers_any):
                    header_idx = i
                    break
        if header_idx is None:
            raise ValueError(f"Couldn't find a header row in {file_path}")

        df = pd.read_csv(
            file_path,
            engine="python",
            sep=None,
            header=header_idx,
            encoding="utf-8",
            on_bad_lines="skip"
        )

    # Identify the state column
    state_col = None
    for cand in ["Location", "State", "Location Name", "location", "state"]:
        if cand in df.columns:
            state_col = cand
            break
    if state_col is None:
        raise ValueError(f"No State/Location column in {file_path.name}")

    # Normalize
    df[state_col] = df[state_col].astype(str).str.strip()

    # Keep only US states
    df = df[df[state_col].isin(US_STATES)].copy()

    # Columns likely present with percentages or counts
    likely_numeric = [
        "Employer", "Non-Group", "Medicaid", "Medicare", "Military",
        "Uninsured", "Total", "Other Public", "Other Private"
    ]
    keep_cols = [state_col] + [c for c in likely_numeric if c in df.columns]
    df = df[keep_cols].copy()

    # Clean numeric columns (remove %, $, commas, spaces)
    for c in df.columns:
        if c == state_col:
            continue
        df[c] = (
            df[c].astype(str)
                .str.replace(r"[,\$%]", "", regex=True)
                .str.strip()
        )
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.rename(columns={state_col: "State"})
    return df

# === Process each year (2017, 2018, 2019, 2021 available) ===
all_years_data = {}
for year in [2017, 2018, 2019, 2021]:
    fp = RAW_FILTERED_DIR / f"KFF Insurance by State Population {year}.csv"
    print(f"📥 Loading {year}: {fp}")
    df = read_kff(fp)
    df["Year"] = year
    out_path = PREPROCESSED_DIR / f"KFF_Insurance_Cleaned_{year}.csv"
    df.to_csv(out_path, index=False)
    print(f"✅ Saved: {out_path} (shape={df.shape})")
    all_years_data[year] = df

# === Impute 2020 from average(2019, 2021) ===
if 2019 in all_years_data and 2021 in all_years_data:
    print("🛠 Imputing 2020 values from average of 2019 and 2021...")
    df_2019 = all_years_data[2019].set_index("State")
    df_2021 = all_years_data[2021].set_index("State")

    # Align on states intersection just in case
    common_states = df_2019.index.intersection(df_2021.index)
    df_2019 = df_2019.loc[common_states]
    df_2021 = df_2021.loc[common_states]

    df_2020 = df_2019.copy()
    numeric_cols = df_2019.select_dtypes(include=["number"]).columns
    df_2020[numeric_cols] = (df_2019[numeric_cols] + df_2021[numeric_cols]) / 2
    df_2020["Year"] = 2020
    df_2020 = df_2020.reset_index()

    out_path = PREPROCESSED_DIR / "KFF_Insurance_Cleaned_2020_Imputed.csv"
    df_2020.to_csv(out_path, index=False)
    print(f"✅ Saved: {out_path} (shape={df_2020.shape})")
    all_years_data[2020] = df_2020
else:
    print("⚠️ Cannot impute 2020 because 2019 and/or 2021 are missing.")

# === Merge all available years ===
merged_df = pd.concat(all_years_data[yr] for yr in sorted(all_years_data)).reset_index(drop=True)
merged_out_path = MERGED_DIR / "KFF_Insurance_2017_2021_Final.csv"
merged_df.to_csv(merged_out_path, index=False)
print(f"🎉 Merged saved: {merged_out_path} (shape={merged_df.shape})")
print("\n🔎 Merged preview:")
print(merged_df.head(10))
