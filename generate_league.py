#!/usr/bin/env python3
import sys
import shutil
from pathlib import Path
from itertools import combinations
import openpyxl

def generate_league(roosters_folder):
    """Generate league pairings and create match templates."""
    roosters_path = Path(roosters_folder)
    
    if not roosters_path.exists():
        print(f"Error: Folder '{roosters_folder}' does not exist.")
        return
    
    # Get team names from filenames (without extension)
    teams = [f.stem for f in roosters_path.glob("*") if f.is_file()]
    
    if len(teams) < 2:
        print("Need at least 2 teams to generate a league.")
        return
    
    # Generate round-robin schedule (each team plays once per date)
    n = len(teams)
    if n % 2 == 1:
        teams.append("BYE")  # Add bye for odd number of teams
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
        # Rotate teams (keep first team fixed)
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    
    total_dates = len(schedule)
    
    template_path = Path("samples/clean/Hoja Limpia Acta.xlsx")
    
    if not template_path.exists():
        print(f"Template file not found: {template_path}")
        return
    
    # Create date folders and match files in same parent directory
    parent_dir = roosters_path.parent
    
    # Wipe previous date folders
    for existing_folder in parent_dir.glob("J*"):
        if existing_folder.is_dir():
            shutil.rmtree(existing_folder)
            print(f"Removed: {existing_folder}")
    
    for date_num, round_matches in enumerate(schedule, 1):
        date_folder = parent_dir / f"J{date_num}"
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
    
    total_matches = sum(len(round_matches) for round_matches in schedule)
    print(f"\nLeague generated with {len([t for t in teams if t != 'BYE'])} teams, {total_matches} matches across {total_dates} dates.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_league.py <roosters_folder_path>")
        sys.exit(1)
    
    roosters_folder = sys.argv[1]
    generate_league(roosters_folder)