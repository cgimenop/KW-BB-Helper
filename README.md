# KW BB League - Blood Bowl League Manager

A Python tool for managing Blood Bowl league data, processing Excel match reports, and generating league classifications with automatic fixture generation.

## Features

- **League Generation**: Create round-robin tournament schedules from team rosters
- **Division Support**: Automatic division detection or random team splitting
- **Match Processing**: Read Excel match reports and extract team statistics
- **Classification**: Generate league tables with points, wins, draws, losses, touchdowns
- **Configurable Sorting**: Customizable classification sorting criteria
- **Fixtures JSON**: Automatic generation of fixtures in JSON format
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
python generate_league.py <league_folder_path> [--divisions N]
```

**Options:**
- `--divisions N`: Split teams randomly into N equal-sized divisions (requires teams to be evenly divisible)

### Process Match Results
```bash
python update_classification.py <league_folder_path>
```

### Examples
```bash
# Generate league from existing divisions
python generate_league.py league_output

# Generate league and split 16 teams into 2 divisions
python generate_league.py league_output --divisions 2

# Process match results and generate classification
python update_classification.py league_output
```

## Folder Structure

### Input Structure

The script expects a league folder with the following structure:

**Option 1: Pre-organized divisions**
```
league_output/
└── Rosters/
    ├── Division 1/
    │   ├── Team1.pdf
    │   ├── Team2.pdf
    │   └── Team3.pdf
    └── Division 2/
        ├── Team4.pdf
        ├── Team5.pdf
        └── Team6.pdf
```

**Option 2: All teams in Rosters (use --divisions flag)**
```
league_output/
└── Rosters/
    ├── Team1.pdf
    ├── Team2.pdf
    ├── Team3.pdf
    ├── Team4.pdf
    ├── Team5.pdf
    └── Team6.pdf
```

### Output Structure

After running `generate_league.py` and `update_classification.py`:

```
league_output/
├── Rosters/
│   ├── Division 1/          # Division folders with team PDFs
│   └── Division 2/
├── Fixtures/
│   ├── fixtures.json     # Generated fixtures in JSON format
│   ├── Division 1/
│   │   ├── J1/           # Match date folders
│   │   │   ├── Match_1_Team1_vs_Team2.xlsx
│   │   │   └── Match_2_Team3_vs_Team4.xlsx
│   │   └── J2/
│   └── Division 2/
│       ├── J1/
│       └── J2/
└── Classification/
    ├── league_data.json           # Complete match data
    ├── league_classification.md   # Overall classification
    ├── Division 1/
    │   └── classification.md      # Division-specific classification
    └── Division 2/
        └── classification.md
```

## Output Files

### Fixtures Folder
- `Fixtures/fixtures.json` - Generated fixtures in JSON format (compatible with manual pairings)
- `Fixtures/Division X/JY/*.xlsx` - Excel match report templates

### Classification Folder
- `Classification/league_data.json` - Complete match data by divisions, dates and teams
- `Classification/league_classification.md` - Combined classification with all divisions
- `Classification/Division X/classification.md` - Division-specific classification tables

## Match Processing

### Match Status
- **Not Played**: Both touchdown fields are empty - match is skipped in classification
- **Played**: Both teams have touchdown values - match counts toward standings
- **Partial**: One team has touchdown value, other is empty - empty treated as 0

## Configuration

### league_points_cfg.json

Configures league points and classification sorting criteria:

```json
{
  "league_points": {
    "win": 3,
    "draw": 1,
    "lose": 0
  },
  "sorting_criteria": [
    {"field": "points", "order": "desc"},
    {"field": "touchdowns", "order": "desc"},
    {"field": "wins", "order": "desc"}
  ]
}
```

**Sorting Criteria:**
- Teams are sorted by multiple criteria in order (first is primary, second is tiebreaker, etc.)
- Available fields: `"points"`, `"wins"`, `"draws"`, `"losses"`, `"touchdowns"`
- Order: `"desc"` (descending/highest first) or `"asc"` (ascending/lowest first)

**Example configurations:**

Prioritize goal difference over wins:
```json
"sorting_criteria": [
  {"field": "points", "order": "desc"},
  {"field": "touchdowns", "order": "desc"},
  {"field": "losses", "order": "asc"}
]
```

### star_points_cfg.json

Blood Bowl star points system configuration

## How It Works

### 1. Generate League

The `generate_league.py` script:
- Scans the `Rosters` folder for team PDF files
- Detects existing divisions (subfolders) or creates them with `--divisions` flag
- Generates round-robin schedules for each division
- Creates Excel match report templates in `Fixtures/` folder
- Outputs `fixtures.json` with all match pairings

### 2. Fill Match Reports

Manually fill in the Excel files in `Fixtures/Division X/JY/` with:
- Touchdowns (row 4, columns B and C)
- Leave empty if match not played

### 3. Generate Classification

The `update_classification.py` script:
- Reads all Excel files from `Fixtures/` folder
- Processes only matches with touchdown data
- Calculates points, wins, draws, losses
- Sorts teams according to `sorting_criteria` in config
- Generates classification tables in `Classification/` folder
- Lists all teams even if no matches played yet

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