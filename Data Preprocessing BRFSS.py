import pandas as pd

# 1) Load raw file
df = pd.read_csv(
    "data/raw/CDC BRFSS Age-Adjusted Prevalence Data (2011 to present)/BRFSS__Age-Adjusted_Prevalence_Data__2011_to_present__20250806.csv",
    low_memory=False
)

# 2) Resolve column names case-insensitively
cols = {c.lower(): c for c in df.columns}
year_col = cols.get("year")
if year_col is None:
    raise ValueError("Couldn't find a 'Year' column in the BRFSS file.")

loc_col = cols.get("locationdesc", "LocationDesc" if "LocationDesc" in df.columns else None)
if loc_col is None:
    raise ValueError("Couldn't find 'LocationDesc' column for state names.")

# 3) Filter years + states
US_STATES = [
    "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
    "Delaware","District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois",
    "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts",
    "Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
    "New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota",
    "Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota",
    "Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"
]
df = df[df[year_col].between(2017, 2021) & df[loc_col].isin(US_STATES)]

# Save filtered copy
df.to_csv("data/raw_filtered/CDC_BRFSS_2017_2021_filtered.csv", index=False)

# 4) Keep only useful columns that exist
keep_cols = [
    year_col, "LocationAbbr", loc_col, "Class", "Topic", "Question", "Response",
    "Break_Out", "Break_Out_Category", "Sample_Size", "Data_Value", "Data_Value_Unit",
    "Data_Value_Type", "Low_Confidence_Limit", "High_Confidence_Limit",
    "Confidence_limit_Low", "Confidence_limit_High", "DataSource", "Data_Source"
]
keep_cols_present = [c for c in keep_cols if c in df.columns]
df = df[keep_cols_present].copy()

# 5) Rename to consistent names
rename_map = {
    year_col: "Year",
    "LocationAbbr": "StateAbbr",
    loc_col: "State",
    "Break_Out": "Breakout",
    "Break_Out_Category": "Breakout_Category",
    "Data_Source": "Data_Source",
    "DataSource": "Data_Source",
    "Low_Confidence_Limit": "CI_Lower",
    "High_Confidence_Limit": "CI_Upper",
    "Confidence_limit_Low": "CI_Lower",
    "Confidence_limit_High": "CI_Upper",
}
df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

# 6) Clean text + numerics
for c in df.select_dtypes(include="object").columns:
    df[c] = df[c].astype(str).str.strip()

for c in ["Data_Value", "CI_Lower", "CI_Upper", "Sample_Size", "Year"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Drop rows with no Data_Value
if "Data_Value" in df.columns:
    df = df.dropna(subset=["Data_Value"])

# 7) Save cleaned outputs
df.to_csv("data/preprocessed/CDC_BRFSS_Cleaned_2017_2021.csv", index=False)
df.to_csv("data/merged/CDC_BRFSS_2017_2021_Final.csv", index=False)

print("✅ BRFSS processed: saved to preprocessed and merged.")
print(df.head(3))
