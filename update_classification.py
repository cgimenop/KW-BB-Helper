#!/usr/bin/env python3
import sys
import json
from pathlib import Path
import pandas as pd

def load_settings():
    """Load point settings from league_points_cfg.json"""
    try:
        with open('league_points_cfg.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "league_points": {"win": 3, "draw": 1, "lose": 0},
            "sorting_criteria": [
                {"field": "points", "order": "desc"},
                {"field": "touchdowns", "order": "desc"},
                {"field": "wins", "order": "desc"}
            ]
        }

def process_date_folder(date_folder, date_data, settings):
    """Process Excel files in a date folder."""
    excel_files = list(date_folder.glob("*.xlsx")) + list(date_folder.glob("*.xls"))
    
    for file_path in excel_files:
        try:
            df = pd.read_excel(file_path, header=None)
            
            # Team B (column B)
            team_b = str(df.iloc[1, 1]) if len(df) > 1 and len(df.columns) > 1 else "Unknown_B"
            touchdowns_b = df.iloc[3, 1] if len(df) > 3 else None
            
            # Team C (column C)
            team_c = str(df.iloc[1, 2]) if len(df) > 1 and len(df.columns) > 2 else "Unknown_C"
            touchdowns_c = df.iloc[3, 2] if len(df) > 3 else None
            
            # Check if touchdowns are empty
            td_b_empty = pd.isna(touchdowns_b) or str(touchdowns_b).strip() == ''
            td_c_empty = pd.isna(touchdowns_c) or str(touchdowns_c).strip() == ''
            
            # If both empty, skip this match (not played)
            if td_b_empty and td_c_empty:
                continue
            
            # If one is empty, treat as 0
            if td_b_empty:
                touchdowns_b = 0
            if td_c_empty:
                touchdowns_c = 0
            
            # Determine match result
            if touchdowns_b > touchdowns_c:
                result_b, result_c = "win", "lose"
            elif touchdowns_b < touchdowns_c:
                result_b, result_c = "lose", "win"
            else:
                result_b = result_c = "draw"
            
            if team_b != "nan":
                date_data[team_b] = {
                    "touchdowns": touchdowns_b,
                    "cash": df.iloc[4, 1] if len(df) > 4 else 0,
                    "fans": df.iloc[5, 1] if len(df) > 5 else 0,
                    "attendants": df.iloc[6, 1] if len(df) > 6 else 0,
                    "result": result_b,
                    "rival": team_c,
                    "points": settings["league_points"][result_b]
                }
            
            if team_c != "nan":
                date_data[team_c] = {
                    "touchdowns": touchdowns_c,
                    "cash": df.iloc[4, 2] if len(df) > 4 else 0,
                    "fans": df.iloc[5, 2] if len(df) > 5 else 0,
                    "attendants": df.iloc[6, 2] if len(df) > 6 else 0,
                    "result": result_c,
                    "rival": team_b,
                    "points": settings["league_points"][result_c]
                }
            
            print(f"Processed: {date_folder.parent.name}/{date_folder.name}/{file_path.name} - {team_b} vs {team_c}")
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")

def read_excel_files(folder_path):
    """Read Excel files from division and date subfolders and extract team data to JSON."""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    # Look for Fixtures subfolder
    fixtures_folder = folder / "Fixtures"
    if fixtures_folder.exists():
        folder = fixtures_folder
    
    settings = load_settings()
    league_data = {}
    
    # Check if there are division folders or direct date folders
    has_divisions = any(d.is_dir() and any(sub.is_dir() and sub.name.startswith('J') for sub in d.iterdir()) for d in folder.iterdir())
    
    if has_divisions:
        # Process divisions
        for division_folder in folder.iterdir():
            if not division_folder.is_dir():
                continue
            
            division_name = division_folder.name
            league_data[division_name] = {}
            
            for date_folder in division_folder.iterdir():
                if not date_folder.is_dir():
                    continue
                    
                date_name = date_folder.name
                league_data[division_name][date_name] = {}
                
                process_date_folder(date_folder, league_data[division_name][date_name], settings)
    else:
        # Process direct date folders (legacy mode)
        for date_folder in folder.iterdir():
            if not date_folder.is_dir():
                continue
                
            date_name = date_folder.name
            league_data[date_name] = {}
            
            process_date_folder(date_folder, league_data[date_name], settings)
    
    # Output to Classification folder in the original folder_path (not Fixtures)
    output_folder = Path(folder_path) / "Classification"
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / "league_data.json"
    
    with open(output_file, 'w') as f:
        json.dump(league_data, f, indent=2)
    
    # Generate classification tables
    if has_divisions:
        # Generate division-specific tables
        for division_name, division_data in league_data.items():
            if isinstance(division_data, dict):
                division_output_folder = output_folder / division_name
                division_output_folder.mkdir(exist_ok=True)
                division_fixtures_folder = folder / division_name
                generate_classification_table(division_data, division_output_folder, division_fixtures_folder)
        
        # Generate overall league classification
        generate_overall_classification(league_data, output_folder, folder)
    else:
        # No divisions
        generate_classification_table(league_data, output_folder, folder)
    
    print(f"\nData saved to: {output_file}")

def generate_classification_table(league_data, output_folder, fixtures_folder=None):
    """Generate classification table in markdown format"""
    settings = load_settings()
    teams_stats = {}
    
    # Initialize all teams from fixtures if provided
    if fixtures_folder:
        for date_folder in fixtures_folder.iterdir():
            if date_folder.is_dir():
                for excel_file in date_folder.glob("*.xlsx"):
                    try:
                        df = pd.read_excel(excel_file, header=None)
                        team_b = str(df.iloc[1, 1]) if len(df) > 1 and len(df.columns) > 1 else None
                        team_c = str(df.iloc[1, 2]) if len(df) > 1 and len(df.columns) > 2 else None
                        if team_b and team_b != "nan":
                            if team_b not in teams_stats:
                                teams_stats[team_b] = {"points": 0, "wins": 0, "draws": 0, "losses": 0, "touchdowns": 0}
                        if team_c and team_c != "nan":
                            if team_c not in teams_stats:
                                teams_stats[team_c] = {"points": 0, "wins": 0, "draws": 0, "losses": 0, "touchdowns": 0}
                    except:
                        pass
    
    # Calculate total stats for each team
    for date, teams in league_data.items():
        for team, data in teams.items():
            if team not in teams_stats:
                teams_stats[team] = {"points": 0, "wins": 0, "draws": 0, "losses": 0, "touchdowns": 0}
            
            teams_stats[team]["points"] += data["points"]
            teams_stats[team]["touchdowns"] += data["touchdowns"]
            
            if data["result"] == "win":
                teams_stats[team]["wins"] += 1
            elif data["result"] == "draw":
                teams_stats[team]["draws"] += 1
            else:
                teams_stats[team]["losses"] += 1
    
    # Sort teams using configurable criteria
    sorting_criteria = settings.get("sorting_criteria", [
        {"field": "points", "order": "desc"},
        {"field": "touchdowns", "order": "desc"},
        {"field": "wins", "order": "desc"}
    ])
    
    def sort_key(item):
        team_stats = item[1]
        return tuple(
            team_stats.get(criterion["field"], 0) * (-1 if criterion["order"] == "desc" else 1)
            for criterion in sorting_criteria
        )
    
    sorted_teams = sorted(teams_stats.items(), key=sort_key)
    
    # Generate markdown table
    markdown = "# League Classification\n\n"
    markdown += "| Pos | Team | Points | W | D | L | TD |\n"
    markdown += "|-----|------|--------|---|---|---|----|\n"
    
    for pos, (team, stats) in enumerate(sorted_teams, 1):
        markdown += f"| {pos} | {team} | {stats['points']} | {stats['wins']} | {stats['draws']} | {stats['losses']} | {stats['touchdowns']} |\n"
    
    # Save markdown file
    markdown_file = output_folder / "classification.md"
    with open(markdown_file, 'w') as f:
        f.write(markdown)
    
    print(f"Classification table saved to: {markdown_file}")

def generate_overall_classification(league_data, output_folder, fixtures_folder):
    """Generate league classification with separate tables for each division"""
    settings = load_settings()
    markdown = "# League Classification\n\n"
    
    # Generate table for each division
    for division_name, division_data in league_data.items():
        teams_stats = {}
        
        # Initialize all teams from fixtures
        division_fixtures_folder = fixtures_folder / division_name
        if division_fixtures_folder.exists():
            for date_folder in division_fixtures_folder.iterdir():
                if date_folder.is_dir():
                    for excel_file in date_folder.glob("*.xlsx"):
                        try:
                            df = pd.read_excel(excel_file, header=None)
                            team_b = str(df.iloc[1, 1]) if len(df) > 1 and len(df.columns) > 1 else None
                            team_c = str(df.iloc[1, 2]) if len(df) > 1 and len(df.columns) > 2 else None
                            if team_b and team_b != "nan":
                                if team_b not in teams_stats:
                                    teams_stats[team_b] = {"points": 0, "wins": 0, "draws": 0, "losses": 0, "touchdowns": 0}
                            if team_c and team_c != "nan":
                                if team_c not in teams_stats:
                                    teams_stats[team_c] = {"points": 0, "wins": 0, "draws": 0, "losses": 0, "touchdowns": 0}
                        except:
                            pass
        
        # Calculate stats for this division
        for date, teams in division_data.items():
            for team, data in teams.items():
                if team not in teams_stats:
                    teams_stats[team] = {"points": 0, "wins": 0, "draws": 0, "losses": 0, "touchdowns": 0}
                
                teams_stats[team]["points"] += data["points"]
                teams_stats[team]["touchdowns"] += data["touchdowns"]
                
                if data["result"] == "win":
                    teams_stats[team]["wins"] += 1
                elif data["result"] == "draw":
                    teams_stats[team]["draws"] += 1
                else:
                    teams_stats[team]["losses"] += 1
        
        # Sort teams using configurable criteria
        sorting_criteria = settings.get("sorting_criteria", [
            {"field": "points", "order": "desc"},
            {"field": "touchdowns", "order": "desc"},
            {"field": "wins", "order": "desc"}
        ])
        
        def sort_key(item):
            team_stats = item[1]
            return tuple(
                team_stats.get(criterion["field"], 0) * (-1 if criterion["order"] == "desc" else 1)
                for criterion in sorting_criteria
            )
        
        sorted_teams = sorted(teams_stats.items(), key=sort_key)
        
        # Add division header and table
        markdown += f"## {division_name}\n\n"
        markdown += "| Pos | Team | Points | W | D | L | TD |\n"
        markdown += "|-----|------|--------|---|---|---|----|\n"
        
        for pos, (team, stats) in enumerate(sorted_teams, 1):
            markdown += f"| {pos} | {team} | {stats['points']} | {stats['wins']} | {stats['draws']} | {stats['losses']} | {stats['touchdowns']} |\n"
        
        markdown += "\n"
    
    # Save markdown file
    markdown_file = output_folder / "league_classification.md"
    with open(markdown_file, 'w') as f:
        f.write(markdown)
    
    print(f"League classification saved to: {markdown_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_excel_files.py <league_folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    read_excel_files(folder_path)