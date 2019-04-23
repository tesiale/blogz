from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/blog')
def blogs():
    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).all()
        home = False
    else:
        blog = Blog.query.all()
        home = True
    
    return render_template('blogpost.html', title="Build-A-Blog!", blogs=blog, home=home)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(user_id=['user_id']).first()

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        title_error = ""
        body_error = ""

        if not blog_title:
            title_error = "Please enter in a title"
        if not blog_body:
            body_error = "Please enter in a body"

        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))
        else:
            return render_template('newpost.html', title="New Post", title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)
    else:
        return render_template('newpost.html', title="New Post")


@app.route('/signup')
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        u_error = ''
        p_error = ''
        v_error = ''

        if not username:
            u_error = 'Please enter in a username'
        elif len(username) < 3 or len(username) > 25:
            u_error = 'Username must be between 3-25 characters long'

        if not password:
            p_error = 'Please enter in a password'
        elif len(password) < 3 or len(password) > 25:
            p_error = 'Password must be between 3-25 characters long'

        if not verify:
            v_error = 'Please confirm password'
        elif verify != password:
            v_error = 'Passwords do not match'

        if not u_error and not p_error and not v_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                exist_error = 'Username already exists'            
                return render_template('signup.html', exist_error=exist_error)
        else:
            return render_template('signup.html', 
            title="Blogz | Sign-Up",
            username_error=u_error,
            password_error=p_error,
            vpassword_error=v_error,
            username=username)

@app.route('/login')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif not user:
            flash('')
            return redirect('/login')
        else:
            flash('')
            return redirect('/login')

    return render_template('login.html')

@app.route('/index')
def index():


@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/")

if __name__ == '__main__':
    app.run()