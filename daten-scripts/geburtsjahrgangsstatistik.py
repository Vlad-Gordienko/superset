import pandas as pd
import os
import datetime

from common.gebiet_schluessel import gebiet_schluessel
from common.sorted_gebiet_to_gemeinde import sorted_gebiet_to_gemeinde

FILENAME = "geburtsjahrgangsstatistik.xlsx"
INPUT_DIR = "data"
OUTPUT_DIR = "dist"
SHEET_NAME = "dadigesamt"

INPUT_FILENAME = os.path.join(INPUT_DIR, FILENAME)
OUTPUT_FILENAME = os.path.join(OUTPUT_DIR, FILENAME)

def parse_excel():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(INPUT_FILENAME):
        print(f"Error: File {INPUT_FILENAME} not found.")
        return

    xls = pd.ExcelFile(INPUT_FILENAME)
    if SHEET_NAME not in xls.sheet_names:
        print(f"Error: Sheet '{SHEET_NAME}' not found. Available: {xls.sheet_names}")
        return

    df = pd.read_excel(xls, sheet_name=SHEET_NAME, dtype=str)
    df = df.dropna(subset=["Gebiet", "Jahrgang"])
    df["Gebiet"] = df["Gebiet"].str.strip()

    df["Jahrgang"] = pd.to_numeric(df["Jahrgang"], errors='coerce')
    df = df.dropna(subset=["Jahrgang"])
    df["Jahrgang"] = df["Jahrgang"].astype(int)

    df["Gemeinde"] = df["Gebiet"].map(lambda x: sorted_gebiet_to_gemeinde.get(x, x))

    if "EW gesamt" not in df.columns:
        print("Error: Column 'EW gesamt' not found.")
        return

    df["EW gesamt"] = pd.to_numeric(df["EW gesamt"], errors='coerce').fillna(0).astype(int)

    current_year = datetime.datetime.now().year

    def classify_group(year):
        age = current_year - year
        if age < 21:
            return "young"
        elif age > 64:
            return "elder"
        return "sonstige"

    df["gruppe"] = df["Jahrgang"].apply(classify_group)

    grouped_df = df.groupby(["Gemeinde", "gruppe"])["EW gesamt"].sum().reset_index()

    total_df = grouped_df.groupby("Gemeinde")["EW gesamt"].sum().reset_index()
    total_df = total_df.rename(columns={"EW gesamt": "EW total"})

    merged = grouped_df.merge(total_df, on="Gemeinde")
    merged["ew quotient"] = ((merged["EW gesamt"] / merged["EW total"]) * 100).round(2).astype(str) + "%"

    merged["amtlicher gemeindeschlüssel"] = merged["Gemeinde"].map(lambda x: gebiet_schluessel.get(x, ("", ""))[0])
    merged["iso"] = merged["Gemeinde"].map(lambda x: gebiet_schluessel.get(x, ("", ""))[1])

    final_df = merged.pivot_table(
        index=["Gemeinde", "amtlicher gemeindeschlüssel", "iso"],
        columns="gruppe",
        values="ew quotient",
        aggfunc="first"
    ).reset_index()

    final_df = final_df.rename(columns={
        "Gemeinde": "gemeinde",
        "amtlicher gemeindeschlüssel": "amtlicher gemeindeschlüssel",
        "iso": "iso",
        "young": "young quotient",
        "sonstige": "sonstige quotient",
        "elder": "elder quotient"
    })

    final_df = final_df[~final_df["gemeinde"].isin(["Ausgewählte Gebiete zusammengefasst", "Sanierungsgebiet"])]

    final_df.to_excel(OUTPUT_FILENAME, index=False)
    print(f"Result saved to {OUTPUT_FILENAME}")

if __name__ == "__main__":
    parse_excel()
