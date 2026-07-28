from flask import Flask, render_template, request, redirect

app = Flask(__name__)

votes = {
    "Candidate A": 0,
    "Candidate B": 0,
    "Candidate C": 0
}

voted_users = []

# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']

        if username in voted_users:
            return "You already voted!"

        return redirect(f'/vote/{username}')

    return render_template('login.html')


# Vote Page
@app.route('/vote/<username>', methods=['GET', 'POST'])
def vote(username):

    if request.method == 'POST':

        candidate = request.form['candidate']

        votes[candidate] += 1

        voted_users.append(username)

        return redirect('/result')

    return render_template('vote.html')


# Result Page
@app.route('/result')
def result():

    winner = max(votes, key=votes.get)

    return render_template(
        'result.html',
        votes=votes,
        winner=winner
    )


if __name__ == '__main__':
    app.run(debug=True)