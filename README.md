# KW BB League - Excel Data Processor

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

Run the script with the league folder path:
```bash
python read_excel_files.py <league_folder_path>
```

### Example:
```bash
python read_excel_files.py samples
```

## Folder Structure

The league folder should contain subfolders for each match date (J1, J2, J3, etc.), with Excel files inside each subfolder.

## Output

- `tests/output/league_data.json` - Complete match data by dates and teams
- `tests/output/classification.md` - League classification table in markdown format

## Configuration Files

- `league_points_cfg.json` - League points system (win=3, draw=1, lose=0)
- `star_points_cfg.json` - Star points system for Blood Bowl rules