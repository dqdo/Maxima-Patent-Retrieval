import os
import json
from collections import defaultdict

# Directories
input_dir = 'data'
output_dir = 'patent_family_data'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Dictionary to track family members and their related main patents
family_member_relations = defaultdict(set)

# Loop through all JSON files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(input_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Failed to decode {filename}")
                continue

        # Skip files with empty data list
        if not data.get("data"):
            print(f"Skipping {filename} due to empty data.")
            continue

        # Get the main patent number from the filename (strip .json)
        main_patent_number = os.path.splitext(filename)[0]

        # Navigate to the extended family members
        extended_family_members = data["data"][0].get('families', {}).get('extended_family', {}).get('members', [])

        # Handle single object vs list
        if isinstance(extended_family_members, dict):
            extended_family_members = [extended_family_members]

        # Extract patent numbers as jurisdiction + doc_number
        extracted_family = []
        for member in extended_family_members:
            doc = member.get('document_id', {})
            jurisdiction = doc.get('jurisdiction')
            doc_number = doc.get('doc_number')
            if jurisdiction and doc_number:
                patent_id = f"{jurisdiction}{doc_number}"
                extracted_family.append(patent_id)
                family_member_relations[patent_id].add(main_patent_number)

        # Write to output file
        output_filename = f"{main_patent_number}_extended_family.json"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, 'w', encoding='utf-8') as out_file:
            json.dump(extracted_family, out_file, indent=2)

        print(f"Saved extended family for {main_patent_number} with {len(extracted_family)} member(s).")

# Create the summary JSON with unique patent numbers and their related main patents
family_summary = {member: sorted(list(related)) for member, related in family_member_relations.items()}

# Write the summary to a single JSON file
summary_path = os.path.join(output_dir, 'patent_family_set.json')
with open(summary_path, 'w', encoding='utf-8') as summary_file:
    json.dump(family_summary, summary_file, indent=2)

print(f"Saved complete patent family set with {len(family_summary)} unique family member(s).")
