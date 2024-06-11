from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from config import Config
import random
from werkzeug.security import generate_password_hash, check_password_hash

def create_id():
    res = ''
    for i in range(12):
        res += f"{random.randint(0 , 9)}"
    return int(res)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

with app.app_context():
    db.create_all()

@app.route("/add_user", methods=["POST", "GET"])
def add_user():
    if request.method == "POST":
        if request.form.get('username') and request.form.get('email') and request.form.get('password'):
            new_user = User(username=request.form['username'], email=request.form['email'])
            new_user.set_password(request.form['password'])
            db.session.add(new_user)
            db.session.commit()
    return redirect(url_for('main'))

@app.route("/add_task/<int:user_id>", methods=["POST", "GET"])
def add_task(user_id):
    if request.method == "POST":
        new_task = Task(id=create_id(), user_id=user_id, content=request.form['task'])
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('user', id=user_id))

@app.route("/")
def main():
    if 'username' in session:
        users = User.query.all()
        return render_template("index.html", users=users)
    return redirect(url_for('login'))

@app.route('/user/<int:id>')
def user(id):
    if 'username' in session:
        return render_template("user.html", user=User.query.filter_by(id=id).first(), tasks=Task.query.filter_by(user_id=id).all())
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
  
        session['username'] = username
        return redirect(url_for('main'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()
