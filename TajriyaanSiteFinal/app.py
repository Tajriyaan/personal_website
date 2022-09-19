# Importing flask module in the project is mandatory
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
from flask_mail import Mail, Message
from config import mail_username, mail_password



# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__, static_folder='static')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/tajri/Desktop/TajriyaanSitewithFlask/blog.db'

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'mysql://root:''@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password

mail = Mail(app)

# Database model
class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70),unique=True,)
    author = db.Column(db.String(30))
    date_posted = db.Column(db.DateTime(timezone=True),server_default=func.now())
    content = db.Column(db.Text)

    def __repr__(self):
        return f'<Title {self.title}>'
    
# Create the database
db.create_all()
print('Database Created! \n')

# Main site
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

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

    return render_template('posts.html', posts=posts)

# Show Particular post


@app.route('/posts/<int:id>')
def post(id):

    post = Blogpost.query.get_or_404(id)

    return render_template('post.html', post=post)

# Add blog post


@app.route('/add')
def add():
    return render_template('add.html')

# Add blog post to database


@app.route('/addpost', methods=['GET', 'POST'])
def addpost():
    title = request.form['title']
    author = request.form['author']
    content = request.form['content']

    post = Blogpost(title=title, author=author,
                    content=content, date_posted=datetime.now())

    db.session.add(post)
    db.session.commit()

    # return '<h1>Title:{} <br> Author:{} <br> Content:{}  <br> </h1>'.format(title,author,content)

    return redirect(url_for('posts'))


# main driver function
   # run() method of Flask class runs the application
    # on the local development server.
if __name__ == '__main__':
    app.run(debug=True)
