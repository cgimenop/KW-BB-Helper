# KW BB League - Excel Data Processor

A Python tool for managing Blood Bowl league data, processing Excel match reports, and generating league classifications.

## Features

- **League Generation**: Create round-robin tournament schedules from team rosters
- **Match Processing**: Read Excel match reports and extract team statistics
- **Classification**: Generate league tables with points, wins, draws, losses
- **Team Information**: Extract team names, logos, and colors from PDF files with Unicode normalization
- **Enhanced Tables**: Classification tables include team logos and colors with correct relative paths
- **Configurable Scoring**: Customizable point systems for league and star points
- **Pending Match Handling**: Matches with empty touchdowns are marked as pending without affecting standings
- **Injury Tracking**: Tracks injuries caused by each team from match reports
- **Test Mode**: Generate fixtures with random match data for testing
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
python generate_league.py <teams_json_path> <output_folder_path> [--cross-division] [--test-mode]
```

### Process Match Results
```bash
python update_classification.py <league_folder_path>
```

### Extract Team Information
```bash
python extract_team_info.py <league_folder_path>
```

### Examples
```bash
# Extract team info from PDFs
python extract_team_info.py league_output

# Generate division-only fixtures (default)
python generate_league.py league_output/Roosters/teams_info.json league_output

# Process match results and generate classifications
python update_classification.py league_output

# Generate with cross-division matches
python generate_league.py league_output/Roosters/teams_info.json league_output --cross-division

# Generate with test data (random touchdowns and injuries)
python generate_league.py league_output/Roosters/teams_info.json league_output --test-mode
```

## Folder Structure

### Workflow Structure
```
project/
├── league_output/      # Generated league structure
│   ├── Roosters/      # Team information
│   │   ├── Grupo 1/   # Division 1 team PDFs
│   │   ├── Grupo 2/   # Division 2 team PDFs
│   │   ├── logos/     # Extracted team logos
│   │   └── teams_info.json # Team data (names, colors, logos)
│   ├── Fixtures/      # All match fixtures
│   │   ├── Grupo 1/   # Division 1 fixtures
│   │   │   └── J1/, J2/... # Match date folders with Excel files
│   │   ├── Grupo 2/   # Division 2 fixtures
│   │   │   └── J1/, J2/... # Match date folders with Excel files
│   │   └── Cross-Division/ # Cross-division matches (optional)
│   │       └── J1/, J2/... # Match date folders
│   ├── Grupo 1/       # Division 1 classification
│   │   └── classification.md
│   ├── Grupo 2/       # Division 2 classification
│   │   └── classification.md
│   ├── league_data.json # Complete match results
│   └── league_classification.md # Combined classification
└── samples/clean/      # Excel template
```

## Output Files

### Single Division
- `league_output/league_data.json` - Complete match data by dates and teams
- `league_output/classification.md` - League classification table

### Multiple Divisions
- `league_output/league_data.json` - Complete match data by divisions, dates and teams
- `league_output/DivisionName/classification.md` - Division-specific classification tables (with ../ relative paths)
- `league_output/league_classification.md` - Combined classification with all divisions
- `league_output/Roosters/teams_info.json` - Team information (names, logos, colors)

## Match Status

- **Played**: Both teams have touchdown values - match counts toward standings (including injuries)
- **Pending**: Both teams have empty touchdown values - match displayed but doesn't affect standings
- **Partial**: One team has touchdown value, other is empty - empty treated as 0 and match is played

## Injuries

Injuries are tracked from the "Lesionados" row in match reports:
- Format: Comma-separated player numbers (e.g., "3,7,12")
- Each number represents a player who caused an injury to a rival
- Total injuries are accumulated in the classification table under the "INJ" column

## Configuration

- `league_points_cfg.json` - League points (win=3, draw=1, lose=0)
- `star_points_cfg.json` - Blood Bowl star points system

## Technical Details

- **Unicode Normalization**: Team names are normalized using NFC form to handle accented characters correctly
- **HTML Entity Decoding**: Handles HTML entities in PDF text extraction
- **Relative Paths**: Division-specific classifications use relative paths (../) for logo references
- **Injury Counting**: Injuries are counted from comma-separated player numbers in the "Lesionados" row
- **Test Mode**: Generates random touchdowns (0-5) and injuries (0-5 player numbers between 1-15)

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