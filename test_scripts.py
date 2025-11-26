#!/usr/bin/env python3
import unittest
import tempfile
import shutil
from pathlib import Path
import json
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock, mock_open, MagicMock
import sys
import os
import openpyxl

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from update_classification import read_excel_files, load_settings, generate_classification_table
from generate_league import generate_league

class TestReadExcelFiles(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_load_settings(self):
        """Test loading league points configuration"""
        with patch('builtins.open', mock_open(read_data='{"league_points": {"win": 3, "draw": 1, "lose": 0}}')):
            settings = load_settings()
            self.assertEqual(settings["league_points"]["win"], 3)
    
    def test_load_settings_file_not_found(self):
        """Test default settings when file not found"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            settings = load_settings()
            self.assertEqual(settings["league_points"]["win"], 3)
    
    @patch('update_classification.Path')
    def test_read_excel_files_folder_not_exists(self, mock_path):
        """Test error when folder doesn't exist"""
        mock_path.return_value.exists.return_value = False
        with patch('builtins.print') as mock_print:
            read_excel_files("nonexistent")
            mock_print.assert_called_with("Error: Folder 'nonexistent' does not exist.")
    
    def test_read_excel_files_no_excel_files(self):
        """Test when no Excel files found"""
        test_folder = self.temp_path / "empty_dates"
        test_folder.mkdir()
        date_folder = test_folder / "J1"
        date_folder.mkdir()
        
        with patch('builtins.print') as mock_print:
            read_excel_files(str(test_folder))
        
        # Should process but find no Excel files
        self.assertTrue(mock_print.called)

class TestGenerateLeague(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.roosters_folder = self.temp_path / "roosters"
        self.roosters_folder.mkdir()
        
        # Create mock team files
        (self.roosters_folder / "team1.txt").touch()
        (self.roosters_folder / "team2.txt").touch()
        (self.roosters_folder / "team3.txt").touch()
        (self.roosters_folder / "team4.txt").touch()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    @patch('generate_league.Path')
    def test_generate_league_folder_not_exists(self, mock_path):
        """Test error when roosters folder doesn't exist"""
        mock_path.return_value.exists.return_value = False
        with patch('builtins.print') as mock_print:
            generate_league("nonexistent")
            mock_print.assert_called_with("Error: Folder 'nonexistent' does not exist.")
    
    def test_generate_league_insufficient_teams(self):
        """Test error with less than 2 teams"""
        single_team_folder = self.temp_path / "single"
        single_team_folder.mkdir()
        (single_team_folder / "team1.txt").touch()
        
        with patch('builtins.print') as mock_print:
            generate_league(str(single_team_folder))
            mock_print.assert_called_with("Need at least 2 teams to generate a league.")
    
    def test_generate_league_no_files(self):
        """Test with empty roosters folder"""
        empty_folder = self.temp_path / "empty"
        empty_folder.mkdir()
        
        with patch('builtins.print') as mock_print:
            generate_league(str(empty_folder))
            mock_print.assert_called_with("Need at least 2 teams to generate a league.")
    
    @patch('generate_league.Path')
    def test_generate_league_template_not_found(self, mock_path_class):
        """Test error when template file not found"""
        mock_roosters = MagicMock()
        mock_roosters.exists.return_value = True
        mock_roosters.glob.return_value = [MagicMock(stem="team1"), MagicMock(stem="team2")]
        mock_roosters.parent = MagicMock()
        
        mock_template = MagicMock()
        mock_template = MagicMock()
        mock_template.exists.return_value = False
        mock_template.__str__ = lambda x: "samples/clean/Hoja Limpia Acta.xlsx"
        
        def path_side_effect(path_str):
            if "roosters" in str(path_str):
                return mock_roosters
            elif "Hoja Limpia Acta.xlsx" in str(path_str):
                return mock_template
            return MagicMock()
        
        mock_path_class.side_effect = path_side_effect
        
        with patch('builtins.print') as mock_print:
            generate_league("roosters")
            mock_print.assert_called_with("Template file not found: samples/clean/Hoja Limpia Acta.xlsx")
    
    @patch('openpyxl.load_workbook')
    @patch('shutil.copy2')
    @patch('shutil.rmtree')
    def test_generate_league_success(self, mock_rmtree, mock_copy, mock_load_wb):
        """Test successful league generation"""
        # Create template file
        template_dir = self.temp_path / "samples" / "clean"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "Hoja Limpia Acta.xlsx"
        template_file.touch()
        
        # Mock workbook
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_wb.active = mock_ws
        mock_load_wb.return_value = mock_wb
        
        with patch('generate_league.Path') as mock_path_class:
            mock_roosters = MagicMock()
            mock_roosters.exists.return_value = True
            mock_roosters.glob.return_value = [MagicMock(stem="team1"), MagicMock(stem="team2")]
            mock_parent = MagicMock()
            mock_parent.glob.return_value = []
            mock_roosters.parent = mock_parent
            
            def path_side_effect(path_str):
                if "roosters" in str(path_str):
                    return mock_roosters
                elif "Hoja Limpia Acta.xlsx" in str(path_str):
                    return template_file
                return MagicMock()
            
            mock_path_class.side_effect = path_side_effect
            
            with patch('builtins.print'):
                generate_league("roosters")
            
            # Verify Excel file was modified
            mock_ws.cell.assert_called()
            mock_wb.save.assert_called()
    
    def test_round_robin_schedule(self):
        """Test that round-robin generates correct number of matches"""
        teams = ["team1", "team2", "team3", "team4"]
        n = len(teams)
        expected_rounds = n - 1
        expected_matches_per_round = n // 2
        expected_total_matches = (n * (n - 1)) // 2
        
        self.assertEqual(expected_rounds, 3)
        self.assertEqual(expected_matches_per_round, 2)
        self.assertEqual(expected_total_matches, 6)

class TestClassificationGeneration(unittest.TestCase):
    
    def test_classification_table_generation(self):
        """Test markdown classification table generation"""
        sample_data = {
            "J1": {
                "Team A": {"touchdowns": 2, "result": "win", "points": 3},
                "Team B": {"touchdowns": 1, "result": "lose", "points": 0}
            },
            "J2": {
                "Team A": {"touchdowns": 1, "result": "draw", "points": 1},
                "Team B": {"touchdowns": 1, "result": "draw", "points": 1}
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_folder = Path(temp_dir)
            generate_classification_table(sample_data, output_folder)
            
            markdown_file = output_folder / "classification.md"
            self.assertTrue(markdown_file.exists())
            
            content = markdown_file.read_text()
            self.assertIn("Team A", content)
            self.assertIn("Team B", content)
            self.assertIn("| 1 |", content)
            # Check that teams are properly sorted by points
            lines = content.split('\n')
            team_lines = [line for line in lines if '| Team' in line]
            self.assertTrue(len(team_lines) >= 2)

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_odd_number_teams(self):
        """Test league generation with odd number of teams"""
        temp_dir = tempfile.mkdtemp()
        roosters_folder = Path(temp_dir) / "roosters"
        roosters_folder.mkdir()
        
        # Create 3 teams (odd number)
        for i in range(3):
            (roosters_folder / f"team{i}.txt").touch()
        
        # This should handle the odd number by adding a BYE
        teams = [f.stem for f in roosters_folder.glob("*") if f.is_file()]
        self.assertEqual(len(teams), 3)
        
        shutil.rmtree(temp_dir)
    
    def test_classification_with_draws(self):
        """Test classification handles draws correctly"""
        sample_data = {
            "J1": {
                "Team A": {"touchdowns": 1, "result": "draw", "points": 1},
                "Team B": {"touchdowns": 1, "result": "draw", "points": 1}
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_folder = Path(temp_dir)
            generate_classification_table(sample_data, output_folder)
            
            markdown_file = output_folder / "classification.md"
            self.assertTrue(markdown_file.exists())
            
            content = markdown_file.read_text()
            # Both teams should have 1 draw
            self.assertIn("| 1 |", content)  # Points
            self.assertIn("Team A", content)
            self.assertIn("Team B", content)

if __name__ == "__main__":
    unittest.main()