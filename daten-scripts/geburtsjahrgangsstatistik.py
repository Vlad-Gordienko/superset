import pandas as pd
import os
import datetime

FILENAME = "geburtsjahrgangsstatistik.xlsx"
INPUT_DIR = "data"
OUTPUT_DIR = "dist"
SHEET_NAME = "dadigesamt"

INPUT_FILENAME = os.path.join(INPUT_DIR, FILENAME)
OUTPUT_FILENAME = os.path.join(OUTPUT_DIR, FILENAME)

gemeinde_schluessel = {
    "Wetteraukreis": (6440, 0),
    "Altenstadt": (6440001, 1),
    "Bad Nauheim, Stadt": (6440002, 2),
    "Bad Vilbel, Stadt": (6440003, 3),
    "Büdingen, Stadt": (6440004, 4),
    "Butzbach, Friedrich-Ludwig-Weidig-Stadt": (6440005, 5),
    "Echzell": (6440006, 6),
    "Florstadt, Stadt": (6440007, 7),
    "Friedberg (Hessen), Kreisstadt": (6440008, 8),
    "Gedern, Stadt": (6440009, 9),
    "Glauburg": (6440010, 10),
    "Hirzenhain": (6440011, 11),
    "Karben, Stadt": (6440012, 12),
    "Kefenrod": (6440013, 13),
    "Limeshain": (6440014, 14),
    "Münzenberg, Stadt": (6440015, 15),
    "Nidda, Stadt": (6440016, 16),
    "Niddatal, Stadt": (6440017, 17),
    "Ober-Mörlen": (6440018, 18),
    "Ortenberg, Stadt": (6440019, 19),
    "Ranstadt": (6440020, 20),
    "Reichelsheim (Wetterau), Stadt": (6440021, 21),
    "Rockenberg": (6440022, 22),
    "Rosbach v. d. Höhe, Stadt": (6440023, 23),
    "Wölfersheim": (6440024, 24),
    "Wöllstadt": (6440025, 25),
}

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
        df = df.dropna(subset=["Gebiet", "Jahrgang"])
        df["Gebiet"] = df["Gebiet"].str.strip()

        df["Jahrgang"] = pd.to_numeric(df["Jahrgang"], errors='coerce')
        df = df.dropna(subset=["Jahrgang"])
        df["Jahrgang"] = df["Jahrgang"].astype(int)

        columns_to_keep = ["Gebiet", "Jahrgang", "M gesamt", "W gesamt", "EW gesamt"]
        missing_columns = [col for col in columns_to_keep if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing columns {missing_columns}")
            return

        df = df[columns_to_keep]

        for col in ["M gesamt", "W gesamt", "EW gesamt"]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        current_year = datetime.datetime.now().year

        def classify_age_group(year):
            age = current_year - year
            if age < 21:
              return "Unter 21 Jährige"
            elif age > 64:
               return "65 Jahre und älter"
            return "21 Jahre - 65 Jahre"

        df["Gruppe"] = df["Jahrgang"].apply(classify_age_group)
        grouped_df = df.groupby(["Gebiet", "Gruppe"])[["M gesamt", "W gesamt", "EW gesamt"]].sum().reset_index()

        total_population = df.groupby("Gebiet")[["M gesamt", "W gesamt", "EW gesamt"]].sum().reset_index()
        total_population = total_population.rename(columns={
            "M gesamt": "M total", "W gesamt": "W total", "EW gesamt": "EW total"
        })

        grouped_df = grouped_df.merge(total_population, on="Gebiet", how="left")

        grouped_df.insert(1, "Amtlicher Gemeinde-schlüssel", grouped_df["Gebiet"].map(lambda x: gemeinde_schluessel.get(x, ("", ""))[0]))
        grouped_df.insert(2, "ISO", grouped_df["Gebiet"].map(lambda x: gemeinde_schluessel.get(x, ("", ""))[1]))

        grouped_df["M quotient"] = (grouped_df["M gesamt"] / grouped_df["M total"] * 100).round(2).astype(str) + "%"
        grouped_df["W quotient"] = (grouped_df["W gesamt"] / grouped_df["W total"] * 100).round(2).astype(str) + "%"
        grouped_df["EW quotient"] = (grouped_df["EW gesamt"] / grouped_df["EW total"] * 100).round(2).astype(str) + "%"

        if not os.access(OUTPUT_DIR, os.W_OK):
            print(f"Error: No write permission for directory {OUTPUT_DIR}")
            return

        grouped_df.to_excel(OUTPUT_FILENAME, index=False)
        print(f"Result saved to {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    parse_excel()
