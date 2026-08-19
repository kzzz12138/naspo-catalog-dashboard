import os
import glob
import numpy as np
import pandas as pd

RAW_DIR = "data/raw"
OUT_PATH = "data/clean/catalog_clean.csv"

RENAME = {
    "Vendor": "vendor",
    "Description": "description",
    "Manufacturer Part Number": "mpn",
    "List Price": "list_price",
    "NASPO Price": "naspo_price",
}


def fix_part_number(value):
    if value is None:
        return np.nan

    if isinstance(value, float):
        if np.isnan(value):
            return np.nan
        if value.is_integer():
            return str(int(value))
        return str(value)

    if isinstance(value, int):
        return str(value)

    return str(value).replace("\xa0", " ").strip()


def remove_price_symbols(value):
    if isinstance(value, str):
        return value.replace("$", "").replace(",", "").strip()
    return value


def clean_price_column(series):
    price_without_symbols = series.apply(remove_price_symbols)
    price_numeric = pd.to_numeric(price_without_symbols, errors="coerce")
    lost = series[series.notna() & price_numeric.isna()]
    return price_numeric, lost


def clean_text(value):
    if value is None:
        return np.nan

    if isinstance(value, float) and np.isnan(value):
        return np.nan

    text = str(value).replace("\xa0", " ").strip()
    while "  " in text:
        text = text.replace("  ", " ")

    return text


def main():
    paths = sorted(
        glob.glob(os.path.join(RAW_DIR, "NASPO_Price_Catalog_*.xlsx")))

    parts = []
    for path in paths:
        df = pd.read_excel(path)
        df = df.rename(columns=RENAME)

        mpn_numeric = 0
        for value in df["mpn"]:
            if isinstance(value, (int, float)):
                mpn_numeric += 1

        price_strings = 0
        for column in ["list_price", "naspo_price"]:
            for value in df[column]:
                if isinstance(value, str):
                    price_strings += 1

        df["vendor"] = df["vendor"].map(clean_text)
        df["description"] = df["description"].map(clean_text)
        df["mpn"] = df["mpn"].map(fix_part_number)
        df["list_price"], lost_list = clean_price_column(df["list_price"])
        df["naspo_price"], lost_naspo = clean_price_column(df["naspo_price"])
        df["source_file"] = os.path.basename(path)

        # print lost
        for column_name, lost in [("list_price", lost_list),
                                  ("naspo_price", lost_naspo)]:
            for row_index, value in lost.items():
                print(f"unparseable {column_name} row {row_index}: "
                      f"{value!r} -> missing")

        parts.append(df)

    catalog = pd.concat(parts, ignore_index=True)

    length_before_drop = len(catalog)
    catalog = catalog.drop_duplicates()
    print(f"Duplicates dropped: {length_before_drop - len(catalog)}")

    catalog["duplicate_vendor_mpn"] \
        = catalog.duplicated(subset=["vendor", "mpn"], keep=False)
    catalog.to_csv(OUT_PATH, index=False)


if __name__ == "__main__":
    main()
