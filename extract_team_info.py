#!/usr/bin/env python3
import json
import base64
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io

def extract_team_info():
    """Extract team information from PDFs in Reference folder."""
    reference_folder = Path("Reference")
    teams_data = {}
    
    for group_folder in ["Grupo 1", "Grupo 2"]:
        group_path = reference_folder / group_folder
        if not group_path.exists():
            continue
            
        for pdf_file in group_path.glob("*.pdf"):
            try:
                team_name = pdf_file.stem
                doc = fitz.open(pdf_file)
                page = doc[0]  # First page
                
                # Extract images
                image_list = page.get_images()
                logo_base64 = None
                
                if image_list:
                    # Get first image as logo
                    xref = image_list[0][0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        logo_base64 = base64.b64encode(img_data).decode()
                    pix = None
                
                # Extract text and find team color (simplified approach)
                text_dict = page.get_text("dict")
                team_color = "#000000"  # Default black
                
                # Look for colored text blocks
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                if team_name.lower() in span["text"].lower():
                                    # Extract color from span
                                    color = span.get("color", 0)
                                    if color != 0:
                                        team_color = f"#{color:06x}"
                
                teams_data[team_name] = {
                    "group": group_folder,
                    "team_name": team_name,
                    "logo_base64": logo_base64,
                    "team_color": team_color
                }
                
                doc.close()
                print(f"Processed: {team_name}")
                
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {e}")
    
    # Save to JSON
    output_file = Path("tests/output/teams_info.json")
    with open(output_file, 'w') as f:
        json.dump(teams_data, f, indent=2)
    
    print(f"Team information saved to: {output_file}")

if __name__ == "__main__":
    extract_team_info()