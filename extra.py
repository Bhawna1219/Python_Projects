
import sqlite3
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'bhawna019'

users = {}

# Establish a connection to the SQL Server database
conn_str = sqlite3.connect('todoapp.db')
cursor = conn_str.cursor()

@app.route('/')
def index():
return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
if request.method == 'POST':
username = request.form['username']
password = request.form['password']

if username in users:
return 'Username already exists.'

hashed_password = generate_password_hash(password)
users[username] = hashed_password

return redirect('/login')
else:
return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
if request.method == 'POST':
username = request.form['username']
password = request.form['password']

if username in users and check_password_hash(users[username], password):
session['username'] = username
return redirect('/todo')
else:
return 'Invalid username or password.'
else:
return render_template('login.html')

@app.route('/logout')
def logout():
session.pop('username', None)
return redirect('/')

if __name__ == '__main__':
app.run(debug=True)












from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'bhawna19' # Change this to a secure secret key

DATABASE = 'todoapp.db'

def initialize_database():
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

# Create user table
c.execute('''CREATE TABLE IF NOT EXISTS users 
(id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
password TEXT NOT NULL)''')

# Create task table
c.execute('''CREATE TABLE IF NOT EXISTS tasks
(id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
task TEXT NOT NULL,
FOREIGN KEY (user_id) REFERENCES users (id))''')

conn.commit()
conn.close()

@app.route('/')
def index():
if 'username' in session:
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

# Retrieve tasks for the logged-in user
user_id = session['user_id']
c.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
tasks = c.fetchall()

conn.close()
return render_template('index.html', tasks=tasks)
return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
if request.method == 'POST':
username = request.form.get('username')
password = request.form.get('password')

if username and password:
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

# Check if the username already exists
c.execute('SELECT id FROM users WHERE username = ?', (username,))
existing_user = c.fetchone()

if existing_user:
conn.close()
return render_template('register.html', error='Username already exists.')

# Insert new user into the database
hashed_password = generate_password_hash(password)
c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
user_id = c.lastrowid
session['user_id'] = user_id

conn.commit()
conn.close()

return redirect('/')

return render_template('register.html', error='')

@app.route('/login', methods=['GET', 'POST'])
def login():
if request.method == 'POST':
username = request.form.get('username')
password = request.form.get('password')

if username and password:
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

# Retrieve user from the database
c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
user = c.fetchone()
print(user)

if user and check_password_hash(user[1], password):
session['username'] = username
session['user_id'] = user[0]
conn.close()
return redirect('/')
else:
conn.close()
return render_template('login.html', error='Invalid username or password.')

return render_template('login.html', error='')

@app.route('/logout')
def logout():
session.pop('username', None)
session.pop('user_id', None)
return redirect('/login')

@app.route('/add', methods=['POST'])
def add():
if 'username' in session:
task = request.form.get('task')
if task:
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

user_id = session['user_id']
c.execute('INSERT INTO tasks (user_id, task) VALUES (?, ?)', (user_id, task))

conn.commit()
conn.close()

return redirect('/')
return redirect('/login')

@app.route('/update/<int:index>', methods=['POST'])
def update(index):
if 'username' in session:
task = request.form.get('task')
if task:
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

user_id = session['user_id']
c.execute('UPDATE tasks SET task = ? WHERE id = ? AND user_id = ?', (task, index, user_id))

conn.commit()
conn.close()

return redirect('/')
return redirect('/login')

@app.route('/delete/<int:index>')
def delete(index):
if 'username' in session:
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

user_id = session['user_id']
c.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (index, user_id))

conn.commit()
conn.close()

return redirect('/')
return redirect('/login')

if __name__ == '__main__':
initialize_database()
app.run(debug=True)


<!DOCTYPE html>
<html>
<head>
<title>To-Do List</title>
</head>
<body>
<h1>To-Do List</h1>
<form action="/add" method="POST">
<input type="text" name="task" placeholder="Enter task" required>
<button type="submit">Add Task</button>
</form>
<ul>
<li>
<form action="/update/{{ index }}" method="POST">
<input type="text" name="task" value="{{ task }}" required>
<button type="submit">Update</button>
</form>
<a href="/delete/{{ index }}">Delete</a>
</li>
</ul>
</body>
</html>



































$(document).ready(function() {
$('#login-form').on('submit', function(e) {
e.preventDefault();

var username = $('#username').val();
var password = $('#password').val();

$.ajax({
url: '/login',
type: 'POST',
data: {username: username, password: password},
success: function(response) {
alert('Login successful!');
window.location.href = '/tasks';
},
error: function(xhr) {
alert(xhr.responseText);
}
});
});
});
