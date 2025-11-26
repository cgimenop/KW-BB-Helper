# KW BB League - Excel Data Processor

A Python tool for managing Blood Bowl league data, processing Excel match reports, and generating league classifications.

## Features

- **League Generation**: Create round-robin tournament schedules from team rosters
- **Match Processing**: Read Excel match reports and extract team statistics
- **Classification**: Generate league tables with points, wins, draws, losses
- **Configurable Scoring**: Customizable point systems for league and star points
- **Automated Reports**: Output JSON data and Markdown classification tables

## Installation

1. Create virtual environment:
```bash
python3 -m venv venv
```

2. Activate virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Generate League Schedule
```bash
python generate_league.py <roosters_folder_path>
```

### Process Match Results
```bash
python update_classification.py <league_folder_path>
```

### Examples
```bash
python generate_league.py roosters
python update_classification.py samples
```

## Folder Structure

### Single Division (Legacy)
```
project/
├── roosters/           # Team roster files
├── J1/, J2/, J3/...   # Match date folders (auto-generated)
├── tests/output/       # Generated reports
└── samples/clean/      # Excel template
```

### Multiple Divisions
```
project/
├── roosters/           # Team roster files
├── Division1/          # Division folder
│   ├── J1/, J2/...    # Match date folders
├── Division2/          # Division folder
│   ├── J1/, J2/...    # Match date folders
├── tests/output/       # Generated reports
│   ├── Division1/     # Division-specific reports
│   └── Division2/     # Division-specific reports
└── samples/clean/      # Excel template
```

## Output Files

### Single Division
- `tests/output/league_data.json` - Complete match data by dates and teams
- `tests/output/classification.md` - League classification table

### Multiple Divisions
- `tests/output/league_data.json` - Complete match data by divisions, dates and teams
- `tests/output/DivisionName/classification.md` - Division-specific classification tables

## Configuration

- `league_points_cfg.json` - League points (win=3, draw=1, lose=0)
- `star_points_cfg.json` - Blood Bowl star points system

## Development

### Run Tests
```bash
./scripts/run_coverage.sh
```

### Static Analysis
```bash
./scripts/run_static_analysis.sh
```

### Test Coverage
Current coverage: **88%**

## License

MIT License - see LICENSE file for details