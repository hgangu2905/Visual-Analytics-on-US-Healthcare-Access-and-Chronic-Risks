import pandas as pd
import os

# Ensure both folders exist
os.makedirs('./data/processed', exist_ok=True)
os.makedirs('./data/merged', exist_ok=True)

# File map for 2017–2021 CMS #2 files
file_map = {
    2017: 'MUP_IHP_RY23_P03_V10_DY17_GEO.CSV',
    2018: 'MUP_IHP_RY23_P03_V10_DY18_GEO.CSV',
    2019: 'MUP_IHP_RY23_P03_V10_DY19_GEO.CSV',
    2020: 'MUP_IHP_RY23_P03_V10_DY20_GEO.CSV',
    2021: 'MUP_IHP_RY23_P03_V10_DY21_GEO.CSV'
}

# Store cleaned DataFrames
cleaned_dfs = []

for year, filename in file_map.items():
    print(f"\n📂 Processing {year}...")

    file_path = f'data/raw_filtered/{filename}'
    df = pd.read_csv(file_path)

    # Filter to state-level data
    df = df[df['Rndrng_Prvdr_Geo_Lvl'] == 'State']

    # Select and rename relevant columns
    df = df[[
        'Rndrng_Prvdr_Geo_Desc',
        'DRG_Cd',
        'DRG_Desc',
        'Tot_Dschrgs',
        'Avg_Submtd_Cvrd_Chrg',
        'Avg_Tot_Pymt_Amt',
        'Avg_Mdcr_Pymt_Amt'
    ]].rename(columns={
        'Rndrng_Prvdr_Geo_Desc': 'State',
        'DRG_Cd': 'DRG_Code',
        'DRG_Desc': 'DRG_Description',
        'Tot_Dschrgs': 'Total_Discharges',
        'Avg_Submtd_Cvrd_Chrg': 'Avg_Charge_Submitted',
        'Avg_Tot_Pymt_Amt': 'Avg_Total_Payment',
        'Avg_Mdcr_Pymt_Amt': 'Avg_Medicare_Payment'
    })

    # Add Year column
    df['Year'] = year

    # Sort
    df = df.sort_values(by=['State', 'DRG_Code'])

    # Save per-year cleaned file
    out_path = f'data/preprocessed/CMS_Inpatient_Cleaned_{year}.csv'
    df.to_csv(out_path, index=False)
    print(f"✅ Saved cleaned file: {out_path}")

    # Collect for merging
    cleaned_dfs.append(df)

# Merge and save final file
merged_df = pd.concat(cleaned_dfs)
merged_path = 'data/merged/CMS_Inpatient_2017_2021_Final.csv'
merged_df.to_csv(merged_path, index=False)

print("\n🎉 All years merged successfully.")
print(f"✅ Final merged file saved to: {merged_path}")
print(f"📊 Final shape: {merged_df.shape}")
