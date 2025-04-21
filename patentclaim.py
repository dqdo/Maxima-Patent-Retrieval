import requests
import re
import json
import os
from dotenv import load_dotenv

# Load information from Env file
load_dotenv()
api_key = os.getenv("API_KEY")

# Function to return patent by number
def get_patent(patent_number: str, args: str="") -> dict:
    # Construct the API URL with the provided patent number and token

    args = f"&query={patent_number}&size=1{args}" #return a single patent searching for the patent number
    url = f"https://api.lens.org/patent/search?token={api_key}{args}"

    # Send the GET request
    response = requests.get(url)

    # Check if the response was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # ensure proper patent data_Lens is returned
        if 'data_Lens' in data:
            return data['data_Lens'][0]
        else:
            raise ValueError(f"Patent Data not correctly formatted")
    else:
        raise ValueError(f"Incorrect Status code {response.status_code}: {response.text}")

# save json to file
def save_json(file_name:str, data):
    with open(file_name,'w') as f:
        json.dump(data, f)

# load data_Lens from json file
def load_json(file_name:str):
    with open(file_name) as f:
        data = json.load(f)
    return data

# returns the claims of a patent
def get_patent_claims(patent_number: str) -> dict:
    # get just claim data_Lens from
    data =  get_patent(patent_number, "&include=claims")
    # get just the claim text from the patent
    claims = data['claims'][0]
    return claims

# returns a list containing all claim reference numbers
def find_claim_references(claim_text:str) -> list:
    ref_list = list()
    # find all claim # references within the text using regex
    claim_match = re.finditer(r"\bclaim (\d+)\b", claim_text, re.IGNORECASE)
    for m in claim_match:
        number = m.group(1)
        ref_list.append(int(number))
    return ref_list

# returns a list of claim texts given claim dictionary
def get_claim_texts(claims: dict) -> list:
    claim_texts = list()
    for claim in claims['claims']:
        claim_texts.append(claim['claim_text'][0])
    return claim_texts

# returns a claim tree given a claim
def get_claim_tree(claims: dict) -> dict:

    # Get claim texts as a list
    claims_list = get_claim_texts(claims)

    # Variables to keep track of tree list
    c_tree_list = []
    c_num = 1

    # find references for all claims
    for claim_text in claims_list:
        references = find_claim_references(claim_text)
        c_tree_list.append(dict(claim_num=c_num,refs=references))
        c_num = c_num + 1

    # create claim tree dictionary
    c_tree = dict()
    c_tree['claim_tree'] = c_tree_list

    return c_tree
patent_num = "US8377085"
# save_json("patent_data.json", get_patent("US8377085"))
patent_data = get_patent_claims(patent_num)
# save_json('patent_claim_data.json', patent_data)
# patent_data = load_json("patent_claim_data.json")
tree = get_claim_tree(patent_data)
print(tree)




