import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from werkzeug.utils import secure_filename
import os

from database import get_db, init_db
conn = get_db()
conn=sqlite3.connect("voting.db")
init_db()  # Initialize the database
app = Flask(__name__)

app.secret_key = "student-voting-system-secret-key"

UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
from werkzeug.utils import secure_filename
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True) #create the upload folder if it doesn't exist
def allowed_file(filename):
    #only allow certain file extensions
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


DATABASE = "MyVote.db"

# -------------------------------------------------
# HOME
# -------------------------------------------------

@app.route("/")
def index():

    conn = get_db()

    candidates = conn.execute(
        "SELECT * FROM candidates ORDER BY id DESC LIMIT 3"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        candidates=candidates
    )

@app.route("/about")
def about():
    return render_template("about.html")


# -------------------------------------------------
# REGISTER
# -------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO users
                (username, email, password)
                VALUES (?, ?, ?)
                """,
                (username, email, password)
            )

            conn.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(url_for("login"))

        except Exception:

            flash(
                "Username or email already exists.",
                "danger"
            )

        finally:
            conn.close()

    return render_template("register.html")


# -------------------------------------------------
# USER LOGIN
# -------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            """
            SELECT * FROM users
            WHERE username = ? AND password = ?
            """,
            (username, password)
        ).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash("Login successful!", "success")

            return redirect(url_for("candidates"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "info")

    return redirect(url_for("index"))


# -------------------------------------------------
# CANDIDATES + SEARCH + PAGINATION
# -------------------------------------------------

@app.route("/candidates")
def candidates():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    search = request.args.get("search", "")

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    per_page = 6

    offset = (page - 1) * per_page

    conn = get_db()

    # Total candidates
    if search:

        total = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM candidates
            WHERE name LIKE ? OR party LIKE ?
            """,
            (
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchone()["count"]

        candidates = conn.execute(
            """
            SELECT * FROM candidates
            WHERE name LIKE ? OR party LIKE ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (
                f"%{search}%",
                f"%{search}%",
                per_page,
                offset
            )
        ).fetchall()

    else:

        total = conn.execute(
            "SELECT COUNT(*) AS count FROM candidates"
        ).fetchone()["count"]

        candidates = conn.execute(
            """
            SELECT * FROM candidates
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (per_page, offset)
        ).fetchall()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "candidates.html",
        candidates=candidates,
        search=search,
        page=page,
        total_pages=total_pages,
        user=user
    )


# -------------------------------------------------
# VOTE CASTING
# -------------------------------------------------

@app.route("/vote/<int:candidate_id>", methods=["POST"])
def vote(candidate_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    candidate = conn.execute(
        "SELECT * FROM candidates WHERE id = ?",
        (candidate_id,)
    ).fetchone()

    if candidate is None:

        conn.close()

        flash("Candidate not found.", "danger")

        return redirect(url_for("candidates"))

    if user["has_voted"] == 1:

        conn.close()

        flash("You have already voted.", "warning")

        return redirect(url_for("candidates"))

    # INSERT vote
    conn.execute(
        """
        INSERT INTO votes
        (user_id, candidate_id)
        VALUES (?, ?)
        """,
        (session["user_id"], candidate_id)
    )

    # UPDATE user
    conn.execute(
        """
        UPDATE users
        SET has_voted = 1
        WHERE id = ?
        """,
        (session["user_id"],)
    )

    conn.commit()
    conn.close()

    flash(
        f"Your vote for {candidate['name']} has been recorded!",
        "success"
    )

    return redirect(url_for("results"))


# -------------------------------------------------
# RESULTS
# -------------------------------------------------

@app.route("/results")
def results():

    conn = get_db()

    results = conn.execute(
        """
        SELECT
            candidates.id,
            candidates.name,
            candidates.party,
            candidates.symbol,
            candidates.photo,
            COUNT(votes.id) AS vote_count
        FROM candidates
        LEFT JOIN votes
            ON candidates.id = votes.candidate_id
        GROUP BY candidates.id
        ORDER BY vote_count DESC
        """
    ).fetchall()

    conn.close()

    total_votes = sum(
        candidate["vote_count"]
        for candidate in results
    )

    return render_template(
        "results.html",
        results=results,
        total_votes=total_votes
    )


# -------------------------------------------------
# PROFILE
# -------------------------------------------------

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )


# =================================================
# ADMIN
# =================================================

# -------------------------------------------------
# ADMIN LOGIN
# -------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        admin = conn.execute(
            """
            SELECT * FROM admins
            WHERE username = ? AND password = ?
            """,
            (username, password)
        ).fetchone()

        conn.close()

        if admin:

            session["admin_id"] = admin["id"]

            flash(
                "Admin login successful.",
                "success"
            )

            return redirect(url_for("admin_dashboard"))

        flash(
            "Invalid admin login.",
            "danger"
        )

    return render_template("admin/login.html")


# -------------------------------------------------
# ADMIN LOGOUT
# -------------------------------------------------

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_id", None)

    return redirect(url_for("index"))


# -------------------------------------------------
# ADMIN DASHBOARD
# -------------------------------------------------

@app.route("/admin")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()

    users = conn.execute(
        "SELECT COUNT(*) AS count FROM users"
    ).fetchone()["count"]

    candidates_count = conn.execute(
        "SELECT COUNT(*) AS count FROM candidates"
    ).fetchone()["count"]

    votes = conn.execute(
        "SELECT COUNT(*) AS count FROM votes"
    ).fetchone()["count"]

    conn.close()

    return render_template(
        "admin/dashboard.html",
        users=users,
        candidates=candidates_count,
        votes=votes
    )


# -------------------------------------------------
# ADMIN CANDIDATES - READ
# -------------------------------------------------

@app.route("/admin/candidates")
def admin_candidates():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()

    candidates = conn.execute(
        "SELECT * FROM candidates ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "admin/candidates.html",
        candidates=candidates
    )


# -------------------------------------------------
# ADD CANDIDATE - CREATE
# -------------------------------------------------

@app.route("/admin/candidates/add", methods=["GET", "POST"])
def add_candidate():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        name = request.form["name"]
        party = request.form["party"]
        symbol = request.form["symbol"]
        description = request.form["description"]

        photo_url = request.form["photo_url"]

        photo_filename = ""

        # Upload photo
        photo = request.files.get("photo")

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            photo_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            photo.save(photo_path)

            photo_filename = filename

        elif photo_url:

            # Store URL directly
            photo_filename = photo_url

        conn = get_db()

        conn.execute(
            """
            INSERT INTO candidates
            (name, party, symbol, photo, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                party,
                symbol,
                photo_filename,
                description
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Candidate added successfully.",
            "success"
        )

        return redirect(
            url_for("admin_candidates")
        )

    return render_template(
        "admin/candidate_form.html",
        candidate=None
    )


# -------------------------------------------------
# EDIT CANDIDATE - UPDATE
# -------------------------------------------------

@app.route(
    "/admin/candidates/edit/<int:id>",
    methods=["GET", "POST"]
)
def edit_candidate(id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()

    candidate = conn.execute(
        "SELECT * FROM candidates WHERE id = ?",
        (id,)
    ).fetchone()

    if candidate is None:

        conn.close()

        flash(
            "Candidate not found.",
            "danger"
        )

        return redirect(
            url_for("admin_candidates")
        )

    if request.method == "POST":

        name = request.form["name"]
        party = request.form["party"]
        symbol = request.form["symbol"]
        description = request.form["description"]

        photo_url = request.form["photo_url"]

        photo_filename = candidate["photo"]

        photo = request.files.get("photo")

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            photo_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            photo.save(photo_path)

            photo_filename = filename

        elif photo_url:

            photo_filename = photo_url

        conn.execute(
            """
            UPDATE candidates
            SET name = ?,
                party = ?,
                symbol = ?,
                photo = ?,
                description = ?
            WHERE id = ?
            """,
            (
                name,
                party,
                symbol,
                photo_filename,
                description,
                id
            )
        )

        conn.commit()

        flash(
            "Candidate updated successfully.",
            "success"
        )

        conn.close()

        return redirect(
            url_for("admin_candidates")
        )

    conn.close()

    return render_template(
        "admin/candidate_form.html",
        candidate=candidate
    )


# -------------------------------------------------
# DELETE CANDIDATE - DELETE
# -------------------------------------------------

@app.route(
    "/admin/candidates/delete/<int:id>",
    methods=["POST"]
)
def delete_candidate(id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()

    # Delete votes first
    conn.execute(
        "DELETE FROM votes WHERE candidate_id = ?",
        (id,)
    )

    # Delete candidate
    conn.execute(
        "DELETE FROM candidates WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Candidate deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_candidates")
    )


# -------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )