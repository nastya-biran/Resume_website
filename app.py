from flask import Flask, session, redirect, url_for, escape, request,  render_template, flash, send_file
import sqlite3
from flask import g
import pdfkit

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


app.config.update(dict(
    DATABASE="user",
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'))




def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('scheme.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()




@app.route('/')
def index():
    return render_template("layout.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    db.commit()
    error = None
    if request.method == 'POST':
        if db.execute("SELECT username  FROM user WHERE username= ?", (request.form['username'],)).fetchone() is None:
            error = 'Invalid username'
        elif db.execute("SELECT password  FROM user WHERE username= ?", (request.form['username'],)).fetchone()[0] != request.form['password']:
            error = 'Invalid password'
        else:
            session['username'] = request.form['username']
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('resume'))
    return render_template('login1.html', error=error)

@app.route('/register',  methods=['GET', 'POST'])
def register():
    error = None
    db = get_db()
    is_registered = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_registered = db.execute("SELECT username  FROM user WHERE username = ?", (username,)).fetchone()
        if is_registered is not None:
            error = 'Already registered, you can only log in'
        elif username == "":
            error = 'You should enter your username'
        elif password == "":
            error = 'You should enter your password'
        else:
            db.execute('INSERT INTO user (username, password, name, surname, age, education,\
                                         job_position, previous_workplace, projects) \
                                         VALUES (?, ?, "", "", "", "", "", "", "")', (username, password))
            db.commit()
            is_registered = True
    return render_template('register1.html', error=error, is_registered=is_registered)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out, wow')
    return redirect(url_for('index'))

@app.route('/resume', methods=['GET', 'POST'])
def resume():
    db = get_db()
    pdf_name = ""
    if request.method == 'POST':
        if request.form.get("save") == "Save":
            db.execute('UPDATE user SET name = ?, surname = ?, age =  ?, education = ?, job_position = ?, \
                                        previous_workplace = ?, projects = ? WHERE username = ?',
                                        (request.form["name"], request.form["surname"],
                                        request.form["age"], request.form["education"],
                                        request.form["job_position"], request.form["previous_workplace"],
                                        request.form["projects"], session["username"]))
            db.commit()
        else:
            saved_resume = db.execute("SELECT *  FROM user WHERE username= ?", (session['username'],)).fetchone()
            pdf_name = "resume_pdf/" + saved_resume['username'] + ".pdf"
            html = str(render_template('resume1.html', saved_resume=saved_resume))
            pdfkit.from_string(html, pdf_name, css="/home/nastya/PycharmProjects/HW3/static/beautiful.css",  options={"enable-local-file-access": ""})
            return send_file(pdf_name, as_attachment=True)
    saved_resume = db.execute("SELECT *  FROM user WHERE username= ?", (session['username'],)).fetchone()
    return render_template('resume1.html', saved_resume=saved_resume)

if __name__ == '__main__':
    init_db()
    app.run()