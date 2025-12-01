#!/usr/bin/env python3
import sys
import json
from pathlib import Path
import pandas as pd
import base64

def load_settings():
    """Load point settings from league_points_cfg.json"""
    try:
        with open('league_points_cfg.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"league_points": {"win": 3, "draw": 1, "lose": 0}}

def process_date_folder(date_folder, date_data, settings, league_path):
    """Process Excel files in a date folder."""
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

            # Load team info for logos and colors
            team_info = load_team_info(league_path)

            if team_b != "nan":
                team_b_info = team_info.get(team_b, {})
                date_data[team_b] = {
                    "touchdowns": touchdowns_b,
                    "cash": df.iloc[4, 1] if len(df) > 4 else 0,
                    "fans": df.iloc[5, 1] if len(df) > 5 else 0,
                    "attendants": df.iloc[6, 1] if len(df) > 6 else 0,
                    "result": result_b,
                    "rival": team_c,
                    "points": settings["league_points"][result_b],
                    "logo_base64": team_b_info.get("logo_base64", ""),
                    "font_color": team_b_info.get("font_color", "#000000"),
                    "background_color": team_b_info.get("background_color", "#ffffff")
                }

            if team_c != "nan":
                team_c_info = team_info.get(team_c, {})
                date_data[team_c] = {
                    "touchdowns": touchdowns_c,
                    "cash": df.iloc[4, 2] if len(df) > 4 else 0,
                    "fans": df.iloc[5, 2] if len(df) > 5 else 0,
                    "attendants": df.iloc[6, 2] if len(df) > 6 else 0,
                    "result": result_c,
                    "rival": team_b,
                    "points": settings["league_points"][result_c],
                    "logo_base64": team_c_info.get("logo_base64", ""),
                    "font_color": team_c_info.get("font_color", "#000000"),
                    "background_color": team_c_info.get("background_color", "#ffffff")
                }

            print(f"Processed: {date_folder.parent.name}/{date_folder.name}/{file_path.name} - {team_b} vs {team_c}")
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")

def read_excel_files(folder_path):
    """Read Excel files from Fixtures subfolder and extract team data to JSON."""
    folder = Path(folder_path)
    fixtures_folder = folder / "Fixtures"

    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    if not fixtures_folder.exists():
        print(f"Error: Fixtures folder not found in '{folder_path}'")
        return

    settings = load_settings()
    league_data = {}

    # Check if there are division folders or direct date folders in Fixtures
    has_divisions = any(d.is_dir() and any(sub.is_dir() and sub.name.startswith('J') for sub in d.iterdir()) for d in fixtures_folder.iterdir())

    if has_divisions:
        # Process divisions in Fixtures folder
        for division_folder in fixtures_folder.iterdir():
            if not division_folder.is_dir():
                continue

            division_name = division_folder.name
            league_data[division_name] = {}

            for date_folder in division_folder.iterdir():
                if not date_folder.is_dir():
                    continue

                date_name = date_folder.name
                league_data[division_name][date_name] = {}

                process_date_folder(date_folder, league_data[division_name][date_name], settings, folder_path)
    else:
        # Process direct date folders in Fixtures (legacy mode)
        for date_folder in fixtures_folder.iterdir():
            if not date_folder.is_dir():
                continue

            date_name = date_folder.name
            league_data[date_name] = {}

            process_date_folder(date_folder, league_data[date_name], settings, folder_path)

    output_folder = Path("tests/output")
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / "league_data.json"

    with open(output_file, 'w') as f:
        json.dump(league_data, f, indent=2)

    # Generate classification tables
    if has_divisions:
        # Generate division-specific tables
        for division_name, division_data in league_data.items():
            if isinstance(division_data, dict) and division_data:
                division_output_folder = output_folder / division_name
                division_output_folder.mkdir(exist_ok=True)
                generate_classification_table(division_data, division_output_folder, folder_path)

        # Generate overall league classification
        generate_overall_classification(league_data, output_folder, folder_path)
    else:
        # No divisions
        generate_classification_table(league_data, output_folder, folder_path)

    print(f"\nData saved to: {output_file}")

def load_team_info(league_path):
    """Load team information from Roosters/teams_info.json"""
    path = Path(league_path) / "Roosters" / "teams_info.json"

    try:
        with open(path, 'r') as f:
            data = json.load(f)
            print(f"Loaded team info from: {path}")
            return data
    except FileNotFoundError:
        print(f"Warning: teams_info.json not found at {path}")
    return {}

def save_team_logos(teams_stats, output_folder):
    """Save team logos as image files"""
    logos_folder = output_folder / "logos"
    logos_folder.mkdir(exist_ok=True)
    
    for team, stats in teams_stats.items():
        logo_base64 = stats.get('logo_base64', '')
        if logo_base64:
            try:
                logo_data = base64.b64decode(logo_base64)
                logo_file = logos_folder / f"{team.replace(' ', '_').replace('/', '_')}.png"
                with open(logo_file, 'wb') as f:
                    f.write(logo_data)
                stats['logo_file'] = f"logos/{logo_file.name}"
            except Exception as e:
                print(f"Error saving logo for {team}: {e}")
                stats['logo_file'] = None
        else:
            stats['logo_file'] = None

def generate_classification_table(league_data, output_folder, folder_path):
    """Generate classification table in markdown format"""
    settings = load_settings()
    team_info = load_team_info(folder_path)
    teams_stats = {}

    # Calculate total stats for each team
    for date, teams in league_data.items():
        for team, data in teams.items():
            if team not in teams_stats:
                teams_stats[team] = {
                    "points": 0, "wins": 0, "draws": 0, "losses": 0, "touchdowns": 0,
                    "logo_base64": data.get("logo_base64", ""),
                    "font_color": data.get("font_color", "#000000"),
                    "background_color": data.get("background_color", "#ffffff")
                }

            teams_stats[team]["points"] += data["points"]
            teams_stats[team]["touchdowns"] += data["touchdowns"]

            if data["result"] == "win":
                teams_stats[team]["wins"] += 1
            elif data["result"] == "draw":
                teams_stats[team]["draws"] += 1
            else:
                teams_stats[team]["losses"] += 1

    # Save team logos as files
    save_team_logos(teams_stats, output_folder)

    # Sort teams by points (descending)
    sorted_teams = sorted(teams_stats.items(), key=lambda x: x[1]["points"], reverse=True)

    # Generate markdown table
    markdown = "# League Classification\n\n"
    markdown += "| Pos | Logo | Color | Team | Points | W | D | L | TD |\n"
    markdown += "|-----|------|-------|------|--------|---|---|---|----|\n"

    for pos, (team, stats) in enumerate(sorted_teams, 1):
        logo = f"<img src='{stats['logo_file']}' width='20' height='20' alt='{team}'>" if stats.get('logo_file') else "N/A"
        bg_square = f"<span style='color:{stats.get('background_color', '#ffffff')}'>■</span>"
        font_square = f"<span style='color:{stats.get('font_color', '#000000')}'>■</span>"
        color = f"{bg_square}{font_square}"
        markdown += f"| {pos} | {logo} | {color} | {team} | {stats['points']} | {stats['wins']} | {stats['draws']} | {stats['losses']} | {stats['touchdowns']} |\n"

    # Add calendar with results
    markdown += "\n## Calendar\n\n"
    
    # Group matches by date
    dates = sorted(league_data.keys())
    for date in dates:
        markdown += f"### {date}\n\n"
        markdown += "| Match | Team 1 | Score | Team 2 | Status |\n"
        markdown += "|:-----:|:-------|:-----:|:-------|:------:|\n"
        
        teams = league_data[date]
        match_num = 1
        
        # Create match pairs
        team_list = list(teams.keys())
        for i in range(0, len(team_list), 2):
            if i + 1 < len(team_list):
                team1 = team_list[i]
                team2 = team_list[i + 1]
                data1 = teams[team1]
                data2 = teams[team2]
                
                # Check if match was played
                if str(data1['touchdowns']) != 'nan' and str(data2['touchdowns']) != 'nan':
                    score = f"{data1['touchdowns']} - {data2['touchdowns']}"
                    status = "✅ Played"
                else:
                    score = "- vs -"
                    status = "⏳ Pending"
                
                # Get team logos
                team1_stats = teams_stats.get(team1, {})
                team2_stats = teams_stats.get(team2, {})
                team1_logo = f"<img src='{team1_stats.get('logo_file', '')}' width='20' height='20' alt='{team1}'> **{team1}**" if team1_stats.get('logo_file') else f"**{team1}**"
                team2_logo = f"<img src='{team2_stats.get('logo_file', '')}' width='20' height='20' alt='{team2}'> **{team2}**" if team2_stats.get('logo_file') else f"**{team2}**"
                
                markdown += f"| {match_num} | {team1_logo} | {score} | {team2_logo} | {status} |\n"
                match_num += 1
        markdown += "\n"

    # Save markdown file
    markdown_file = output_folder / "classification.md"
    with open(markdown_file, 'w') as f:
        f.write(markdown)

    print(f"Classification table saved to: {markdown_file}")

def generate_overall_classification(league_data, output_folder, folder_path):
    """Generate league classification with separate tables for each division"""
    team_info = load_team_info(folder_path)
    markdown = "# League Classification\n\n"
    all_teams_stats = {}

    # Generate table for each division
    for division_name, division_data in league_data.items():
        teams_stats = {}

        # Calculate stats for this division
        for date, teams in division_data.items():
            for team, data in teams.items():
                if team not in teams_stats:
                    teams_stats[team] = {
                        "points": 0, "wins": 0, "draws": 0, "losses": 0, "touchdowns": 0,
                        "logo_base64": data.get("logo_base64", ""),
                        "font_color": data.get("font_color", "#000000"),
                        "background_color": data.get("background_color", "#ffffff")
                    }

                teams_stats[team]["points"] += data["points"]
                teams_stats[team]["touchdowns"] += data["touchdowns"]

                if data["result"] == "win":
                    teams_stats[team]["wins"] += 1
                elif data["result"] == "draw":
                    teams_stats[team]["draws"] += 1
                else:
                    teams_stats[team]["losses"] += 1

        # Collect all teams for logo saving
        all_teams_stats.update(teams_stats)

        # Sort teams by points (descending)
        sorted_teams = sorted(teams_stats.items(), key=lambda x: x[1]["points"], reverse=True)

        # Add division header and table
        markdown += f"## {division_name}\n\n"
        markdown += "| Pos | Logo | Color | Team | Points | W | D | L | TD |\n"
        markdown += "|-----|------|-------|------|--------|---|---|---|----|\n"

        for pos, (team, stats) in enumerate(sorted_teams, 1):
            logo = f"<img src='logos/{team.replace(' ', '_').replace('/', '_')}.png' width='20' height='20' alt='{team}'>" if stats.get('logo_base64') else "N/A"
            bg_square = f"<span style='color:{stats.get('background_color', '#ffffff')}'>■</span>"
            font_square = f"<span style='color:{stats.get('font_color', '#000000')}'>■</span>"
            color = f"{bg_square}{font_square}"
            markdown += f"| {pos} | {logo} | {color} | {team} | {stats['points']} | {stats['wins']} | {stats['draws']} | {stats['losses']} | {stats['touchdowns']} |\n"

        # Add calendar for this division
        markdown += f"### {division_name} Calendar\n\n"
        dates = sorted(division_data.keys())
        for date in dates:
            markdown += f"#### {date}\n\n"
            markdown += "| Match | Team 1 | Score | Team 2 | Status |\n"
            markdown += "|:-----:|:-------|:-----:|:-------|:------:|\n"
            
            teams = division_data[date]
            match_num = 1
            
            # Create match pairs
            team_list = list(teams.keys())
            for i in range(0, len(team_list), 2):
                if i + 1 < len(team_list):
                    team1 = team_list[i]
                    team2 = team_list[i + 1]
                    data1 = teams[team1]
                    data2 = teams[team2]
                    
                    # Check if match was played
                    if str(data1['touchdowns']) != 'nan' and str(data2['touchdowns']) != 'nan':
                        score = f"{data1['touchdowns']} - {data2['touchdowns']}"
                        status = "✅ Played"
                    else:
                        score = "- vs -"
                        status = "⏳ Pending"
                    
                    # Get team logos from all_teams_stats
                    team1_stats = all_teams_stats.get(team1, {})
                    team2_stats = all_teams_stats.get(team2, {})
                    team1_logo = f"<img src='logos/{team1.replace(' ', '_').replace('/', '_')}.png' width='20' height='20' alt='{team1}'> **{team1}**" if team1_stats.get('logo_base64') else f"**{team1}**"
                    team2_logo = f"<img src='logos/{team2.replace(' ', '_').replace('/', '_')}.png' width='20' height='20' alt='{team2}'> **{team2}**" if team2_stats.get('logo_base64') else f"**{team2}**"
                    
                    markdown += f"| {match_num} | {team1_logo} | {score} | {team2_logo} | {status} |\n"
                    match_num += 1
            markdown += "\n"
        
        markdown += "\n"

    # Save all team logos
    save_team_logos(all_teams_stats, output_folder)

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