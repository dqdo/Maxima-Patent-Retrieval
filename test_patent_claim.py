import pytest
from patent_claim import ClaimNode, find_claim_references, build_claim_tree, get_patent_claims

# test functions
def test_claim_references():
    claims = [
        "1. A system for controlling a robot.",
        "2. The system of claim 1, wherein the robot includes a gripper.",
        "3. The system of claim 1, wherein the robot is mobile.",
        "4. The system of claim 1 and claim 2, further including sensors.",
    ]

    claimRefs = [find_claim_references(claim) for claim in claims]

    assert len(claimRefs) == 4
    assert claimRefs == [[],[1],[1],[1,2]]
    
def find_node_by_number(root_nodes, number):
    """Recursively find a node by its number in the tree."""
    for node in root_nodes:
        if node.number == number:
            return node
        result = find_node_by_number(node.children, number)
        if result:
            return result
    return None
    

def test_build_claim_tree():
    claims = [
        "1. A device comprising a widget.",
        "2. The device of claim 1, wherein the widget is blue.",
        "3. The device of claim 1, further comprising a doohickey.",
        "4. The device of claim 1 and claim 2, wherein the doohickey is removable.",
        "5. A system for controlling a widget.",
        "6. The system of claim 5, wherein the controller is wireless.",
        "7. The system of claim 6, further comprising a backup battery.",
        "8. A composition of matter."
    ]

    tree = build_claim_tree(claims)

    # Test for root claims
    root_numbers = {node.number for node in tree}
    assert root_numbers == {1, 5, 8}

    # Check structure under claim 1
    claim1 = find_node_by_number(tree, 1)
    assert {c.number for c in claim1.children} == {2, 3, 4} 
    claim2 = find_node_by_number(tree, 2)
    assert {c.number for c in claim2.children} == {4}


    # Check claim 5 tree 
    claim5 = find_node_by_number(tree, 5)
    assert {c.number for c in claim5.children} == {6}
    claim6 = find_node_by_number(tree, 6)
    assert {c.number for c in claim6.children} == {7}

    # Check claim 8 is lone root
    claim8 = find_node_by_number(tree,8)
    assert claim8.children == []

def test_real_patent_claim():
    patent = "US8377085"
    tree = get_patent_claims(patent)

    # Test for root claims
    root_numbers = {node.number for node in tree}
    assert root_numbers == {1, 21}


# patent_num = "US8377085"
# # save_json("patent_data.json", get_patent("US8377085"))
# patent_data = get_patent_claims(patent_num)
# # save_json('patent_claim_data.json', patent_data)
# # patent_data = load_json("patent_claim_data.json")
# tree = get_claim_tree(patent_data)
# print(tree)



