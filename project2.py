# ONLINE VOTING SYSTEM
# ==================================

# Step 1: Main Entity Dictionary (Single Voter)
voter = {
    "voter_id": 101,
    "name": "Rahul",
    "age": 20,
    "city": "Latur",
    "status": "Voted"
}

# Step 2: List of 5 Voter Records
voters = [
    {"voter_id": 101, "name": "Rahul", "age": 20, "city": "Latur", "status": "Voted"},
    {"voter_id": 102, "name": "Priya", "age": 21, "city": "Pune", "status": "Not Voted"},
    {"voter_id": 103, "name": "Amit", "age": 22, "city": "Mumbai", "status": "Voted"},
    {"voter_id": 104, "name": "Sneha", "age": 23, "city": "Nagpur", "status": "Voted"},
    {"voter_id": 105, "name": "Rohit", "age": 24, "city": "Nashik", "status": "Not Voted"}
]

# Step 3: Bonus - Candidate Dictionary
candidate = {
    "candidate_id": 1,
    "candidate_name": "Amit Patil",
    "party": "ABC Party"
}

# Step 4: Function to Get Voting Status
def get_status(voter_id):
    for voter in voters:
        if voter["voter_id"] == voter_id:
            return voter["status"]
    return "Voter Not Found"

# Step 5: Function to Search Voter Record
def search_records(voter_id):
    for voter in voters:
        if voter["voter_id"] == voter_id:
            return voter
    return "Record Not Found"

# Step 6: Print All Records Using Loop
print("ONLINE VOTING SYSTEM")
print("---------------------")

for voter in voters:
    print("ID:", voter["voter_id"])
    print("Name:", voter["name"])
    print("Age:", voter["age"])
    print("City:", voter["city"])
    print("Status:", voter["status"])
    print("---------------------")

# Step 7: Function Testing
print("Status of Voter 103 =", get_status(103))

print("Search Result:")
print(search_records(104))