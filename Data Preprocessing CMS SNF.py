# Process CMS MDCR SNF 3 (State-level) for 2017–2021 and merge
# -------------------------------------------------------------

import pandas as pd
from pathlib import Path

US_STATES = [
    "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
    "Delaware","District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois",
    "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts",
    "Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
    "New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota",
    "Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina",
    "South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington",
    "West Virginia","Wisconsin","Wyoming"
]

def dedup_columns(cols):
    out, seen = [], {}
    for i, c in enumerate(cols):
        c = "" if c is None else str(c)
        c = c.strip()
        if c.lower() in ("", "nan", "none"):
            c = f"col_{i}"
        if c in seen:
            out.append(f"{c}_{seen[c]}")
            seen[c] += 1
        else:
            out.append(c); seen[c] = 1
    return out

def find_header_row(raw, first_data_idx, lookback=8, min_non_null=4):
    top = max(first_data_idx - 1 - lookback, 0)
    for r in range(first_data_idx - 1, top - 1, -1):
        if raw.iloc[r].notna().sum() >= min_non_null:
            return r
    return max(first_data_idx - 1, 0)

def infer_header_and_data_start(raw_df):
    col0 = raw_df.iloc[:, 0].astype(str).str.strip()
    keys = set(US_STATES + ["All Areas", "United States"])
    idxs = col0[col0.isin(keys)].index.tolist()
    if not idxs:
        raise ValueError("Couldn't find first data row (no state/US key found in column 0).")
    data_start = idxs[0]
    header_row = find_header_row(raw_df, data_start)
    return header_row, data_start

def clean_numeric_columns(df, non_numeric=("State", "Year")):
    for c in df.columns:
        if c in non_numeric:
            continue
        if pd.api.types.is_object_dtype(df[c]):
            ser = (df[c].astype(str)
                      .str.replace(r'[\$,]', '', regex=True)
                      .str.replace('%', '', regex=True)
                      .str.strip())
            df[c] = pd.to_numeric(ser, errors="coerce")
    return df

def process_snf_one_year(file_path, year, sheet_name="MDCR SNF 3",
                         out_dir="data/preprocessed"):
    raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    header_row, data_start = infer_header_and_data_start(raw)

    cols = dedup_columns(raw.iloc[header_row].tolist())
    df = raw.iloc[data_start:].copy()
    df.columns = cols

    first_col = df.columns[0]
    df = df.rename(columns={first_col: "State"})
    df["State"] = df["State"].astype(str).str.strip()

    df = df[df["State"].isin(US_STATES)].copy()
    df["Year"] = int(year)
    df = clean_numeric_columns(df)

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(out_dir) / f"CMS_SNF3_Cleaned_{year}.csv"
    df.to_csv(out_path, index=False)
    print(f"✅ Saved {year}: {out_path} (shape={df.shape})")
    return df

# ---------- Run for 2017–2021 and merge ----------
raw_dir = Path("data/raw_filtered")
years = [2017, 2018, 2019, 2020, 2021]
frames = []

for y in years:
    fp = raw_dir / f"CPS MDCR SNF 3 {y}.XLSX"
    if not fp.exists():
        print(f"⚠️  Skipping {y}: file not found -> {fp}")
        continue
    try:
        frames.append(process_snf_one_year(str(fp), y, sheet_name="MDCR SNF 3"))
    except Exception as e:
        print(f"❌ Failed {y}: {e}")

if frames:
    merged = pd.concat(frames, ignore_index=True)
    merged_path = Path("data/merged") / "CMS_SNF3_2017_2021_Final.csv"
    merged.to_csv(merged_path, index=False)
    print(f"\n🎉 Merged saved: {merged_path} (shape={merged.shape})")
else:
    print("No yearly files processed; nothing to merge.")
