import requests
from dotenv import load_dotenv
import os
import json

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment
api_key = os.getenv("API_KEY")


# Function to save full API response to a JSON file
def save_patent_json_response(patent_number, directory):
    url = f"https://api.lens.org/patent/search?token={api_key}&query={patent_number}"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            os.makedirs(directory, exist_ok=True)
            filename = os.path.join(directory, f"{patent_number}.json")

            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            print(f"[✓] Saved: {filename}")
        else:
            print(f"[!] Error for {patent_number} - {response.status_code}: {response.text}")

    except Exception as e:
        print(f"[!] Exception for {patent_number}: {e}")


# Main routine to process all patent numbers from input.txt
def process_patent_list(input_file, output_directory):
    if not os.path.exists(input_file):
        print(f"[!] Input file not found: {input_file}")
        return

    with open(input_file, "r") as file:
        patent_numbers = [line.strip() for line in file if line.strip()]

    for patent in patent_numbers:
        save_patent_json_response(patent, output_directory)


# Specify your paths
input_file = "input.txt"
output_directory = "data"

# Run the script
process_patent_list(input_file, output_directory)
