# app.py
import os
from flask import (
    Flask,
    request,
    render_template_string,
    render_template,
    url_for,
    redirect,
    flash,
)
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)

from model import User, db

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f'sqlite:///{os.path.join(basedir, "instance/drive.db")}'
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "add_secret_key_here_for_session_security"

db.init_app(app)


with app.app_context():
    db.create_all()


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password_hash(password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            print("Invalid username or password")
            flash("Invalid username or password")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists.")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)

        if request.form.get("admin"):
            new_user.set_admin()

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return render_template_string(
        """
        <!doctype html>
        <html>
        <head>
            <title>Upload File</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/dropzone/5.7.2/min/dropzone.min.js"></script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/dropzone/5.7.2/min/dropzone.min.css" />
        </head>
        <body>
            <form action="/upload" class="dropzone" id="my-awesome-dropzone"></form>
        </body>
        </html>
    """
    )


@app.route("/upload", methods=["POST"])
def file_upload():
    file = request.files["file"]
    file.save("docs/" + file.filename)  # Replace with your desired save path
    return "File uploaded successfully"


@app.route("/users", methods=["GET"])
@login_required
def get_users():
    if not current_user.is_admin_user:
        return redirect(url_for("index"))

    all_users = User.query.all()
    return render_template("users.html", users=all_users)


if __name__ == "__main__":
    app.run(debug=True)
