"""
Address normalizer for ACRIS real property data.

Reads raw addresses from real_property_legals, normalizes street names,
and produces a canonical address per borough/block/lot with all known units.
"""

import re
import mysql.connector
import pandas as pd
from collections import Counter
from config import DB_CONFIG


# ---------------------------------------------------------------------------
# Normalization rules
# ---------------------------------------------------------------------------

# Direction prefixes: normalize short forms to full words
DIRECTION_MAP = {
    "E": "EAST",
    "E.": "EAST",
    "W": "WEST",
    "W.": "WEST",
    "N": "NORTH",
    "N.": "NORTH",
    "S": "SOUTH",
    "S.": "SOUTH",
}

# Street type suffixes: normalize abbreviations to full words
SUFFIX_MAP = {
    "ST": "STREET",
    "ST.": "STREET",
    "ST.,": "STREET",
    "STREE": "STREET",
    "STRET": "STREET",
    "STRRET": "STREET",
    "AVE": "AVENUE",
    "AVE.": "AVENUE",
    "AVENU": "AVENUE",
    "AVENEU": "AVENUE",
    "AVENEU": "AVENUE",
    "AVENIE": "AVENUE",
    "AVENUW": "AVENUE",
    "AVEUE": "AVENUE",
    "AVEBYE": "AVENUE",
    "AVENNUE": "AVENUE",
    "PL": "PLACE",
    "PL.": "PLACE",
    "BLVD": "BOULEVARD",
    "BLVD.": "BOULEVARD",
    "DR": "DRIVE",
    "DR.": "DRIVE",
    "CT": "COURT",
    "CT.": "COURT",
    "LN": "LANE",
    "LN.": "LANE",
    "TER": "TERRACE",
    "RD": "ROAD",
    "RD.": "ROAD",
    "PKWY": "PARKWAY",
    "SQ": "SQUARE",
    "SQ.": "SQUARE",
}

# Ordinal suffixes for street numbers
ORDINAL_MAP = {
    "1": "1ST", "2": "2ND", "3": "3RD",
    "21": "21ST", "22": "22ND", "23": "23RD",
    "31": "31ST", "32": "32ND", "33": "33RD",
    "41": "41ST", "42": "42ND", "43": "43RD",
    "51": "51ST", "52": "52ND", "53": "53RD",
    "61": "61ST", "62": "62ND", "63": "63RD",
    "71": "71ST", "72": "72ND", "73": "73RD",
    "81": "81ST", "82": "82ND", "83": "83RD",
    "91": "91ST", "92": "92ND", "93": "93RD",
    "101": "101ST", "102": "102ND", "103": "103RD",
    "111": "111TH", "112": "112TH", "113": "113TH",
    "121": "121ST", "122": "122ND", "123": "123RD",
    "131": "131ST", "132": "132ND", "133": "133RD",
    "141": "141ST", "142": "142ND", "143": "143RD",
    "151": "151ST", "152": "152ND", "153": "153RD",
    "161": "161ST", "162": "162ND", "163": "163RD",
    "171": "171ST", "172": "172ND", "173": "173RD",
    "181": "181ST", "182": "182ND", "183": "183RD",
    "191": "191ST", "192": "192ND", "193": "193RD",
    "201": "201ST", "202": "202ND", "203": "203RD",
    "211": "211TH", "212": "212TH", "213": "213TH",
    "221": "221ST", "222": "222ND", "223": "223RD",
}

# Words spelled out for numbered streets/avenues
SPELLED_NUMBERS = {
    "FIRST": "1ST",
    "SECOND": "2ND",
    "THIRD": "3RD",
    "FOURTH": "4TH",
    "FIFTH": "5TH",
    "SIXTH": "6TH",
    "SEVENTH": "7TH",
    "EIGHTH": "8TH",
    "EIGTH": "8TH",
    "NINTH": "9TH",
    "TENTH": "10TH",
    "ELEVENTH": "11TH",
    "ELEVNTH": "11TH",
    "TWELFTH": "12TH",
    "THIRTEENTH": "13TH",
}

# Known name corrections
NAME_FIXES = {
    "AMSTERDM": "AMSTERDAM",
    "BRADHURTS": "BRADHURST",
    "COUMBUS": "COLUMBUS",
    "EDGECUMBE": "EDGECOMBE",
    "EDGECOMBER": "EDGECOMBE",
    "MANHATTEN": "MANHATTAN",
    "MORNINSSIDE": "MORNINGSIDE",
    "FILTH": "FIFTH",
    "SEVETH": "SEVENTH",
    "SEVERTH": "SEVENTH",
    "THID": "THIRD",
    "THIED": "THIRD",
}


def normalize_streetname(raw: str) -> str:
    """Normalize a raw ACRIS street name to a canonical form."""
    if not raw or not raw.strip():
        return ""

    name = raw.strip().upper()

    # Strip trailing punctuation: backtick, comma, period (if not part of abbreviation)
    name = re.sub(r"[`]+$", "", name)
    name = re.sub(r",\s*$", "", name)

    # Strip appended unit/apt info:
    # "EAST 72ND STREET UNIT 21J" -> "EAST 72ND STREET"
    # "W 72ND ST APT 6N" -> "W 72ND ST"
    # "BROADWAY #27A" -> "BROADWAY"
    # "7TH AVENUE, 5G" -> "7TH AVENUE"
    name = re.sub(
        r"\s*(,\s*|\s)(APT\.?|UNIT|#|SUITE|STE|FL|FLOOR|PENTHOUSE|PH)\s*.*$",
        "",
        name,
    )
    # Also strip ", <unit>" patterns like "BROADWAY, #12D" or "5TH AVE 22G"
    name = re.sub(r",\s*#?\w+$", "", name)

    # Collapse multiple spaces
    name = re.sub(r"\s+", " ", name).strip()

    # Strip trailing periods
    name = re.sub(r"\.\s*$", "", name)

    # Fix concatenated direction+street: "EAST72ND" -> "EAST 72ND", "WEST72ND" -> "WEST 72ND"
    name = re.sub(r"^(EAST|WEST|NORTH|SOUTH)(\d)", r"\1 \2", name)

    # Fix concatenated number+suffix: "72ST" -> "72 ST" (only bare number+suffix)
    name = re.sub(r"^(\d+)(ST|ND|RD|TH)\b", r"\1 \2", name)

    # Split into tokens for processing
    tokens = name.split()
    if not tokens:
        return ""

    result = []
    i = 0

    # --- Pass 1: Normalize direction prefix ---
    if tokens[0] in DIRECTION_MAP:
        result.append(DIRECTION_MAP[tokens[0]])
        i = 1
    # Handle "W EST" -> "WEST"
    elif len(tokens) >= 2 and tokens[0] == "W" and tokens[1] == "EST":
        result.append("WEST")
        i = 2

    # --- Pass 2: Process remaining tokens ---
    while i < len(tokens):
        token = tokens[i]

        # Fix known misspellings
        if token in NAME_FIXES:
            token = NAME_FIXES[token]

        # Convert spelled-out numbers: "FIFTH" -> "5TH"
        if token in SPELLED_NUMBERS:
            token = SPELLED_NUMBERS[token]

        # Fix wrong ordinal suffixes: "72TH" -> "72ND"
        m = re.match(r"^(\d+)(ST|ND|RD|TH)$", token)
        if m:
            num = m.group(1)
            token = _make_ordinal(int(num))

        result.append(token)
        i += 1

    # --- Pass 3: Normalize suffix (last token) ---
    if result:
        last = result[-1]
        if last in SUFFIX_MAP:
            result[-1] = SUFFIX_MAP[last]

    # --- Pass 4: Add missing ordinal suffix ---
    # "EAST 72 STREET" -> "EAST 72ND STREET"
    # Check if there's a bare number followed by a street type
    for idx in range(len(result) - 1):
        if re.match(r"^\d+$", result[idx]) and result[idx + 1] in (
            "STREET", "AVENUE", "PLACE", "BOULEVARD", "DRIVE", "COURT",
            "LANE", "TERRACE", "ROAD", "PARKWAY", "SQUARE",
        ):
            result[idx] = _make_ordinal(int(result[idx]))

    # Collapse spaces again and return
    return " ".join(result)


def _make_ordinal(n: int) -> str:
    """Convert an integer to its ordinal string: 1->1ST, 2->2ND, 72->72ND."""
    s = str(n)
    if s in ORDINAL_MAP:
        return ORDINAL_MAP[s]
    # General rules
    if 11 <= (n % 100) <= 13:
        return f"{n}TH"
    remainder = n % 10
    if remainder == 1:
        return f"{n}ST"
    if remainder == 2:
        return f"{n}ND"
    if remainder == 3:
        return f"{n}RD"
    return f"{n}TH"


# ---------------------------------------------------------------------------
# Database queries and main logic
# ---------------------------------------------------------------------------

QUERY = """
    SELECT borough, block, lot, streetnumber, streetname, unit
    FROM real_property_legals
    WHERE borough IS NOT NULL
      AND block IS NOT NULL AND block > 0
      AND lot IS NOT NULL AND lot > 0
"""


def fetch_data():
    """Fetch all address records from the database."""
    conn = mysql.connector.connect(**DB_CONFIG)
    print("Connected to database. Fetching records...")
    df = pd.read_sql(QUERY, conn)
    conn.close()
    print(f"Fetched {len(df):,} records.")
    return df


def build_normalized_addresses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group by borough/block/lot, normalize street names,
    pick the most common canonical name, and collect units.
    """
    print("Normalizing street names...")
    df["normalized_streetname"] = df["streetname"].apply(normalize_streetname)

    print("Grouping by borough/block/lot...")
    results = []
    grouped = df.groupby(["borough", "block", "lot"])

    for (borough, block, lot), group in grouped:
        # Pick the most common normalized street name
        name_counts = Counter(
            n for n in group["normalized_streetname"] if n
        )
        if name_counts:
            canonical_name = name_counts.most_common(1)[0][0]
        else:
            canonical_name = ""

        # Pick the most common street number
        num_counts = Counter(
            str(n).strip() for n in group["streetnumber"] if pd.notna(n) and str(n).strip()
        )
        if num_counts:
            canonical_number = num_counts.most_common(1)[0][0]
        else:
            canonical_number = ""

        # Collect distinct non-empty units, sorted
        units = sorted(set(
            str(u).strip()
            for u in group["unit"]
            if pd.notna(u) and str(u).strip()
        ))

        results.append({
            "borough": int(borough),
            "block": int(block),
            "lot": int(lot),
            "streetnumber": canonical_number,
            "streetname": canonical_name,
            "unit_count": len(units),
            "units": "; ".join(units) if units else "",
        })

    result_df = pd.DataFrame(results)
    print(f"Normalized to {len(result_df):,} unique properties.")
    return result_df


CREATE_TABLE = """
    DROP TABLE IF EXISTS normalized_addresses;
    CREATE TABLE normalized_addresses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        borough TINYINT NOT NULL,
        block INT NOT NULL,
        lot INT NOT NULL,
        streetnumber VARCHAR(20) NOT NULL DEFAULT '',
        streetname VARCHAR(100) NOT NULL DEFAULT '',
        unit_count INT NOT NULL DEFAULT 0,
        units TEXT,
        UNIQUE KEY bbl (borough, block, lot),
        INDEX idx_street (streetname, streetnumber),
        INDEX idx_street_full (streetnumber, streetname, borough)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

INSERT_BATCH = """
    INSERT INTO normalized_addresses
        (borough, block, lot, streetnumber, streetname, unit_count, units)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

BATCH_SIZE = 5000


def write_to_db(df: pd.DataFrame):
    """Write normalized addresses to the normalized_addresses table."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("Creating normalized_addresses table...")
    for stmt in CREATE_TABLE.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            cursor.execute(stmt)
    conn.commit()

    print(f"Inserting {len(df):,} rows...")
    rows = list(df.itertuples(index=False, name=None))
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        cursor.executemany(INSERT_BATCH, batch)
        conn.commit()
        if (i // BATCH_SIZE) % 20 == 0:
            print(f"  {i + len(batch):,} / {len(rows):,}")

    print(f"Inserted {len(rows):,} rows.")
    cursor.close()
    conn.close()


def main():
    df = fetch_data()
    normalized = build_normalized_addresses(df)

    # Drop rows with no resolved address
    normalized = normalized[normalized["streetname"] != ""]
    normalized = normalized[normalized["streetnumber"] != ""]

    # Ensure column order matches INSERT statement
    normalized = normalized[
        ["borough", "block", "lot", "streetnumber", "streetname", "unit_count", "units"]
    ]

    write_to_db(normalized)

    # Print stats
    borough_names = {1: "Manhattan", 2: "Bronx", 3: "Brooklyn", 4: "Queens", 5: "Staten Island"}
    print(f"\nProperties by borough:")
    for borough, count in normalized.groupby("borough").size().items():
        print(f"  {borough_names.get(borough, borough)}: {count:,}")


if __name__ == "__main__":
    main()
