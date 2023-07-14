from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'bhawna19' 


DATABASE = 'todo.db'

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
                 title TEXT NOT NULL,
                 description TEXT,
                 status TEXT,
                 FOREIGN KEY (user_id) REFERENCES users (id))''')
    

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/loginpage')
def loginpage():
    return render_template('login.html')

@app.route('/registerpage')
def registerpage():
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()       
        
        # Check if the username already exists
        cursor.execute('SELECT id FROM users WHERE username=?', (username,))
        user = cursor.fetchone()
        if user:
            conn.close()
            return 'Username already exists'

        # Insert the new user into the database
        hashed_password = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()

        return redirect('/login')
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if the username and password match
        cursor.execute('SELECT id, password FROM users WHERE username=?', (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[1], password):
            session['username'] = username
            session['user_id'] = user[0]
            conn.close()
            return jsonify({'success': True})
        else:
            conn.close()
            return jsonify({'success': False, 'message': 'Invalid username or password'})
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


@app.route('/tasks')
def tasks():
    if 'user_id' in session:
        user_id = session['user_id']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Retrieve the tasks for the logged-in user
        cursor.execute('SELECT id, title, description, status FROM tasks WHERE user_id=?', (user_id,))
        tasks = cursor.fetchall()

        conn.close()

        return render_template('tasks.html', tasks=tasks)
    else:
        return redirect('/login')

@app.route('/add_task', methods=['POST'])
def addtask():
    if 'user_id' in session:
        user_id = session['user_id']

        title= request.form['title']
        description= request.form['description']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        #Insert into tasks table
        cursor.execute('INSERT INTO tasks (user_id, title, description, status) VALUES (?, ?, ?, ?)', (user_id,title, description,'Pending'))
        conn.commit()
        conn.close()

        return redirect('/tasks')
    else:
        return redirect('/login')


@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    status = request.form['status']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Update the status of the task in the database
    cursor.execute('UPDATE tasks SET status=? WHERE id=?', (status, task_id))
    conn.commit()

    conn.close()

    return redirect('/tasks')

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Delete the task from the database
    cursor.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    conn.commit()

    conn.close()

    return redirect('/tasks')

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
