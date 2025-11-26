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
        return {"league_points": {"win": 3, "draw": 1, "lose": 0}}

def read_excel_files(folder_path):
    """Read Excel files from date subfolders and extract team data to JSON."""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    settings = load_settings()
    league_data = {}
    
    for date_folder in folder.iterdir():
        if not date_folder.is_dir():
            continue
            
        date_name = date_folder.name
        league_data[date_name] = {}
        
        excel_files = list(date_folder.glob("*.xlsx")) + list(date_folder.glob("*.xls"))
        
        for file_path in excel_files:
            try:
                df = pd.read_excel(file_path, header=None)
                
                # Team B (column B)
                team_b = str(df.iloc[1, 1]) if len(df) > 1 and len(df.columns) > 1 else "Unknown_B"
                touchdowns_b = df.iloc[3, 1] if len(df) > 3 else 0
                
                # Team C (column C)
                team_c = str(df.iloc[1, 2]) if len(df) > 1 and len(df.columns) > 2 else "Unknown_C"
                touchdowns_c = df.iloc[3, 2] if len(df) > 3 else 0
                
                # Determine match result
                if touchdowns_b > touchdowns_c:
                    result_b, result_c = "win", "lose"
                elif touchdowns_b < touchdowns_c:
                    result_b, result_c = "lose", "win"
                else:
                    result_b = result_c = "draw"
                
                if team_b != "nan":
                    league_data[date_name][team_b] = {
                        "touchdowns": touchdowns_b,
                        "cash": df.iloc[4, 1] if len(df) > 4 else 0,
                        "fans": df.iloc[5, 1] if len(df) > 5 else 0,
                        "attendants": df.iloc[6, 1] if len(df) > 6 else 0,
                        "result": result_b,
                        "rival": team_c,
                        "points": settings["league_points"][result_b]
                    }
                
                if team_c != "nan":
                    league_data[date_name][team_c] = {
                        "touchdowns": touchdowns_c,
                        "cash": df.iloc[4, 2] if len(df) > 4 else 0,
                        "fans": df.iloc[5, 2] if len(df) > 5 else 0,
                        "attendants": df.iloc[6, 2] if len(df) > 6 else 0,
                        "result": result_c,
                        "rival": team_b,
                        "points": settings["league_points"][result_c]
                    }
                
                print(f"Processed: {date_name}/{file_path.name} - {team_b} vs {team_c}")
            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")
    
    output_folder = Path("tests/output")
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / "league_data.json"
    
    with open(output_file, 'w') as f:
        json.dump(league_data, f, indent=2)
    
    # Generate classification table
    generate_classification_table(league_data, output_folder)
    
    print(f"\nData saved to: {output_file}")

def generate_classification_table(league_data, output_folder):
    """Generate classification table in markdown format"""
    settings = load_settings()
    teams_stats = {}
    
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
    
    # Sort teams by points (descending)
    sorted_teams = sorted(teams_stats.items(), key=lambda x: x[1]["points"], reverse=True)
    
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_excel_files.py <league_folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    read_excel_files(folder_path)