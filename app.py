from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import pymysql.cursors
import json
from datetime import datetime
from flask_mail import Mail, Message
from config import mail_username, mail_password, upload_folder, secret_key,db_username
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = upload_folder

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = secret_key

db_config = {
    "host": "103.169.160.17",
    "user": db_username,
    "password": "asoijv#2314",
    "db": "blog",
    "port": 3306,
    "cursorclass": pymysql.cursors.DictCursor
}

db_connection = pymysql.connect(**db_config)

mail = Mail(app)

class Blogpost:
    def __init__(self, title, content, author, image, date_posted):
        self.title = title
        self.content = content
        self.author = author
        self.image = image
        self.date_posted = date_posted

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

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

        image_json = json.dumps(filepaths)

        with db_connection.cursor() as cursor:
            sql = "INSERT INTO blogpost (title, author, content, image, date_posted) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (title, author, content, image_json, datetime.utcnow()))
            db_connection.commit()

        flash('Blog post added successfully', 'success')
        return redirect(url_for('posts'))

    return render_template('posts.html')


@app.route('/edit/posts/<int:id>', methods=['GET', 'POST'])
def edit(id):
    with db_connection.cursor() as cursor:
        sql = "SELECT * FROM blogpost WHERE id = %s"
        cursor.execute(sql, (id,))
        post = cursor.fetchone()

        if request.method == 'POST':
            post["title"] = request.form['title']
            post["author"] = request.form['author']
            post["content"] = request.form['content']

            # Clear existing images and start with an empty list
            post_images = []

            # Process the uploaded images
            new_images = request.files.getlist('images')
            for new_image in new_images:
                if new_image:
                    filename = secure_filename(new_image.filename)
                    new_image.save(os.path.join(app.root_path, UPLOAD_FOLDER, filename))
                    post_images.append(os.path.join(UPLOAD_FOLDER, filename))

            # Convert the list of images to a JSON string
            post["image"] = json.dumps(post_images)

            sql = "UPDATE blogpost SET title = %s, author = %s, content = %s, image = %s WHERE id = %s"
            cursor.execute(sql, (post["title"], post["author"], post["content"], post["image"], id))
            db_connection.commit()

            flash('Blog post updated successfully', 'success')
            return redirect(url_for('posts'))

    return render_template('edit.html', post=post)




# @app.route('/edit/posts/<int:id>', methods=['GET', 'POST'])
# def edit(id):
#     with db_connection.cursor() as cursor:
#         sql = "SELECT * FROM blogpost WHERE id = %s"
#         cursor.execute(sql, (id,))
#         post = cursor.fetchone()

#         if request.method == 'POST':
#             post["title"] = request.form['title']
#             post["author"] = request.form['author']
#             post["content"] = request.form['content']

#             sql = "UPDATE blogpost SET title = %s, author = %s, content = %s WHERE id = %s"
#             cursor.execute(sql, (post["title"], post["author"], post["content"], id))
#             db_connection.commit()

#             flash('Blog post updated successfully', 'success')
#             return redirect(url_for('posts'))

#     return render_template('edit.html', post=post)

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
    with db_connection.cursor() as cursor:
        sql = "SELECT * FROM blogpost ORDER BY date_posted DESC"
        cursor.execute(sql)
        posts = cursor.fetchall()

        for post in posts:
            try:
                post["image"] = json.loads(post["image"])
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                post["image"] = []

    return render_template('posts.html', posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    with db_connection.cursor() as cursor:
        sql = "SELECT * FROM blogpost WHERE id = %s"
        cursor.execute(sql, (id,))
        post = cursor.fetchone()

    return render_template('post.html', post=post)

@app.route('/add')
def add():
    return render_template('add.html')



# Delete blog post API
@app.route('/delete/posts/<int:id>', methods=['GET', 'DELETE'])
def delete_post(id):
    with db_connection.cursor() as cursor:
        # Get the post details before deleting
        sql_select = "SELECT * FROM blogpost WHERE id = %s"
        cursor.execute(sql_select, (id,))
        post = cursor.fetchone()

        # Delete the post
        sql_delete = "DELETE FROM blogpost WHERE id = %s"
        cursor.execute(sql_delete, (id,))
        db_connection.commit()

    # Flash a message indicating successful deletion
    flash('Blog post deleted successfully', 'success')

    # Redirect back to the posts page after deletion
    return redirect(url_for('posts'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
