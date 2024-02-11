# app.py
import os
from flask import (
    Flask,
    jsonify,
    request,
    render_template_string,
    render_template,
    url_for,
    redirect,
    flash,
    send_from_directory,
)
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)

from werkzeug.utils import secure_filename

from model import User, File, FileShare, db

from utils import formatBytes


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f'sqlite:///{os.path.join(basedir, "instance/drive.db")}'
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "add_secret_key_here_for_session_security"

db.init_app(app)

UPLOAD_FOLDER = "docs"


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
    if "file" not in request.files:
        return "No file found"

    file = request.files["file"]
    if file.filename == "":
        return "No file found"

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        file_size = os.path.getsize(os.path.join(UPLOAD_FOLDER, filename))

        new_file = File(
            name=filename,
            path=os.path.join(UPLOAD_FOLDER, filename),
            user_id=current_user.id,
            file_size=file_size,
        )
        db.session.add(new_file)
        db.session.commit()

        return "File uploaded successfully"


@app.route("/users", methods=["GET"])
@login_required
def get_users():
    if not current_user.is_admin_user:
        return redirect(url_for("index"))

    all_users = User.query.all()
    return render_template("users.html", users=all_users)


@app.route("/files")
@login_required
def view_files():
    users = User.query.filter(User.id != current_user.id).all()
    shared_files = (
        File.query.join(FileShare).filter(FileShare.user_id == current_user.id).all()
    )

    if current_user.is_admin_user:
        files = File.query.all()
    else:
        files = File.query.filter_by(user_id=current_user.id).all()

    # List of users having access to each owned file
    shares = {}

    for file in files:
        shares[file.id] = [file_share.user_id for file_share in file.file_shares]

    return render_template(
        "files.html",
        files=files,
        shared_files=shared_files,
        shares=shares,
        users=users,
        formatBytes=formatBytes,
    )


@app.route("/change-permissions", methods=["POST"])
def change_file_permissions():
    data = request.get_json()

    file_id = data.get("file_id")
    user_id = data.get("user_id")
    can_view = data.get("checked")

    file_share = FileShare.query.filter_by(file_id=file_id, user_id=user_id).first()

    if can_view:
        if file_share is None:
            file_share = FileShare(file_id=file_id, user_id=user_id)
            db.session.add(file_share)
    else:
        if file_share:
            db.session.delete(file_share)

    db.session.commit()

    return jsonify(success=True)


# TODO : protect this route from unauthorized downloads


@app.route("/download/<int:id>")
@login_required
def download_file(id):
    file = File.query.get(id)
    return send_from_directory(UPLOAD_FOLDER, file.name, as_attachment=True)


# DEBUGGING ONLY : REMOVE IN PRODUCTION


@app.route("/drop-db")
def reset_db():
    db.drop_all()
    db.create_all()
    return "Database reset"


if __name__ == "__main__":
    app.run(debug=True)
