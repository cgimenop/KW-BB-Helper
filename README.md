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

### Extract Team Information
```bash
python extract_team_info.py <league_folder>
```

Extracts team data from PDF roster files and generates:
- `Rosters/teams_info.json` - Team names, divisions, colors, and base64 logos
- `Rosters/logos/*.png` - Individual team logo files

This must be run before generating league schedules.

### Generate League Schedule
```bash
python generate_league.py <league_folder> [--divisions N] [--pairings-json <path>] [--test-mode]
```

**Options:**
- `--divisions N`: Split teams randomly into N equal-sized divisions (requires teams to be evenly divisible)
- `--pairings-json <path>`: Use manual pairings from JSON file instead of automatic round-robin generation
- `--test-mode`: Generate random touchdowns (0-5) and injuries (0-5) for testing

### Process Match Results
```bash
python update_classification.py <league_folder>
```

### Examples
```bash
# Generate league from existing divisions
python generate_league.py league_folder

# Generate league and split 16 teams into 2 divisions
python generate_league.py league_folder --divisions 2

# Generate league from manual pairings JSON file
python generate_league.py league_folder --pairings-json samples/Rondas/manual_pairings.json

# Generate test league with random data
python generate_league.py league_folder --test-mode

# Process match results and generate classification
python update_classification.py league_folder
```

## Folder Structure

### Input Structure

The script expects a league folder with the following structure:

**Option 1: Pre-organized divisions**
```
league_folder/
└── Roosters/
    ├── Division 1/
    │   ├── Team1.pdf
    │   ├── Team2.pdf
    │   └── Team3.pdf
    └── Division 2/
        ├── Team4.pdf
        ├── Team5.pdf
        └── Team6.pdf
```

**Option 2: All teams in Roosters (use --divisions flag)**
```
league_folder/
└── Roosters/
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
league_folder/
├── Roosters/
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

## Manual Pairings

You can provide custom match pairings instead of automatic round-robin generation.

### Pairings JSON Format

Create a JSON file with this structure:

```json
{
  "J1": {
    "Division 1": [
      {"home": "Team A1", "away": "Team A2"},
      {"home": "Team A3", "away": "Team A4"}
    ],
    "Division 2": [
      {"home": "Team B1", "away": "Team B2"}
    ]
  },
  "J2": {
    "Division 1": [
      {"home": "Team A2", "away": "Team A3"}
    ]
  }
}
```

**Structure:**
- Top level: Round names (J1, J2, J3, etc.)
- Second level: Division names (must match folder names in Rosters/)
- Third level: Array of matches with `home` and `away` team names

**Example files:**
- `samples/Rondas/manual_pairings.json` - Real league example
- `samples/Rondas/manual_pairings_example.json` - Anonymized template

### Usage

```bash
python generate_league.py league_folder --pairings-json path/to/pairings.json
```

The script will:
1. Read team info from `Rosters/Division X/*.pdf` files
2. Create matches according to your pairings JSON
3. Generate Excel templates in `Fixtures/Division X/JY/`
4. Output `Fixtures/fixtures.json` with your custom pairings

## How It Works

### 1. Extract Team Information

The `extract_team_info.py` script:
- Scans `Rosters/` folder for team PDF files
- Detects divisions from subfolder structure (or assigns "Division 1" if all PDFs in root)
- Extracts team logos (first image in PDF)
- Extracts team colors from PDF text and background fills
- Saves `teams_info.json` with team data including division assignment
- Exports individual logo PNG files to `Rosters/logos/`

### 2. Generate League

The `generate_league.py` script:
- Scans the `Roosters` folder for team PDF files
- Detects existing divisions (subfolders) or creates them with `--divisions` flag
- Generates round-robin schedules for each division (or uses `--pairings-json` for custom pairings)
- Creates Excel match report templates in `Fixtures/` folder
- Outputs `fixtures.json` with all match pairings

### 3. Fill Match Reports

Manually fill in the Excel files in `Fixtures/Division X/JY/` with:
- Touchdowns (row 4, columns B and C)
- Leave empty if match not played

### 4. Generate Classification

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