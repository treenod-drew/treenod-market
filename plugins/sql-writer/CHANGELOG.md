# Changelog

## 1.0.1 - 2026-01-05

### Fixed
- `sample.py`: Skip adding LIMIT clause for DESCRIBE, SHOW, EXPLAIN commands
  - Previously, these commands failed with syntax error when LIMIT was appended
  - Example: `DESCRIBE DETAIL table LIMIT 10` caused parse error

## 1.0.0 - Initial Release

### Added
- `schema.py`: Table metadata and schema inspection
- `validate.py`: Query validation with EXPLAIN plan
- `sample.py`: Execute queries with partition filter check
- `utils.py`: Shared utilities for Databricks connection
- Reference documentation for game databases
