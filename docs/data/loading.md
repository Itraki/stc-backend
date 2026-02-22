# Data Loading Guide

Guide for loading case data into the system.

## Quick Start

Load data from CSV files:

```bash
# Load local CSV files
python load_data.py --source csv --file data/cases.csv

# Load from Kenya API
python load_data.py --source kenya --year 2024
```

## CSV Format

Required columns:

```csv
case_id,status,severity,location,created_at,description
CASE-001,open,high,Nairobi,2024-01-15,Description here
```

## Kenya API Integration

Load data from Kenya's case management system:

```bash
# Load specific year
python load_data.py --source kenya --year 2024

# Load all available years
./load_local_data.sh
```

## Data Validation

Data is automatically validated:

- Case ID uniqueness
- Date format normalization
- Required field presence
- Data type validation

## Bulk Import

For large datasets:

```bash
# Import with progress tracking
python load_data.py --source csv --file large_dataset.csv --batch-size 1000
```

## Next Steps

- [Configuration](../getting-started/configuration.md)
- [API Reference](../api/overview.md)
