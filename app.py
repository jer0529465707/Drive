# app.py
from flask import Flask, request, render_template_string, render_template

from model import User, db

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drive.db'

@app.route('/')
def index():
    return render_template_string('''
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
    ''')

@app.route('/upload', methods=['POST'])
def file_upload():
    file = request.files['file']
    file.save("docs/" + file.filename)  # Replace with your desired save path
    return 'File uploaded successfully'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return 'Username already exists!'

        # Create new user and add to database
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return 'Signup successful!'

    return render_template("signup.html")


if __name__ == '__main__':
    app.run(debug=True)
