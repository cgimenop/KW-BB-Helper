#!/usr/bin/env python3
import sys
import json
import base64
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io

def extract_team_info(folder_path):
    """Extract team information from PDFs in Rooster subfolder."""
    rooster_folder = Path(folder_path) / "Roosters"
    teams_data = {}

    if not rooster_folder.exists():
        print(f"Error: Rooster folder not found in '{folder_path}'")
        return

    # Check if there are division folders or direct PDFs
    pdf_files = list(rooster_folder.glob("*.pdf"))
    if not pdf_files:
        # Look in division subfolders
        for division_folder in rooster_folder.iterdir():
            if division_folder.is_dir():
                pdf_files.extend(division_folder.glob("*.pdf"))

    for pdf_file in pdf_files:
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

                # Find cell with team name and extract its colors
                font_color = "#000000"  # Default black
                background_color = "#ffffff"  # Default white
                team_cell_bbox = None

                text_dict = page.get_text("dict")

                # Find the cell containing the team name
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                if team_name.lower() in span["text"].lower():
                                    font_color_int = span.get("color", 0)
                                    if font_color_int != 0:
                                        font_color = f"#{font_color_int:06x}"
                                    team_cell_bbox = span["bbox"]
                                    break

                # Find background color from drawings overlapping the team name cell
                if team_cell_bbox:
                    drawings = page.get_drawings()
                    for drawing in drawings:
                        if drawing.get("fill") and "rect" in drawing:
                            rect = drawing["rect"]
                            # Check if rectangles overlap
                            if (rect[0] <= team_cell_bbox[2] and rect[2] >= team_cell_bbox[0] and
                                rect[1] <= team_cell_bbox[3] and rect[3] >= team_cell_bbox[1]):
                                fill_color = drawing["fill"]
                                if fill_color and fill_color != (1.0, 1.0, 1.0):  # Not white
                                    r, g, b = [int(c * 255) for c in fill_color[:3]]
                                    background_color = f"#{r:02x}{g:02x}{b:02x}"
                                    break

                teams_data[team_name] = {
                    "team_name": team_name,
                    "logo_base64": logo_base64,
                    "font_color": font_color,
                    "background_color": background_color
                }

                # Save logo as PNG file
                if logo_base64:
                    logos_folder = rooster_folder / "logos"
                    logos_folder.mkdir(exist_ok=True)
                    try:
                        logo_data = base64.b64decode(logo_base64)
                        logo_file = logos_folder / f"{team_name.replace(' ', '_').replace('/', '_')}.png"
                        with open(logo_file, 'wb') as f:
                            f.write(logo_data)
                        print(f"Saved logo: {logo_file}")
                    except Exception as e:
                        print(f"Error saving logo for {team_name}: {e}")

                doc.close()
                print(f"Processed: {team_name} - Font: {font_color}, Background: {background_color}")

            except Exception as e:
                print(f"Error processing {pdf_file.name}: {e}")

    # Save to JSON in Roosters subfolder
    output_file = rooster_folder / "teams_info.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(teams_data, f, indent=2, ensure_ascii=False)

    print(f"Team information saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_team_info.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    extract_team_info(folder_path)