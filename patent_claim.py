import requests
import re
import json
import os
from dotenv import load_dotenv
# from google_scraper import get_default_browser, create_webdriver, get_patent_details

# Load information from Env file
load_dotenv()
api_key = os.getenv("API_KEY")
# create a claimnode class 
class ClaimNode:

    def __init__(self, number, text):
        self.number = number
        self.text = text
        self.children = []

    def __repr__(self):
        return f"ClaimNode: {self.number}, text: {self.text}, children: {self.children}"

    def add_child(self, child):
        self.children.append(child)

    ## print tree from the node downwards
    def print_tree(self, level=0):
        indent = "  " * level
        output = f"{indent}- Claim {self.number}: {self.text}\n"
        for child in self.children:
            output += child.print_tree(level + 1)
        return output
    
# returns a list containing all claim reference numbers
def find_claim_references(claim_text:str) -> list:
    ref_list = list()
    # find all claim # references within the text using regex
    claim_match = re.finditer(r"\bclaim (\d+)\b", claim_text, re.IGNORECASE)
    # return all matching numbers
    for m in claim_match:
        number = m.group(1)
        ref_list.append(int(number))
    return ref_list

# build the claim tree given a string of claims
def build_claim_tree(claims: list) -> list:
    nodes = {}
    roots = []
    
    # first, create our claim nodes.
    for claim in claims:
        # break the claim into number and text
        match = re.match(r'^(\d+)\.\s+(.*)', claim.strip())
        if not match:
            continue
        number = int(match.group(1))
        text = match.group(2)
        nodes[number] = ClaimNode(number,text)

    #then, create the tree
    for number, node in nodes.items():
        # find the references of the given claim
        refs = find_claim_references(node.text)
        # if none are found, claim is a root
        if refs == []:
            roots.append(node)
        # if not, add the claim as a child to the referenced node(s).
        else:
            for ref in refs:
                nodes[ref].add_child(node)

    return roots

# save json to file
def save_json(file_name:str, data):
    with open(file_name,'w') as f:
        json.dump(data, f)

# load data from json file
def load_json(file_name:str):
    with open(file_name) as f:
        data = json.load(f)
    return data

# patent = "US8377085"
# tree = get_patent_claims(patent)
# for node in tree:
#     print(node.print_tree())
# print(tree)