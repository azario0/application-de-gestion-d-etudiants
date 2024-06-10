from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'school'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['loggedin'] = True
            session['admin'] = True
            return redirect(url_for('admin'))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['user_id']
            session['username'] = account['username']
            return redirect(url_for('student'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/student')
def student():
    if 'loggedin' in session and not session.get('admin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT u.first_name, u.last_name, c.class_name FROM users u JOIN classes c ON u.class_id = c.class_id WHERE u.user_id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.execute('SELECT module_name, mark FROM modules WHERE user_id = %s', (session['id'],))
        modules = cursor.fetchall()
        return render_template('student.html', account=account, modules=modules)
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'loggedin' in session and session.get('admin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM classes')
        classes = cursor.fetchall()
        
        selected_class = request.form.get('class_id')
        selected_module = request.form.get('module_name')
        
        students = []
        if selected_class and selected_module:
            cursor.execute('''
                SELECT u.first_name, u.last_name, m.mark 
                FROM users u 
                JOIN modules m ON u.user_id = m.user_id 
                WHERE u.class_id = %s AND m.module_name = %s
            ''', (selected_class, selected_module))
            students = cursor.fetchall()
        
        return render_template('admin.html', classes=classes, students=students, selected_class=selected_class, selected_module=selected_module)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
