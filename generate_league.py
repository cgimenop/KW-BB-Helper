#!/usr/bin/env python3
import sys
import json
import shutil
from pathlib import Path
from itertools import combinations
import openpyxl



def load_teams_with_divisions(teams_json_path):
    """Load teams grouped by division from teams_info.json"""
    try:
        with open(teams_json_path, 'r') as f:
            teams_data = json.load(f)
            divisions = {}
            for team_name, team_info in teams_data.items():
                group = team_info.get('group', 'Unknown')
                if group not in divisions:
                    divisions[group] = []
                divisions[group].append(team_name)
            return divisions
    except FileNotFoundError:
        print(f"Error: {teams_json_path} not found.")
        return {}

def generate_division_schedule(teams):
    """Generate round-robin schedule for a division"""
    n = len(teams)
    if n % 2 == 1:
        teams.append("BYE")
        n += 1
    
    schedule = []
    for round_num in range(n - 1):
        round_matches = []
        for i in range(n // 2):
            team1 = teams[i]
            team2 = teams[n - 1 - i]
            if team1 != "BYE" and team2 != "BYE":
                round_matches.append((team1, team2))
        schedule.append(round_matches)
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    
    return schedule

def generate_league(teams_json_path, output_folder, cross_division=False, pairings_json=None):
    """Generate league pairings and create match templates for each division."""
    output_path = Path(output_folder)
    fixtures_path = output_path / "Fixtures"
    
    if not output_path.exists():
        output_path.mkdir(parents=True)
    
    # Get teams grouped by division
    divisions = load_teams_with_divisions(teams_json_path)
    
    if not divisions:
        print("No teams found.")
        return
    
    template_path = Path("samples/clean/Hoja Limpia Acta.xlsx")
    
    if not template_path.exists():
        print(f"Template file not found: {template_path}")
        return
    
    # Wipe previous fixtures folder
    if fixtures_path.exists():
        shutil.rmtree(fixtures_path)
        print(f"Removed: {fixtures_path}")
    
    fixtures_path.mkdir(exist_ok=True)
    
    total_teams = 0
    total_matches = 0
    
    # Generate fixtures from JSON or automatically
    if pairings_json:
        with open(pairings_json, 'r') as f:
            pairings = json.load(f)
        
        for round_name, round_divisions in pairings.items():
            for division_name, matches in round_divisions.items():
                division_folder = fixtures_path / division_name / round_name
                division_folder.mkdir(parents=True, exist_ok=True)
                
                for i, match in enumerate(matches, 1):
                    team1 = match['local']
                    team2 = match['visitante']
                    
                    match_file = division_folder / f"Match_{i}_{team1}_vs_{team2}.xlsx"
                    shutil.copy2(template_path, match_file)
                    
                    wb = openpyxl.load_workbook(match_file)
                    ws = wb.active
                    ws.cell(row=2, column=2, value=team1)
                    ws.cell(row=2, column=3, value=team2)
                    wb.save(match_file)
                    
                    print(f"Created: {match_file}")
                    total_matches += 1
        
        print(f"\nGenerated {total_matches} matches from JSON pairings.")
    else:
        # Generate fixtures for each division
        for division_name, teams in divisions.items():
            if len(teams) < 2:
                print(f"Skipping {division_name}: Need at least 2 teams.")
                continue
            
            division_folder = fixtures_path / division_name
            division_folder.mkdir(exist_ok=True)
            
            schedule = generate_division_schedule(teams.copy())
            
            for date_num, round_matches in enumerate(schedule, 1):
                date_folder = division_folder / f"J{date_num}"
                date_folder.mkdir(exist_ok=True)
                
                for i, (team1, team2) in enumerate(round_matches, 1):
                    match_file = date_folder / f"Match_{i}_{team1}_vs_{team2}.xlsx"
                    shutil.copy2(template_path, match_file)
                    
                    # Update team names in Excel file
                    wb = openpyxl.load_workbook(match_file)
                    ws = wb.active
                    ws.cell(row=2, column=2, value=team1)
                    ws.cell(row=2, column=3, value=team2)
                    wb.save(match_file)
                    
                    print(f"Created: {match_file}")
            
            division_matches = sum(len(round_matches) for round_matches in schedule)
            total_teams += len([t for t in teams if t != 'BYE'])
            total_matches += division_matches
            
            print(f"\n{division_name}: {len(teams)} teams, {division_matches} matches across {len(schedule)} dates.")
    
    # Generate cross-division matches if requested
    if cross_division and len(divisions) > 1:
        cross_matches = generate_cross_division_matches(divisions)
        if cross_matches:
            cross_folder = fixtures_path / "Cross-Division"
            cross_folder.mkdir(exist_ok=True)
            
            for date_num, round_matches in enumerate(cross_matches, 1):
                date_folder = cross_folder / f"J{date_num}"
                date_folder.mkdir(exist_ok=True)
                
                for i, (team1, team2) in enumerate(round_matches, 1):
                    match_file = date_folder / f"Match_{i}_{team1}_vs_{team2}.xlsx"
                    shutil.copy2(template_path, match_file)
                    
                    wb = openpyxl.load_workbook(match_file)
                    ws = wb.active
                    ws.cell(row=2, column=2, value=team1)
                    ws.cell(row=2, column=3, value=team2)
                    wb.save(match_file)
                    
                    print(f"Created: {match_file}")
            
            cross_match_count = sum(len(round_matches) for round_matches in cross_matches)
            total_matches += cross_match_count
            print(f"\nCross-Division: {cross_match_count} matches across {len(cross_matches)} dates.")
    
    print(f"\nTotal: {total_teams} teams, {total_matches} matches across {len(divisions)} divisions.")

def generate_cross_division_matches(divisions):
    """Generate cross-division matches between all teams from different divisions"""
    all_teams = []
    for teams in divisions.values():
        all_teams.extend(teams)
    
    return generate_division_schedule(all_teams)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_league.py <teams_json_path> <output_folder_path> [--cross-division] [--pairings-json <path>]")
        sys.exit(1)
    
    teams_json_path = sys.argv[1]
    output_folder = sys.argv[2]
    cross_division = "--cross-division" in sys.argv
    
    pairings_json = None
    if "--pairings-json" in sys.argv:
        idx = sys.argv.index("--pairings-json")
        if idx + 1 < len(sys.argv):
            pairings_json = sys.argv[idx + 1]
    
    generate_league(teams_json_path, output_folder, cross_division, pairings_json)