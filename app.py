from flask import Flask, request, render_template
from database import init_db
import sqlite3
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search")
def search():
    query = request.args.get("cnic", "")
    conn = sqlite3.connect("police.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suspects WHERE cnic = '" + query + "'")
    results = cursor.fetchall()
    conn.close()
    return render_template("search.html", results=results, query=query)

@app.route("/report")
def report():
    name = request.args.get("name", "")
    return render_template("report.html", name=name)

@app.route("/download")
def download():
    filename = request.args.get("file", "")
    try:
        filepath = os.path.join("files", filename)
        f = open(filepath, "r")
        content = f.read()
        f.close()
        return content
    except:
        return "File not found"
    
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    