import pandas as pd
import os
import datetime

FILENAME = "geburtsjahrgangsstatistik.xlsx"
INPUT_DIR = "data"
OUTPUT_DIR = "dist"
SHEET_NAME = "dadigesamt"

INPUT_FILENAME = os.path.join(INPUT_DIR, FILENAME)
OUTPUT_FILENAME = os.path.join(OUTPUT_DIR, FILENAME)

def parse_excel():
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if not os.path.exists(INPUT_FILENAME):
            print(f"Error: File {INPUT_FILENAME} not found.")
            return

        xls = pd.ExcelFile(INPUT_FILENAME)

        if SHEET_NAME not in xls.sheet_names:
            print(f"Error: Sheet '{SHEET_NAME}' not found in the file. Available sheets: {xls.sheet_names}")
            return

        df = pd.read_excel(xls, sheet_name=SHEET_NAME, dtype=str)

        columns_to_keep = ["Gebiet", "Jahrgang", "M gesamt", "W gesamt", "EW gesamt"]
        missing_columns = [col for col in columns_to_keep if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing columns {missing_columns}")
            return

        df = df[columns_to_keep]

        df["Jahrgang"] = pd.to_numeric(df["Jahrgang"], errors='coerce')
        df = df.dropna(subset=["Jahrgang"])
        df["Jahrgang"] = df["Jahrgang"].astype(int)

        for col in ["M gesamt", "W gesamt", "EW gesamt"]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        df["M quotient"] = ""
        df["W quotient"] = ""
        df["EW quotient"] = ""

        invalid_rows = df[df[["M gesamt", "W gesamt", "EW gesamt"]].map(lambda x: not str(x).isdigit()).any(axis=1)]

        if not invalid_rows.empty:
            print("Warning: Found rows with invalid numerical values:")
            print(invalid_rows)

        current_year = datetime.datetime.now().year

        def classify_age_group(year):
            age = current_year - year
            if age < 18:
                return "Jugend"
            elif age > 65:
                return "Alten"

        df["Gruppe"] = df["Jahrgang"].apply(classify_age_group)

        grouped_df = df.groupby(["Gebiet", "Gruppe"])[["M gesamt", "W gesamt", "EW gesamt"]].sum().reset_index()

        grouped_df["M quotient"] = ""
        grouped_df["W quotient"] = ""
        grouped_df["EW quotient"] = ""

        if not os.access(OUTPUT_DIR, os.W_OK):
            print(f"Error: No write permission for directory {OUTPUT_DIR}")
            return

        grouped_df.to_excel(OUTPUT_FILENAME, index=False)
        print(f"Result saved to {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    parse_excel()
