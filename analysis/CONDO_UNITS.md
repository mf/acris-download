# condo_units Table

## Overview

The `condo_units` table is a comprehensive inventory of all known condominium units in the ACRIS dataset. It combines data from **all document types** — MAPS filings, condo declarations, deed sales, mortgages, and more — to produce a single row per unit identified by its BBL (Borough-Block-Lot).

**Row count:** 271,610 units across 6,741 buildings.

| Borough | Units |
|---------|-------|
| Manhattan | 127,772 |
| Bronx | 17,116 |
| Brooklyn | 72,248 |
| Queens | 46,418 |
| Staten Island | 8,056 |

## Schema

```sql
CREATE TABLE condo_units (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    borough       TINYINT NOT NULL,        -- 1=Manhattan, 2=Bronx, 3=Brooklyn, 4=Queens, 5=Staten Island
    block         INT NOT NULL,
    lot           INT NOT NULL,
    streetnumber  VARCHAR(20) NOT NULL,     -- normalized
    streetname    VARCHAR(100) NOT NULL,    -- normalized (see normalize_addresses.py)
    unit          VARCHAR(20) NOT NULL,     -- most common unit designation for this lot
    propertytype  CHAR(2) NOT NULL,         -- SC=single condo, MC=multiple condo
    in_maps       TINYINT(1) NOT NULL,      -- 1 if unit appears in a MAPS filing
    in_cdec       TINYINT(1) NOT NULL,      -- 1 if unit appears in a CDEC filing
    in_deed       TINYINT(1) NOT NULL,      -- 1 if unit appears in a DEED
    in_other      TINYINT(1) NOT NULL,      -- 1 if unit appears in other doc types
    doc_type_list VARCHAR(200) NOT NULL,    -- semicolon-separated list of all doc types seen
    total_docs    INT NOT NULL,             -- count of distinct documents referencing this unit
    earliest_date VARCHAR(10) NOT NULL,     -- earliest doc date (MM/DD/YYYY)
    latest_date   VARCHAR(10) NOT NULL,     -- latest doc date (MM/DD/YYYY)

    UNIQUE KEY bbl (borough, block, lot),
    INDEX idx_address (streetname, streetnumber),
    INDEX idx_address_unit (streetname, streetnumber, unit),
    INDEX idx_block (borough, block),
    INDEX idx_sources (in_maps, in_cdec, in_deed)
);
```

## How units are identified

Each condo unit in NYC has its own tax lot (BBL). A building at a single address shares a `block` number, and each unit gets a unique `lot` within that block. For example, 514 West 110th Street (block 1881) has lots 1301-1399 for individual units.

Units are included if they appear in `real_property_legals` with `propertytype` of `SC` (Single Residential Condo Unit) or `MC` (Multiple Residential Condo Units) in **any** document type.

## Data sources and coverage

| Source | Units covered | What it captures |
|--------|-------------|------------------|
| MAPS (condo map filings) | 157,622 | Official unit registration with the city |
| CDEC (condo declarations) | 135,011 | Legal establishment of the condominium |
| DEED (sales) | 209,229 | Units that have been sold at least once |
| Other (MTGE, SAT, AGMT, etc.) | 262,653 | Mortgages, satisfactions, agreements, etc. |
| **Combined (this table)** | **271,610** | **All sources merged** |

No single source is complete:
- **22,784 units** have MAPS but no DEED — registered but never sold (sponsor-held or unsold)
- **73,924 units** have DEEDs but no MAPS/CDEC — older condos predating the filing system
- **113,338 units** have no MAPS or CDEC at all — known only through transaction records

## Key document types for condos

- **MAPS** — Condo map/floor plan. Filed when a building becomes a condo. Lists every unit as a separate parcel. Most authoritative for unit enumeration.
- **CDEC** — Condo declaration. The legal document creating the condominium. Always paired with a MAPS filing (consecutive doc IDs).
- **DEED** — Sale/transfer of a unit.
- **MTGE** / **SAT** — Mortgage and satisfaction of mortgage.
- **AGMT** — Agreement (various legal agreements referencing units).
- **ASST** — Assignment of lease or mortgage.

## Note on coops

Coops are **not** included in this table. Coop units are shares in a corporation, not individual tax lots, so they don't get MAPS/CDEC filings. Coop units can be found via `propertytype` values `SP` (single coop) and `MP` (multiple coop) in transaction records, but there is no authoritative registry of all units in a coop building.

## Sample queries

### Look up all units in a building
```sql
SELECT unit, lot, in_maps, in_deed, total_docs, earliest_date, latest_date
FROM condo_units
WHERE streetnumber = '514' AND streetname = 'WEST 110TH STREET' AND borough = 1
ORDER BY unit;
```

### Find buildings with the most units
```sql
SELECT streetnumber, streetname, borough, block, COUNT(*) AS units
FROM condo_units
GROUP BY streetnumber, streetname, borough, block
ORDER BY units DESC
LIMIT 20;
```

### Find units registered but never sold
```sql
SELECT streetnumber, streetname, unit, borough
FROM condo_units
WHERE in_maps = 1 AND in_deed = 0
ORDER BY streetname, streetnumber, unit;
```

### Find units sold but with no condo filing on record
```sql
SELECT streetnumber, streetname, unit, borough, earliest_date
FROM condo_units
WHERE in_maps = 0 AND in_cdec = 0 AND in_deed = 1
ORDER BY streetname, streetnumber;
```

### Count units per building in Manhattan
```sql
SELECT streetnumber, streetname, block, COUNT(*) AS units,
       SUM(in_maps) AS mapped, SUM(in_deed) AS sold
FROM condo_units
WHERE borough = 1
GROUP BY streetnumber, streetname, block
ORDER BY units DESC;
```

### Cross-reference with normalized_addresses
```sql
SELECT na.streetnumber, na.streetname, na.unit_count AS total_known_units,
       COUNT(cu.id) AS condo_units
FROM normalized_addresses na
JOIN condo_units cu ON na.borough = cu.borough AND na.block = cu.block
WHERE na.borough = 1
GROUP BY na.streetnumber, na.streetname, na.unit_count, na.block
ORDER BY condo_units DESC
LIMIT 20;
```

## Regenerating the table

```bash
cd analysis
.venv/bin/python build_condo_units.py
```

Drops and recreates the table. Requires the MySQL container and the `normalize_addresses` module (imported for street name normalization).
