from flask import Flask, request, redirect, render_template
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

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog')
def blogs():
    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).all()
    else:
        blog = Blog.query.all()
    
    return render_template('blogpost.html', title="Build-A-Blog!", blogs=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
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
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))
        else:
            return render_template('newpost.html', title="New Post", title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)
    else:
        return render_template('newpost.html', title="New Post")


if __name__ == '__main__':
    app.run()