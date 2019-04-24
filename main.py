from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "gibberish"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blogs', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    display_users = User.query.all()
    return render_template('index.html', title="Blogz | Home", users=display_users)

@app.route('/blog')
def blogs():
    blog_id = request.args.get('id')
    blog_user = request.args.get('user')
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).all()
        main = False
    else:
        blog = Blog.query.all()
        main = True
    
    return render_template('blogpost.html', title="Blogz | Blogs", blogs=blog, main=main)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    user = User.query.filter_by(username=['username']).first()

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
            new_blog = Blog(blog_title, blog_body, user)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))
        else:
            return render_template('newpost.html', 
            title="New Post", 
            title_error=title_error, 
            body_error=body_error, 
            blog_title=blog_title, 
            blog_body=blog_body)
    else:
        return render_template('newpost.html', title="Blogz | New Post")


@app.route('/signup', methods=['POST', 'GET'])
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
            verify_error=v_error,
            username=username)
    else:
        return render_template('signup.html', title="Blogz | Sign-Up")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif not user:
            flash('Username does not exist')
            return redirect('/login')
        else:
            flash('Invalid Password')
            return redirect('/login')
    else:
        return render_template('login.html', title='Blogz | Login')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()