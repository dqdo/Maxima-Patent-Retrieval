import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

def get_patent_family_details(patent_number):
    # Construct the API URL with the provided patent number and token
    url = f"https://api.lens.org/patent/search?token={api_key}&query={patent_number}"

    # Send the GET request
    response = requests.get(url)
    # Parse the JSON response
    data = response.json()

    families = data['data'][0].get('families', None)
    extended_family = families.get('extended_family', None)
    extended_family_members = extended_family.get('members', None)

    if extended_family_members:
        filename = f"{patent_number}_extended_family.txt"
        with open(filename, "w") as file:
            for member in extended_family_members:
                document_id = member.get('document_id', {})
                jurisdiction = document_id.get('jurisdiction', None)
                doc_number = document_id.get('doc_number', None)
                patent_num = str(jurisdiction) + str(doc_number)
                file.write(f"{patent_num}\n")
        print(f"Extended family members saved to {filename}")
    else:
        print("No extended family members found.")

# Function to get patent details by number
def get_patent_details(patent_number):
    # Construct the API URL with the provided patent number and token
    url = f"https://api.lens.org/patent/search?token={"aKSZdWlGl7IJCqkh7SNvnnfpn1eJ17OmglUZCOoBD1bONIp7yZx3"}&query={patent_number}"

    # Send the GET request
    response = requests.get(url)

    # Check if the response was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Access the 'legal_status' from the first item in the 'data' list
        if 'data' in data and len(data['data']) > 0:
            legal_status = data['data'][0].get('legal_status', None)

            if legal_status:
                # Access the 'calculation_log' list
                calculation_log = legal_status.get('calculation_log', [])

                # Print the 'patent_status'
                patent_status = legal_status.get('patent_status', 'Patent status not found')
                print("Patent Status:", patent_status)

                # Iterate through the 'calculation_log' to find the "Anticipated Termination Date"
                for log in calculation_log:
                    if "Anticipated Termination Date" in log:
                        # Extract the date (everything after the colon)
                        anticipated_termination_date = log.split(":")[1].strip()
                        print("Anticipated Termination Date:", anticipated_termination_date)
                        break
                else:
                    print("Anticipated Termination Date not found in the calculation log.")
            else:
                print("Legal status not found in the response.")
        else:
            print("No patent data found in the response.")
    else:
        print(f"Error {response.status_code}: {response.text}")

patent = "US8377085"
get_patent_details(patent)
get_patent_family_details(patent)
