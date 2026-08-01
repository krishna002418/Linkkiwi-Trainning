import os
from flask import Flask, abort, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.secret_key = "online_voting_secret_key"

app.config['UPLOAD_FOLDER'] = 'static/uploads'
from werkzeug.utils import secure_filename
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the upload folder if it doesn't exist

def allowed_file(filename):
    #only allow certain file extensions
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


DATABASE = "Myproject.db"

# ---------------- DATABASE CONNECTION ----------------

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

# ---------------- CREATE DATABASE TABLES ----------------

def create_tables():
    connection = get_db()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            has_voted INTEGER DEFAULT 0
        )
    """)

    # Candidates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            party TEXT NOT NULL,
            symbol TEXT,
            votes INTEGER DEFAULT 0
        )
    """)

    # Insert default candidates
    cursor.execute("SELECT COUNT(*) FROM candidates")
    count = cursor.fetchone()[0]
    if count == 0:
        candidates = [
            ("Rahul Patil", "Development Party", "🌟"),
            ("Priya Sharma", "Progress Party", "🌿"),
            ("Amit Jadhav", "People's Party", "🦁")
        ]
        cursor.executemany("""
            INSERT INTO candidates(name, party, symbol)
            VALUES (?, ?, ?)
        """, candidates)
    connection.commit()
    connection.close()

# ---------------- LOGIN REQUIRED ----------------

def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return decorated_function

# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    connection = get_db()
    # SELECT method
    candidates = connection.execute("SELECT * FROM candidates ORDER BY id").fetchall()
    connection.close()
    return render_template("index.html",candidates=candidates)

@app.route("/about")
def about():
    return render_template("about.html")

# ---------------- USER REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        connection = get_db()
        try:
            # INSERT method
            connection.execute("""
                INSERT INTO users(
                    name,
                    username,
                    password
                )
                VALUES (?, ?, ?)
            """, (name, username, password))
            connection.commit()
            flash("Registration successful. Please login.","success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists.","danger")
        finally:
            connection.close()
    return render_template("register.html")

# ---------------- USER LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        connection = get_db()
        # SELECT method
        user = connection.execute("""
            SELECT * FROM users
            WHERE username = ?
            AND password = ?
        """, (username, password)).fetchone()
        connection.close()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!","success")
            return redirect(url_for("candidates"))
        else:
            flash("Invalid username or password.","danger")
    return render_template("login.html")

# ---------------- CANDIDATE PAGE ----------------

@app.route("/candidates")
@login_required
def candidates():
    search = request.args.get("search","").strip()
    connection = get_db()
    # SELECT with search
    candidates = connection.execute("""
        SELECT * FROM candidates
        WHERE name LIKE ?
        OR party LIKE ?
        ORDER BY id
    """, (
        f"%{search}%",
        f"%{search}%"
    )).fetchall()
    user = connection.execute("""
        SELECT has_voted
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    )).fetchone()
    connection.close()
    return render_template(
        "candidates.html",
        candidates=candidates,
        search=search,
        has_voted=user["has_voted"]
    )

# ---------------- CAST VOTE ----------------

@app.route("/vote/<int:candidate_id>")
@login_required
def vote(candidate_id):
    connection = get_db()
    user = connection.execute("""
        SELECT has_voted
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    )).fetchone()
    if user["has_voted"] == 1:
        connection.close()
        flash("You have already voted.","warning")
        return redirect(url_for("candidates"))
    # UPDATE candidate vote
    connection.execute("""
        UPDATE candidates
        SET votes = votes + 1
        WHERE id = ?
    """, (
        candidate_id,
    ))
    # UPDATE user voting status
    connection.execute("""
        UPDATE users
        SET has_voted = 1
        WHERE id = ?
    """, (
        session["user_id"],
    ))
    connection.commit()
    connection.close()
    flash("Your vote was cast successfully!","success")
    return redirect(url_for("results"))

#----------------- CANDIDATE DETAIL PAGE ----------------
@app.route("/candidates/<int:id>")
def candidate_detail(id):
    conn = get_db()
    candidate = conn.execute('SELECT * FROM candidates WHERE id = ?', (id,)).fetchone()
    conn.close()
    if candidate is None:
        flash("Candidate not found", "danger")
        return redirect(url_for("candidates"))
    
    return render_template("detail.html", candidate=candidate)

# ---------------- RESULTS ----------------

@app.route("/results")
def results():
    connection = get_db()
    # SELECT method
    candidates = connection.execute("""
        SELECT * FROM candidates
        ORDER BY votes DESC
    """).fetchall()
    connection.close()
    total_votes = sum(
        candidate["votes"]
        for candidate in candidates
    )
    # Dictionary for result data
    result_data = {}
    for candidate in candidates:
        if total_votes > 0:
            percentage = (
                candidate["votes"]
                / total_votes
            ) * 100
        else:
            percentage = 0
        result_data[candidate["name"]] = {
            "votes": candidate["votes"],
            "percentage": round(
                percentage,
                2
            )
        }
    winner = None
    if candidates and total_votes > 0:
        winner = candidates[0]["name"]
    return render_template(
        "results.html",
        candidates=candidates,
        total_votes=total_votes,
        result_data=result_data,
        winner=winner
    )

# ---------------- ADMIN PAGE ----------------

@app.route("/admin",methods=["GET", "POST"])
def admin():
    connection = get_db()
    if request.method == "POST":
        name = request.form["name"]
        party = request.form["party"]
        symbol = request.form["symbol"]
        # INSERT method
        connection.execute("""
            INSERT INTO candidates(
                name,
                party,
                symbol
            )
            VALUES (?, ?, ?)
        """, (
            name,
            party,
            symbol
        ))
        connection.commit()
        flash("Candidate added successfully.","success")
        return redirect(url_for("admin"))

    # SELECT method
    candidates = connection.execute("""
        SELECT * FROM candidates
        ORDER BY id
    """).fetchall()

    connection.close()
    return render_template("admin.html",candidates=candidates)

# ---------------- DELETE CANDIDATE ----------------

@app.route("/delete/<int:candidate_id>", methods=["POST"])
def delete_candidate(id):
    if session.get('role') != 'admin':
        flash("Admins only!  You do not have permission", "danger")
        return redirect(url_for('home'))
    
    conn = get_db()
    
    # First check if it exists
    candidate = conn.execute('SELECT * FROM candidates WHERE id = ?', (id,)).fetchone()
    if candidate is None:
        flash("Candidate not found", "danger")
        conn.close()
        return redirect(url_for('admin'))
    conn.execute('DELETE FROM candidates WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash("Candidate deleted successfully", "success")
    return redirect(url_for('admin'))

#---------------- EDIT CANDIDATE ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_candidate(id):
    if session.get('role') != 'admin':
        flash("Admins only!  You do not have permission", "danger")
        return redirect(url_for('home'))
    
    conn = get_db()
    
    if request.method == 'POST':
        name = request.form['candidate_name']
        party = request.form['party']
        symbol = request.form['symbol']

        if not name:
            flash('Name cannot be empty', 'danger')
            return redirect(url_for('edit_candidate', id=id))
        
        #Add: handle photo upload
        file = request.files.get('photo')
        filename = 'default.png'  # Default photo
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        conn.execute('''UPDATE candidates SET name=?, party=?, symbol=? 
                     WHERE id=?''', (name, party, symbol, id))
        conn.commit()
        conn.close()
        flash(f'{name} updated successfully!', 'success')
        return redirect(url_for('admin'))
    
# GET - fetch exisiting record
    candidate = conn.execute('SELECT * FROM candidates WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if candidate is None:
        abort(404) # trigger 404.html
        
    return render_template('edit_candidate.html', candidate=candidate)


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.","info")
    return redirect(url_for("home"))

def page_not_found(e):
    return render_template("404.html"), 404
app.errorhandler(404)(page_not_found)

# ---------------- RUN APPLICATION ----------------
if __name__ == "__main__":
    create_tables()
    app.run( debug=True)