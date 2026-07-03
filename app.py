from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from config import Config
from database.models import db, User, LearningHistory

from ai.prompt_engine import generate_explanation
from ai.quiz_engine import generate_quiz

from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# =====================================================
# Login Required Decorator
# =====================================================

def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))

        return route_function(*args, **kwargs)

    return wrapper


# =====================================================
# Current User Helper
# =====================================================

def get_current_user():

    if "user_id" not in session:
        return None

    return User.query.get(session["user_id"])


# =====================================================
# Home
# =====================================================

@app.route("/")
def home():

    return render_template("index.html")


# =====================================================
# Register
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:

            flash("Email already registered.", "danger")

            return redirect(url_for("register"))

        user = User(
            name=name,
            email=email
        )

        user.set_password(password)

        db.session.add(user)

        db.session.commit()

        flash("Registration Successful!", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# =====================================================
# Login
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            session["user_id"] = user.id

            if user.learning_style is None:

                return redirect(url_for("preferences"))

            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password", "danger")

        return redirect(url_for("login"))

    return render_template("login.html")


# =====================================================
# Logout
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("home"))
# =====================================================
# Preferences
# =====================================================

@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():

    user = get_current_user()

    if request.method == "POST":

        user.learning_style = request.form["learning_style"]
        user.difficulty = request.form["difficulty"]
        user.language = request.form["language"]

        db.session.commit()

        flash("Learning preferences saved successfully.", "success")

        return redirect(url_for("dashboard"))

    return render_template("preferences.html", user=user)


# =====================================================
# Dashboard
# =====================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user = get_current_user()

    history = (
        LearningHistory.query
        .filter_by(user_id=user.id)
        .order_by(LearningHistory.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        user=user,
        history=history
    )


# =====================================================
# Learn
# =====================================================

@app.route("/learn", methods=["GET", "POST"])
@login_required
def learn():

    user = get_current_user()

    if request.method == "POST":

        topic = request.form["topic"].strip()

        if topic == "":
            flash("Please enter a topic.", "warning")
            return redirect(url_for("learn"))

        explanation = generate_explanation(
            topic=topic,
            style=user.learning_style,
            difficulty=user.difficulty,
            language=user.language
        )

       # quiz = generate_quiz(
       #    topic=topic,
       #     explanation=explanation
       # )
       quiz=[]

        learning = LearningHistory(
            topic=topic,
            explanation=explanation,
            quiz=quiz,
            user_id=user.id
        )

        db.session.add(learning)
        db.session.commit()

        return render_template(
            "result.html",
            topic=topic,
            explanation=explanation,
            quiz=quiz
        )

    return render_template("learn.html", user=user)


# =====================================================
# History
# =====================================================

@app.route("/history")
@login_required
def history():

    user = get_current_user()

    history = (
        LearningHistory.query
        .filter_by(user_id=user.id)
        .order_by(LearningHistory.created_at.desc())
        .all()
    )

    return render_template(
        "history.html",
        user=user,
        history=history
    )


# =====================================================
# Profile
# =====================================================

@app.route("/profile")
@login_required
def profile():

    user = get_current_user()

    total_topics = (
        LearningHistory.query
        .filter_by(user_id=user.id)
        .count()
    )

    return render_template(
        "profile.html",
        user=user,
        total_topics=total_topics
    )
# =====================================================
# Application Entry Point
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
