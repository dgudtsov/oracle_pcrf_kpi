#!/usr/bin/env python3
"""
Script to convert XML files in the 'xml' directory to CSV format.
Each <Sample> section in XML becomes a row in the CSV output.
Each XML tuple (child element) becomes a column in the CSV.
"""

import os
import xml.etree.ElementTree as ET
import csv
from pathlib import Path


def xml_to_csv(xml_file_path, csv_file_path):
    """
    Convert an XML file to CSV format.
    
    Args:
        xml_file_path: Path to the input XML file
        csv_file_path: Path to the output CSV file
    """
    try:
        # Parse the XML file
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        # Find all <Sample> elements
        samples = root.findall('.//Sample')
        
        if not samples:
            print(f"Warning: No <Sample> elements found in {xml_file_path}")
            return
        
        # Collect field names preserving the order as they appear in XML
        # Use the first sample to establish the base order
        field_names = []
        seen_fields = set()
        
        # First, collect fields from the first sample in their original order
        if samples:
            for child in samples[0]:
                if child.tag not in seen_fields:
                    field_names.append(child.tag)
                    seen_fields.add(child.tag)
        
        # Then, add any additional fields from other samples (if any)
        for sample in samples[1:]:
            for child in sample:
                if child.tag not in seen_fields:
                    field_names.append(child.tag)
                    seen_fields.add(child.tag)
        
        # Write CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            
            # Write each sample as a row
            for sample in samples:
                row = {}
                for child in sample:
                    # Get text content, default to empty string if None
                    row[child.tag] = child.text if child.text is not None else ''
                writer.writerow(row)
        
        print(f"Successfully converted {xml_file_path} to {csv_file_path}")
        print(f"  - Found {len(samples)} sample(s)")
        print(f"  - Created {len(field_names)} column(s)")
        
    except ET.ParseError as e:
        print(f"Error parsing XML file {xml_file_path}: {e}")
    except Exception as e:
        print(f"Error processing {xml_file_path}: {e}")


def main():
    """Main function to process all XML files in the xml directory."""
    # Get the script directory
    script_dir = Path(__file__).parent.absolute()
    xml_dir = script_dir / 'xml'
    csv_dir = xml_dir / 'csv'
    
    # Create csv directory if it doesn't exist
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if xml directory exists
    if not xml_dir.exists():
        print(f"Error: XML directory '{xml_dir}' does not exist")
        return
    
    # Find all XML files in the xml directory
    xml_files = list(xml_dir.glob('*.xml'))
    
    if not xml_files:
        print(f"No XML files found in {xml_dir}")
        return
    
    print(f"Found {len(xml_files)} XML file(s) to process\n")
    
    # Process each XML file
    for xml_file in xml_files:
        # Create CSV filename with same name but .csv extension
        csv_filename = xml_file.stem + '.csv'
        csv_file_path = csv_dir / csv_filename
        
        print(f"Processing: {xml_file.name}")
        xml_to_csv(xml_file, csv_file_path)
        print()


if __name__ == '__main__':
    main()
