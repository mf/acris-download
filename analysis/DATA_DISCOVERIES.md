# ACRIS Data Discoveries

Findings from exploring the ACRIS dataset. These inform how to query the data correctly and what pitfalls to avoid.

## Known data quality issues

### Boolean columns are broken (all zeros)

The CSV contains `Y`/`N` for boolean fields (`easement`, `airrights`, `subterraneanrights` in `real_property_legals`; `not_used_1`, `not_used_2` in `real_property_references`). MySQL's `LOAD DATA LOCAL INFILE` cannot parse `Y`/`N` into `boolean` (`tinyint(1)`) and silently inserts `0` for all values. **All 22.5M rows read as 0 regardless of the original value.**

Fix: change these columns to `CHAR(1)` or `VARCHAR(1)` in the schema.

### Missing schema definitions

The schema files (`schema/mysql.sql`, `schema/postgres.sql`, `schema/sqlite.sql`) do not define tables for:
- `real_property_remarks`
- `personal_property_legals`, `personal_property_master`, `personal_property_parties`
- `personal_property_references`, `personal_property_remarks`

The Makefile has targets to load these (`mysql_personal`, `mysql_real_complete`) but they will fail because the tables don't exist.

### goodthroughdate type inconsistency

In `real_property_references`, `goodthroughdate` is declared as `timestamp` while all other tables use `text`. The CSV format is `MM/DD/YYYY HH:MM:SS AM` which MySQL can't parse as a timestamp (expects `YYYY-MM-DD HH:MM:SS`). Values will be null or fail on import.

### documentid type mismatch in SQLite schema

SQLite schema uses `bigint` for `documentid`. Document IDs are zero-padded strings (e.g., `2005011101969002`) and should be `varchar`/`text` to preserve leading zeros.

### All dates stored as text

`docdate`, `recordedfiled`, `modifieddate`, `goodthroughdate` are all `text` in `MM/DD/YYYY` format. This prevents native date comparisons and range queries. Sorting by date requires parsing.

## Street name variations

A single address can appear with 10+ different spellings in `real_property_legals`. Examples for 420 East 72nd Street:

- `EAST 72ND STREET`, `EAST 72 STREET`, `EAST 72ND ST`, `E 72ND STREET`, `E. 72ND STREET`, `EAST 72ND   STREET` (double space), `EAST 72ND ST.`

The `normalized_addresses` table resolves this by grouping on BBL (borough+block+lot) — the authoritative property identifier — and picking the most common normalized spelling. See [NORMALIZED_ADDRESSES.md](NORMALIZED_ADDRESSES.md).

## Property types relevant to residential analysis

### Townhouse types
| Code | Description | Notes |
|------|-------------|-------|
| D1 | Dwelling only - 1 family | Classic single-family townhouse |
| D2 | Dwelling only - 2 family | Two-unit brownstone |
| D3 | Dwelling only - 3 family | Three-unit brownstone |
| RP | 1-2 family with attached garage/vacant land | Older code, split into RG/RV |
| RG | 1-2 family with attached garage | Rare in Manhattan |
| RV | 1-2 family with vacant land | Very rare in Manhattan |

### Condo types
| Code | Description | Notes |
|------|-------------|-------|
| SC | Single residential condo unit | Each unit is a separate tax lot |
| MC | Multiple residential condo units | Multiple units in one transaction |
| CC | Commercial condo unit(s) | Commercial space within condo buildings |
| PS | Parking space | Condo parking units |
| SR | Storage room | Condo storage units |
| CK | Condo unit without kitchen | Studios, maids rooms registered as units |
| BS | Bulk sale of condominiums | Sponsor selling multiple units at once |

### Coop types
| Code | Description | Notes |
|------|-------------|-------|
| SP | Single residential coop unit | No individual tax lot, shares in a corp |
| MP | Multiple residential coop units | Multiple coop units in one transaction |
| CP | Commercial coop unit(s) | Commercial space in coop buildings |

## Condo vs coop: structural differences in ACRIS

**Condos** have individual BBLs per unit. The city maintains a formal registry via MAPS and CDEC filings. Each unit can be independently looked up, mortgaged, and transferred.

**Coops** are a single BBL for the entire building. Shareholders own stock in a corporation, not real property. There are essentially no MAPS filings for coops (only 115 out of 271K+ coop-related records). Unit enumeration for coops must rely on transaction records (DEEDs, mortgages, etc.) and is inherently incomplete.

## Key document types

### For identifying properties
- **MAPS** — Condo floor plan. Lists every unit as a parcel. Best source for complete unit enumeration in condo buildings.
- **CDEC** — Condo declaration. Legal creation of the condominium. Always paired with MAPS (consecutive doc IDs, same filing date).

### For tracking sales
- **DEED** — Transfer of ownership. Filter with `docamount > 0` for actual sales (vs trust transfers at $0).
- **RPTT** — NYC Real Property Transfer Tax. Confirms a sale occurred.

### Other common types
- **MTGE** — Mortgage. Indicates financing activity.
- **SAT** — Satisfaction of mortgage. Mortgage paid off.
- **AGMT** — Agreement. Various legal agreements.
- **ASST** — Assignment of lease or mortgage.
- **PAT** — Power of attorney.
- **LOCC** — Lien of common charges. Indicates unpaid condo fees.

## Condo unit coverage analysis

No single document type captures all condo units:

| Source | Units | % of total |
|--------|-------|-----------|
| MAPS | 157,622 | 58% |
| CDEC | 135,011 | 50% |
| DEED | 209,229 | 77% |
| All sources combined | 271,610 | 100% |

- 22,784 units in MAPS but never sold — sponsor-held or unsold
- 73,924 units sold (DEED) but no MAPS/CDEC on file — older buildings
- 113,338 units with no MAPS or CDEC — known only from transactions

See [CONDO_UNITS.md](CONDO_UNITS.md) for the comprehensive inventory table.

## Multiple MAPS filings per building

Most condo buildings have 1-2 MAPS filings, but some have many more (up to 61). Multiple filings occur due to:
- Amendments adding new units (subdivisions, conversions of common space)
- Corrections to the original filing
- Phased construction

When building a unit inventory, take the **union across all MAPS filings** for a given block.

## Manhattan townhouse sales

~4,600 unique townhouse addresses identified from deed sales in Manhattan (borough=1), filtered by property types D1, D2, D3, RP, RG, RV. Annual volume:
- Typical year: 150-280 sales
- COVID dip (2020): ~150 sales
- Peak years: 2004-2007, 2021-2022
- D1 (1-family) consistently most traded

Exported to `data/manhattan_townhouses.csv`.

## Added indexes

Beyond the default `documentid` indexes created by the Makefile, these were added for analysis queries:

**real_property_legals:**
- `idx_address (streetname, streetnumber)` — address search
- `idx_address_unit (streetname, streetnumber, unit)` — address + unit search
- `idx_bbl (borough, block, lot)` — BBL lookups

**real_property_master:**
- `idx_doctype (doctype)` — filter by document type

Note: these indexes are not persisted across `make mysql` runs. They would need to be added to the Makefile or a post-load script.
