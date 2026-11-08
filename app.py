import sqlite3
from flask import Flask, render_template, request, redirect, url_for, abort, g
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / 'notes.db'

app = Flask(__name__)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config.get("DATABASE", DATABASE))
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(app.config.get("DATABASE", DATABASE))
    db.executescript((BASE_DIR / 'schema.sql').read_text(encoding='utf-8'))
    db.commit()
    db.close()

@app.route('/')
def index():
    q = request.args.get('q', "").strip()
    db = get_db()
    if q:
        notes = db.execute(
            "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ?  ORDER BY id DESC",
            (f"%{q}%",f"%{q}%")).fetchall()
    else:
        notes = db.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
    return render_template('index.html', notes=notes, q=q)
# @app.route('/')
# def index():
#     return "<h1>Привіт! Сервер працює!</h1>"


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()

        if title:
            db = get_db()
            db.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (title, body))
            db.commit()
            return redirect(url_for('index'))

    return render_template('form.html', note=None)
@app.route('/note/<int:id>')
def view(id):
    db = get_db()
    note = db.execute("SELECT * FROM notes WHERE id = ?", (id,)).fetchone()
    if note is None:
        abort(404)
    return render_template('view.html', note=note)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/note/<int:id>/delete', methods=['POST'])
def delete(id):
    db = get_db()
    db.execute("DELETE FROM notes WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('index'))


@app.route('/note/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    db = get_db()
    note = db.execute("SELECT * FROM notes WHERE id = ?", (id,)).fetchone()
    if note is None:
        abort(404)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        if title:
            db.execute(
                "UPDATE notes SET title = ?, body = ? WHERE id = ?",
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('view', id=id))
    return render_template('form.html', note=note)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
























