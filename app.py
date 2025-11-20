import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.utils import secure_filename
# Config class integrated here for completeness
class Config:
    SECRET_KEY = '9f2e3a6d7c4f5b8a912dce4f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///your_db_path.db'
    UPLOAD_FOLDER = 'static/uploads'
    RESULT_FOLDER = 'static/results'

    # other config options...
from database.init_db import init_db, db, User, Upload
from utils.auth_utils import create_user, verify_user
from utils.model_utils import predict_brain_tumor, predict_pneumonia, load_models
from utils.chat_utils import ask_openai

# --- Flask app ---
app = Flask(__name__)
app.config.from_object(Config)

# Ensure folders
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["RESULT_FOLDER"], exist_ok=True)

db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
db_dir = os.path.dirname(db_path)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

# DB init
init_db(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class UserLogin(UserMixin):
    def __init__(self, user):
        self.id = user.id
        self.email = user.email
        self.name = user.name

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return UserLogin(user) if user else None

# Load models once
brain_model, pneumonia_model = load_models() # returns (brain_model, pneumonia_model)

#  Routes 

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return render_template("health.html")

@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")

@app.route("/brain-tumor-info")
def brain_tumor_info():
    return render_template("brain_tumor_info.html")

@app.route("/find-doctor")
def find_doctor():
    return render_template("find_doctor.html")

@app.route("/patient-resources")
def patient_resources():
    return render_template("patient_resources.html")

@app.route("/appointments")
@login_required
def appointments():
    return render_template("appointments.html")

@app.route("/teleconsultation")
@login_required
def teleconsultation():
    return render_template("teleconsultation.html")

@app.route("/research")
def research():
    return render_template("research.html")

@app.route("/faqs")
def faqs():
    return render_template("faqs.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        user = User.query.get(current_user.id)
        user.age = request.form.get("age") or None
        user.phone = request.form.get("phone")
        user.gender = request.form.get("gender")
        user.address = request.form.get("address")
        db.session.commit()
        flash("Profile updated successfully.", "success")
        # Re-fetch updated user info before render
        user = User.query.get(current_user.id)
        return render_template("profile.html", user=user, form_visible=True)
    # For GET requests
    user = User.query.get(current_user.id)
    return render_template("profile.html", user=user, form_visible=False)

@app.route("/upload/brain", methods=["GET", "POST"])
def upload_brain():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("No file uploaded")
            return redirect(request.url)
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        res = predict_brain_tumor(save_path, brain_model)
        user_id = current_user.id if current_user.is_authenticated else None
        rec = Upload(filename=filename, user_id=user_id, result_brain=res["label"], result_pneumonia=None)
        db.session.add(rec)
        db.session.commit()

        return render_template("result.html", image_url=url_for("static", filename="uploads/" + filename), result=res, mode="brain")
    return render_template("upload_brain.html")


@app.route("/upload/pneumonia", methods=["GET", "POST"])
def upload_pneumonia():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("No file uploaded")
            return redirect(request.url)
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        res = predict_pneumonia(save_path, pneumonia_model)
        user_id = current_user.id if current_user.is_authenticated else None
        rec = Upload(filename=filename, user_id=user_id, result_brain=None, result_pneumonia=res["label"])
        db.session.add(rec)
        db.session.commit()

        return render_template("result.html", image_url=url_for("static", filename="uploads/" + filename), result=res, mode="pneumonia")
    return render_template("upload_pneumonia.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")
    language = data.get("language", "en")
    voice = data.get("voice", False)
    if not message:
        return jsonify({"error": "No message provided"}), 400
    try:
        answer = ask_openai(message, language=language)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"reply": answer, "voice": voice})

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        user, err = create_user(email, password, name)
        if user:
            flash("Registered. Please log in.")
            return redirect(url_for("login"))
        else:
            flash(err)
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        u = verify_user(email, password)
        if u:
            login_user(UserLogin(u))
            flash("Logged in successfully.")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(current_user.id)
    uploads = Upload.query.filter_by(user_id=user.id).order_by(Upload.created_at.desc()).all()
    for upload in uploads:
        if upload.result_brain is not None:
            upload.brain_color = '#F25A8E' if upload.result_brain == 'Positive' else '#4CAF50'
        else:
            upload.brain_color = '#888'

        if upload.result_pneumonia is not None:
            upload.pneumonia_color = '#F25A8E' if upload.result_pneumonia == 'Positive' else '#4CAF50'
        else:
            upload.pneumonia_color = '#888'
    return render_template("dashboard.html", user=user, uploads=uploads)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
