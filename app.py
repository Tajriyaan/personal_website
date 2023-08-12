# Importing flask module in the project is mandatory
from flask import Flask, render_template, request, redirect, url_for,flash
import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
from flask_mail import Mail, Message
from config import mail_username, mail_password,upload_folder,secret_key
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
import json



UPLOAD_FOLDER = upload_folder


# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__, static_folder='static')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = secret_key

# get the path to the project directory
project_dir = os.path.dirname(os.path.abspath(__file__))

# set the path to the database file
database_dir = os.path.join(project_dir, "database")
if not os.path.exists(database_dir):
    os.makedirs(database_dir)

database_file = "sqlite:///{}".format(os.path.join(database_dir, "blog.db"))

# check if blog.db exists, otherwise create it
if os.path.exists(os.path.join(database_dir, "blog.db")):
    print('Database Found!')
else:
    conn = sqlite3.connect(os.path.join(database_dir, "blog.db"))
    conn.close()
    print('Database Created! \n')

app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Database model
class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(10000), nullable=True, default='default.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    # date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Blogpost('{self.title}', '{self.author}', '{self.date_posted}')"

with app.app_context():
    # Create the database
    db.create_all()


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password

mail = Mail(app)

    
# Main site
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# Add blog post to database
@app.route('/addpost', methods=['GET', 'POST'])
def addpost():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']
        files = request.files.getlist('image')

        filepaths = []
        for file in files:
            try:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.root_path, UPLOAD_FOLDER, filename))
                filepaths.append(os.path.join(UPLOAD_FOLDER, filename))
            except Exception as e:
                print(f"Error uploading file: {e}")
                filepaths.append('')
            print("filepaths:", filepaths)

        # Serialize the list of image paths to a JSON string
        image_json = json.dumps(filepaths)

        # Create new blog post object
        post = Blogpost(title=title, author=author,
                        content=content, image=image_json, date_posted=datetime.utcnow())

        # Add post to database
        db.session.add(post)
        db.session.commit()

        # Show success message
        flash('Blog post added successfully', 'success')

        return redirect(url_for('posts'))

    return render_template('posts.html')



# Add blog post to database
# @app.route('/addpost', methods=['GET', 'POST'])
# def addpost():
#     if request.method == 'POST':
#         title = request.form['title']
#         author = request.form['author']
#         content = request.form['content']
#         file = request.files.get('image')
        
#         # Check if file was uploaded
#         filename = ''
#         if file:
#             try:
#                 # Get secure filename
#                 filename = secure_filename(file.filename)
#                 # Save file to UPLOAD_FOLDER directory
#                 file.save(os.path.join(app.root_path, UPLOAD_FOLDER, filename))
#                 # Set file path
#                 filepath = os.path.join(UPLOAD_FOLDER, filename)
#             except Exception as e:
#                 # Catch any exceptions that may occur during file upload
#                 print(f"Error uploading file: {e}")
#                 filepath = ''
#         else:
#             # No file uploaded, set filepath to empty string
#             filepath = ''

#         print(f"filename: {filename}")
#         print(f"filepath: {filepath}")

#         # Create new blog post object
#         post = Blogpost(title=title, author=author,
#                         content=content, image=filepath, date_posted=datetime.utcnow())

#         # Add post to database
#         db.session.add(post)
#         db.session.commit()

#         # Show success message
#         flash('Blog post added successfully', 'success')
        
#         return redirect(url_for('posts'))

#     return render_template('posts.html')



# Send Email Successfully

# Send mail
@app.route('/send_mail', methods=['GET', 'POST'])
def send_mail():
    if request.method == "POST":
        name = request.form.get("name")
        subject = request.form.get("subject")
        email = request.form.get("email")
        message = request.form.get("message")

        msg = Message(subject=f"Mail from: {name} & Email: {email}",
                      sender=email, recipients=[mail_username])
        msg.body = message
        mail.send(msg)
        return "Sent Email!"

    return render_template('index.html', success=True)


@app.route('/posts')
def posts():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    for post in posts:
        post.image = json.loads(post.image)
        print(post.image)
    return render_template('posts.html', posts=posts)

    # Get flash message, if any
    message = None
    if 'message' in session:
        message = session['message']
        session.pop('message', None)

    return render_template('posts.html', posts=posts, message=message)


# Show Particular post


@app.route('/posts/<int:id>')
def post(id):

    post = Blogpost.query.get_or_404(id)

    return render_template('post.html', post=post)

# Add blog post


@app.route('/add')
def add():
    return render_template('add.html')





# main driver function
   # run() method of Flask class runs the application
    # on the local development server.
if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
