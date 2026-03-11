"""
Build a comprehensive condo unit inventory from all ACRIS document types.

Combines MAPS, CDEC, DEED, and all other doc types to find every known
condo unit (SC/MC property types) and produces a single table with
normalized addresses and source metadata.
"""

import mysql.connector
import pandas as pd
from collections import Counter
from config import DB_CONFIG
from normalize_addresses import normalize_streetname

# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

# Pull every legals row that references a condo unit, along with doc metadata
FETCH_QUERY = """
    SELECT l.borough, l.block, l.lot,
           l.streetnumber, l.streetname, l.unit, l.propertytype,
           m.doctype, m.docdate, m.documentid
    FROM real_property_legals l
    JOIN real_property_master m USING (documentid)
    WHERE l.propertytype IN ('SC', 'MC')
"""

CREATE_TABLE = """
    DROP TABLE IF EXISTS condo_units;
    CREATE TABLE condo_units (
        id INT AUTO_INCREMENT PRIMARY KEY,
        borough TINYINT NOT NULL,
        block INT NOT NULL,
        lot INT NOT NULL,
        streetnumber VARCHAR(20) NOT NULL DEFAULT '',
        streetname VARCHAR(100) NOT NULL DEFAULT '',
        unit VARCHAR(20) NOT NULL DEFAULT '',
        propertytype CHAR(2) NOT NULL DEFAULT '',
        in_maps TINYINT(1) NOT NULL DEFAULT 0,
        in_cdec TINYINT(1) NOT NULL DEFAULT 0,
        in_deed TINYINT(1) NOT NULL DEFAULT 0,
        in_other TINYINT(1) NOT NULL DEFAULT 0,
        doc_type_list VARCHAR(200) NOT NULL DEFAULT '',
        total_docs INT NOT NULL DEFAULT 0,
        earliest_date VARCHAR(10) NOT NULL DEFAULT '',
        latest_date VARCHAR(10) NOT NULL DEFAULT '',
        UNIQUE KEY bbl (borough, block, lot),
        INDEX idx_address (streetname, streetnumber),
        INDEX idx_address_unit (streetname, streetnumber, unit),
        INDEX idx_block (borough, block),
        INDEX idx_sources (in_maps, in_cdec, in_deed)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

INSERT_BATCH = """
    INSERT INTO condo_units
        (borough, block, lot, streetnumber, streetname, unit, propertytype,
         in_maps, in_cdec, in_deed, in_other,
         doc_type_list, total_docs, earliest_date, latest_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

BATCH_SIZE = 5000


def fetch_data():
    """Fetch all condo unit records from the database."""
    conn = mysql.connector.connect(**DB_CONFIG)
    print("Connected to database. Fetching condo records...")
    df = pd.read_sql(FETCH_QUERY, conn)
    conn.close()
    print(f"Fetched {len(df):,} records.")
    return df


def build_unit_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate records into one row per unique BBL (condo unit)."""
    print("Normalizing street names...")
    df["norm_streetname"] = df["streetname"].apply(normalize_streetname)

    print("Building unit inventory...")
    grouped = df.groupby(["borough", "block", "lot"])
    results = []

    for (borough, block, lot), group in grouped:
        # Canonical street name: most common normalized form
        name_counts = Counter(n for n in group["norm_streetname"] if n)
        canonical_name = name_counts.most_common(1)[0][0] if name_counts else ""

        # Canonical street number
        num_counts = Counter(
            str(n).strip() for n in group["streetnumber"]
            if pd.notna(n) and str(n).strip()
        )
        canonical_number = num_counts.most_common(1)[0][0] if num_counts else ""

        # Unit: most common non-empty unit value
        unit_counts = Counter(
            str(u).strip() for u in group["unit"]
            if pd.notna(u) and str(u).strip()
        )
        canonical_unit = unit_counts.most_common(1)[0][0] if unit_counts else ""

        # Property type: prefer SC over MC
        ptypes = set(group["propertytype"].dropna())
        ptype = "SC" if "SC" in ptypes else ("MC" if "MC" in ptypes else "")

        # Source flags
        doc_types = set(group["doctype"].dropna())
        in_maps = 1 if "MAPS" in doc_types else 0
        in_cdec = 1 if "CDEC" in doc_types else 0
        in_deed = 1 if "DEED" in doc_types else 0
        other_types = doc_types - {"MAPS", "CDEC", "DEED"}
        in_other = 1 if other_types else 0

        # Doc type summary
        doc_type_list = "; ".join(sorted(doc_types))

        # Total distinct documents
        total_docs = group["documentid"].nunique()

        # Date range
        dates = group["docdate"].dropna()
        dates = dates[dates != ""]
        earliest = ""
        latest = ""
        if len(dates) > 0:
            # Dates are MM/DD/YYYY, sort lexically won't work — parse minimally
            def parse_date_sortable(d):
                try:
                    parts = str(d).split("/")
                    return f"{parts[2]}{parts[0].zfill(2)}{parts[1].zfill(2)}"
                except (IndexError, ValueError):
                    return ""
            sortable = dates.apply(parse_date_sortable)
            sortable = sortable[sortable != ""]
            if len(sortable) > 0:
                earliest = dates.iloc[sortable.values.argmin()]
                latest = dates.iloc[sortable.values.argmax()]

        results.append((
            int(borough), int(block), int(lot),
            canonical_number, canonical_name, canonical_unit, ptype,
            in_maps, in_cdec, in_deed, in_other,
            doc_type_list[:200], total_docs, earliest, latest,
        ))

    print(f"Built inventory of {len(results):,} unique condo units.")
    return results


def write_to_db(rows):
    """Write inventory to the condo_units table."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("Creating condo_units table...")
    for stmt in CREATE_TABLE.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            cursor.execute(stmt)
    conn.commit()

    print(f"Inserting {len(rows):,} rows...")
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        cursor.executemany(INSERT_BATCH, batch)
        conn.commit()
        if (i // BATCH_SIZE) % 20 == 0:
            print(f"  {i + len(batch):,} / {len(rows):,}")

    print(f"Inserted {len(rows):,} rows.")
    cursor.close()
    conn.close()


def print_stats(rows):
    """Print summary statistics."""
    df = pd.DataFrame(rows, columns=[
        "borough", "block", "lot", "streetnumber", "streetname", "unit",
        "propertytype", "in_maps", "in_cdec", "in_deed", "in_other",
        "doc_type_list", "total_docs", "earliest_date", "latest_date",
    ])

    borough_names = {1: "Manhattan", 2: "Bronx", 3: "Brooklyn", 4: "Queens", 5: "Staten Island"}

    print(f"\nTotal condo units: {len(df):,}")
    print(f"\nBy borough:")
    for borough, count in df.groupby("borough").size().items():
        print(f"  {borough_names.get(borough, borough)}: {count:,}")

    print(f"\nBy source coverage:")
    print(f"  In MAPS:  {df['in_maps'].sum():,}")
    print(f"  In CDEC:  {df['in_cdec'].sum():,}")
    print(f"  In DEED:  {df['in_deed'].sum():,}")
    print(f"  In other: {df['in_other'].sum():,}")

    maps_only = len(df[(df["in_maps"] == 1) & (df["in_deed"] == 0)])
    deed_only = len(df[(df["in_maps"] == 0) & (df["in_cdec"] == 0) & (df["in_deed"] == 1)])
    no_maps_no_cdec = len(df[(df["in_maps"] == 0) & (df["in_cdec"] == 0)])
    print(f"\n  MAPS but no DEED:  {maps_only:,} (registered but never sold)")
    print(f"  DEED only (no MAPS/CDEC): {deed_only:,} (sold but no condo filing on record)")
    print(f"  No MAPS or CDEC:   {no_maps_no_cdec:,}")

    # Distinct buildings (by borough+block)
    buildings = df.groupby(["borough", "block"]).size().reset_index(name="units")
    print(f"\nDistinct buildings (borough+block): {len(buildings):,}")
    print(f"  Median units per building: {buildings['units'].median():.0f}")
    print(f"  Mean units per building:   {buildings['units'].mean():.1f}")
    print(f"  Max units in a building:   {buildings['units'].max()}")


def main():
    df = fetch_data()
    rows = build_unit_inventory(df)
    write_to_db(rows)
    print_stats(rows)


if __name__ == "__main__":
    main()
