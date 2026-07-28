from app1 import Flask

app = Flask(__name__)

# List of dictionaries (Voting Records)

voters = [
    {"id": 1, "name": "Krishna", "age": 20, "city": "Nanded", "voted": "Yes"},
    {"id": 2, "name": "Dipak", "age": 19, "city": "Kinwat", "voted": "No"},
    {"id": 3, "name": "Kartik", "age": 20, "city": "Mukhed", "voted": "Yes"},
    {"id": 4, "name": "Mahesh", "age": 19, "city": "Latur", "voted": "Yes"},
    {"id": 5, "name": "Suresh", "age": 18, "city": "Shegoan", "voted": "No"}
]

# Route 1 - Homepage

@app.route("/")
def home():
    return '<h1>ONLINE VOTING SYSTEM</h1>''<p> Welcome to the online voting system. Here you can find information about candidates and their voting status.</p>'

# Route 2 - Records Page

@app.route("/records")
def records():
    output = "<h2>Voter Records</h2>"
    
    for voter in voters:
        output += f"""
        <p>
        ID: {voter['id']} <br>
        Name: {voter['name']} <br>
        City: {voter['city']} <br>
        Voted: {voter['voted']}
        </p>
        <hr>
        """
    
    return output

# Route 3 - Voting Status

@app.route("/status")
def status():
    total_voters = len(voters)
    voted_count = 0

    for voter in voters:
        if voter["voted"] == "Yes":
            voted_count += 1

    return f"""
    <h2>Voting Status</h2>
    Total Voters: {total_voters}<br>
    Votes Cast: {voted_count}
    """

# Run Application

if __name__ == "__main__":
    app.run(debug=True)