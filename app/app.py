import os
import sqlite3
from flask import Flask, jsonify, request, render_template, g


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or os.environ.get("DB_PATH", "/data/tasks.db")
    app.config["VERSION"] = os.environ.get("APP_VERSION", "dev")

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with sqlite3.connect(app.config["DB_PATH"]) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL, "
            "done INTEGER NOT NULL DEFAULT 0)"
        )

    @app.get("/")
    def index():
        return render_template("index.html", version=app.config["VERSION"][:7])

    @app.get("/health")
    def health():
        return jsonify(status="ok", version=app.config["VERSION"])

    @app.get("/api/tasks")
    def list_tasks():
        rows = get_db().execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
        return jsonify([dict(r) for r in rows])

    @app.post("/api/tasks")
    def add_task():
        title = (request.get_json(silent=True) or {}).get("title", "").strip()
        if not title:
            return jsonify(error="title is required"), 400
        db = get_db()
        cur = db.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        db.commit()
        return jsonify(id=cur.lastrowid, title=title, done=0), 201

    @app.patch("/api/tasks/<int:task_id>/toggle")
    def toggle_task(task_id):
        db = get_db()
        cur = db.execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))
        db.commit()
        if cur.rowcount == 0:
            return jsonify(error="not found"), 404
        return jsonify(ok=True)

    @app.delete("/api/tasks/<int:task_id>")
    def delete_task(task_id):
        db = get_db()
        cur = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        db.commit()
        if cur.rowcount == 0:
            return jsonify(error="not found"), 404
        return jsonify(ok=True)

    return app
