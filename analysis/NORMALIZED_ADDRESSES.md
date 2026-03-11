# normalized_addresses Table

## Overview

The `normalized_addresses` table provides a deduplicated, normalized view of all property addresses in the ACRIS dataset. It is derived from `real_property_legals` by grouping records on the NYC BBL (Borough-Block-Lot) identifier and resolving the most common spelling of each address.

**Row count:** ~1.13M properties across all five boroughs.

| Borough | Code | Properties |
|---------|------|-----------|
| Manhattan | 1 | 182,652 |
| Bronx | 2 | 108,473 |
| Brooklyn | 3 | 362,914 |
| Queens | 4 | 377,644 |
| Staten Island | 5 | 99,989 |

## Schema

```sql
CREATE TABLE normalized_addresses (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    borough       TINYINT NOT NULL,       -- 1=Manhattan, 2=Bronx, 3=Brooklyn, 4=Queens, 5=Staten Island
    block         INT NOT NULL,
    lot           INT NOT NULL,
    streetnumber  VARCHAR(20) NOT NULL,    -- e.g. '420', '88-37'
    streetname    VARCHAR(100) NOT NULL,   -- normalized, e.g. 'EAST 72ND STREET'
    unit_count    INT NOT NULL DEFAULT 0,  -- number of distinct units found in transaction history
    units         TEXT,                    -- semicolon-separated list of unit identifiers

    UNIQUE KEY bbl (borough, block, lot),
    INDEX idx_street (streetname, streetnumber),
    INDEX idx_street_full (streetnumber, streetname, borough)
);
```

## Normalization rules applied

The `streetname` column has been cleaned from raw ACRIS data using these rules:

- **Direction prefixes** expanded: `E`, `E.` -> `EAST`; `W`, `W.` -> `WEST`; etc.
- **Street type suffixes** expanded: `ST` -> `STREET`, `AVE` -> `AVENUE`, `PL` -> `PLACE`, `BLVD` -> `BOULEVARD`, `DR` -> `DRIVE`, `CT` -> `COURT`, `RD` -> `ROAD`, etc.
- **Ordinal suffixes** corrected: `72 STREET` -> `72ND STREET`, `72TH` -> `72ND`, `3ST` -> `3RD`
- **Spelled-out numbers** converted: `FIFTH` -> `5TH`, `THIRD` -> `3RD`
- **Common typos** fixed: `STRET` -> `STREET`, `AVENIE` -> `AVENUE`, `BRADHURTS` -> `BRADHURST`, etc.
- **Embedded unit info** stripped: `EAST 72ND STREET APT 3B` -> `EAST 72ND STREET`
- **Whitespace** collapsed and trailing punctuation removed

When multiple spellings exist for the same BBL, the most frequently occurring normalized form is chosen.

## Indexes

| Index | Columns | Use case |
|-------|---------|----------|
| `bbl` (unique) | borough, block, lot | Look up a specific property by its BBL |
| `idx_street` | streetname, streetnumber | Find all properties on a street, optionally filtered by number |
| `idx_street_full` | streetnumber, streetname, borough | Find a specific address in a specific borough |

## Sample queries

### Look up a specific address
```sql
SELECT * FROM normalized_addresses
WHERE streetnumber = '420' AND streetname = 'EAST 72ND STREET' AND borough = 1;
```

### Find all properties on a street
```sql
SELECT streetnumber, streetname, unit_count
FROM normalized_addresses
WHERE streetname = 'EAST 72ND STREET' AND borough = 1
ORDER BY CAST(streetnumber AS UNSIGNED);
```

### Find large buildings (by unit count)
```sql
SELECT streetnumber, streetname, borough, unit_count
FROM normalized_addresses
WHERE borough = 1
ORDER BY unit_count DESC
LIMIT 20;
```

### Find all townhouse-type properties (join with sales data)
```sql
SELECT na.streetnumber, na.streetname, na.block, na.lot,
       l.propertytype, p.typedescription
FROM normalized_addresses na
JOIN real_property_legals l ON na.borough = l.borough
    AND na.block = l.block AND na.lot = l.lot
LEFT JOIN property_type_codes p ON l.propertytype = p.propertytype
WHERE na.borough = 1
  AND l.propertytype IN ('D1','D2','D3')
GROUP BY na.streetnumber, na.streetname, na.block, na.lot,
         l.propertytype, p.typedescription
ORDER BY na.streetname, na.streetnumber;
```

### Find sales history for a specific address
```sql
SELECT m.docdate, m.docamount, m.doctype,
       p1.name AS seller, p2.name AS buyer
FROM normalized_addresses na
JOIN real_property_legals l ON na.borough = l.borough
    AND na.block = l.block AND na.lot = l.lot
JOIN real_property_master m ON l.documentid = m.documentid
LEFT JOIN real_property_parties p1 ON m.documentid = p1.documentid AND p1.partytype = 1
LEFT JOIN real_property_parties p2 ON m.documentid = p2.documentid AND p2.partytype = 2
WHERE na.streetnumber = '420' AND na.streetname = 'EAST 72ND STREET' AND na.borough = 1
  AND m.doctype = 'DEED' AND m.docamount > 0
ORDER BY m.docdate DESC;
```

### Search by partial street name
```sql
SELECT streetnumber, streetname, borough, unit_count
FROM normalized_addresses
WHERE streetname LIKE 'PARK AVENUE%' AND borough = 1
ORDER BY CAST(streetnumber AS UNSIGNED);
```

## Regenerating the table

```bash
cd analysis
.venv/bin/python normalize_addresses.py
```

This will drop and recreate the table. Requires the MySQL container to be running. Update `config.py` with the current mapped port if it has changed.
