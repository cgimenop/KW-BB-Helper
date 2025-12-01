# KW BB League - Excel Data Processor

A Python tool for managing Blood Bowl league data, processing Excel match reports, and generating league classifications.

## Features

- **League Generation**: Create round-robin tournament schedules from team rosters
- **Match Processing**: Read Excel match reports and extract team statistics
- **Classification**: Generate league tables with points, wins, draws, losses
- **Team Information**: Extract team names, logos, and colors from PDF files
- **Enhanced Tables**: Classification tables include team logos and colors
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
python generate_league.py <teams_json_path> <output_folder_path> [--cross-division]
```

### Process Match Results
```bash
python update_classification.py <league_folder_path>
```

### Extract Team Information
```bash
python extract_team_info.py
```

### Examples
```bash
# Generate division-only fixtures (default)
python extract_team_info.py
python generate_league.py tests/output/teams_info.json league_output
python update_classification.py league_output

# Generate with cross-division matches
python generate_league.py tests/output/teams_info.json league_output --cross-division
```

## Folder Structure

### Workflow Structure
```
project/
├── Reference/          # Team PDF files (Grupo 1, Grupo 2)
├── league_output/      # Generated league structure
│   └── Fixtures/      # All match fixtures
│       ├── Grupo 1/   # Division 1 fixtures
│       │   ├── J1/, J2/... # Match date folders
│       ├── Grupo 2/   # Division 2 fixtures
│       │   ├── J1/, J2/... # Match date folders
│       └── Cross-Division/ # Cross-division matches (optional)
│           ├── J1/, J2/... # Match date folders
├── tests/output/       # Generated reports and team info
│   ├── teams_info.json # Extracted team information
│   ├── league_data.json # Match results
│   └── *.md           # Classification tables
└── samples/clean/      # Excel template
```

## Output Files

### Single Division
- `tests/output/league_data.json` - Complete match data by dates and teams
- `tests/output/classification.md` - League classification table

### Multiple Divisions
- `tests/output/league_data.json` - Complete match data by divisions, dates and teams
- `tests/output/DivisionName/classification.md` - Division-specific classification tables
- `tests/output/league_classification.md` - Combined classification with all divisions
- `tests/output/teams_info.json` - Team information (names, logos, colors)

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