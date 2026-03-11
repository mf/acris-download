# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ACRIS Downloader: fetches NYC real estate property transaction data (ACRIS) from the NYC Department of Finance open data portal and loads it into MySQL, PostgreSQL, or SQLite. The `analysis/` subfolder contains Python tools for post-processing the loaded data.

## Common Commands

### Data Download & Database Loading (via Makefile)

```bash
make download                  # Download real property basic CSVs
make mysql                     # Load real property basics into MySQL
make mysql_real_complete        # + references and remarks
make mysql_personal             # Load personal property basics
make mysql_personal_complete    # + personal references and remarks
make mysql_test                 # Run test query against MySQL
make psql                       # PostgreSQL equivalent
make sqlite                     # SQLite equivalent
make clean                      # Remove downloaded CSVs
make clean-docker               # Remove Docker volume data
```

### Docker

```bash
# MySQL stack (db + loader + adminer on :8080)
docker compose -f docker-compose.mysql.yml up -d
# PostgreSQL stack
docker compose -f docker-compose.psql.yml up -d
# Note: MySQL port is randomly mapped (check `docker ps` for current port)
```

Docker MySQL defaults: user=`root`, password=`pass`, database=`acris`.

### Analysis Python Scripts

```bash
cd analysis
.venv/bin/python normalize_addresses.py   # Rebuild normalized_addresses table
```

Python venv at `analysis/.venv/` (Python 3.12, deps: mysql-connector-python, pandas). DB connection config in `analysis/config.py` — port must match current Docker mapping.

## Architecture

**Makefile-driven pipeline**: Download CSVs from NYC SODA API -> create schema -> LOAD DATA LOCAL INFILE -> add indexes. The Makefile handles all three database backends with parallel target naming (`mysql_*`, `psql_*`, `sqlite_*`).

**Docker Compose**: Each backend has its own compose file. The loader container (`acris-mysql`/`acris-psql`) runs `make` as its entrypoint, using the `ACRIS_DATASET` env var to select which target. Data is bind-mounted from `./data`.

**Database tables**: Five real property tables (`real_property_legals`, `real_property_master`, `real_property_parties`, `real_property_references`, `real_property_remarks`), five personal property tables with the same structure, and four reference/lookup tables. All linked by `documentid`. Schemas in `schema/`.

**Borough codes**: 1=Manhattan, 2=Bronx, 3=Brooklyn, 4=Queens, 5=Staten Island.

**Analysis module** (`analysis/`): Python scripts that connect to the running MySQL container to post-process data. Currently includes address normalization that groups raw addresses by BBL (Borough-Block-Lot) and produces the `normalized_addresses` table. See `analysis/NORMALIZED_ADDRESSES.md` for details.

## Key Makefile Variables

- `MYSQL_DATABASE` — defaults to `$(USER)`, overridden to `acris` in docker-compose
- `MYSQLFLAGS` / `PSQLFLAGS` — extra CLI flags passed to mysql/psql clients
- `PGSCHEMA` — PostgreSQL schema name, defaults to `acris`
- `ACRIS_DATASET` — controls which make target the Docker loader runs

## CI

GitHub Actions workflow at `.github/workflows/docker-test.yml` builds and tests both MySQL and PostgreSQL Docker images on push using sample data from `tests/data/`.
