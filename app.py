from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os
import subprocess
import time

app = Flask(__name__)

# ============================================
# DATABASE CONNECTION
# ============================================
def get_db():
    conn = sqlite3.connect("police.db")
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# EXISTING ROUTES
# ============================================

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    query = request.args.get('cnic', '').strip()
    results = []
    error = None
    
    if query:
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # VULNERABLE: SQL Injection (including Blind SQLi)
            # Wapiti detects this
            query = f"SELECT * FROM suspects WHERE cnic = '{query}' OR name LIKE '%{query}%'"
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template('search.html', results=results, query=query, error=error)

@app.route('/report')
def report():
    suspect_id = request.args.get('id', '')
    report = None
    
    if suspect_id and suspect_id.isdigit():
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suspects WHERE id = ?", (suspect_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # VULNERABLE: Command Injection hidden here (Wapiti will find it)
                report = {
                    'id': row[0],
                    'name': row[1],
                    'cnic': row[2],
                    'crime': row[3],
                    'status': row[4],
                    'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'summary': f"Suspect {row[1]} is accused of {row[3]}. Status: {row[4]}. Further investigation required."
                }
        except Exception:
            pass
    
    return render_template('report.html', report=report)

# ============================================
# UPDATED DOWNLOAD ROUTE (Replaces old /download/<filename>)
# ============================================
@app.route('/download')
def download_page():
    suspect_id = request.args.get('id', '')
    case_file = None
    requested = None
    
    if suspect_id and suspect_id.isdigit():
        requested = suspect_id
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suspects WHERE id = ?", (suspect_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                case_file = {
                    'id': row[0],
                    'name': row[1],
                    'cnic': row[2],
                    'crime': row[3],
                    'status': row[4],
                    'filed_at': time.strftime('%Y-%m-%d'),
                    'officer': 'Inspector Ahmad Khan',
                    'case_status': 'Under Investigation' if row[4] == 'Wanted' else 'Closed',
                    'summary': f"Case against {row[1]} for {row[3]}. Suspect is currently {row[4]}. Evidence collected, awaiting trial."
                }
        except Exception as e:
            pass
    
    return render_template('download.html', case_file=case_file, requested=requested)

# ============================================
# ACTUAL FILE DOWNLOAD ROUTE (Path Traversal)
# ============================================
@app.route('/download-file/<int:id>')
def download_file(id):
    # VULNERABLE: Path Traversal - Wapiti detects this
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suspects WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return "Suspect not found", 404
        
        format_type = request.args.get('format', 'txt')
        
        # Generate case file content
        content = f"""
========================================
PUNJAB POLICE - CASE FILE
========================================

Case ID: {row[0]}
Suspect Name: {row[1]}
CNIC: {row[2]}
Crime: {row[3]}
Status: {row[4]}
Filed: {time.strftime('%Y-%m-%d %H:%M')}
Officer: Inspector Ahmad Khan

----------------------------------------
CASE SUMMARY
----------------------------------------
{row[1]} is accused of {row[3]}. 
Current status: {row[4]}.
Evidence collected and under review.

----------------------------------------
THIS IS A CONFIDENTIAL DOCUMENT
----------------------------------------
        """
        
        if format_type == 'json':
            import json
            content = json.dumps({
                'id': row[0],
                'name': row[1],
                'cnic': row[2],
                'crime': row[3],
                'status': row[4],
                'filed_at': time.strftime('%Y-%m-%d %H:%M'),
                'officer': 'Inspector Ahmad Khan'
            }, indent=2)
            filename = f"case_{id}.json"
        else:
            filename = f"case_{id}.txt"
        
        # Create a temporary file to serve (vulnerable to path traversal)
        os.makedirs('files', exist_ok=True)
        temp_path = os.path.join('files', filename)
        with open(temp_path, 'w') as f:
            f.write(content)
        
        return send_file(temp_path, as_attachment=True)
        
    except Exception as e:
        return str(e), 500

# ============================================
# OLD DOWNLOAD ROUTE (Keep for backwards compatibility)
# ============================================
@app.route('/download/<filename>')
def download_old(filename):
    # VULNERABLE: Path Traversal
    # This is your existing vulnerable route
    return send_file(f"files/{filename}")

# ============================================
# NEW VULNERABILITY 2: Stored XSS
# ============================================
@app.route('/add-suspect', methods=['GET', 'POST'])
def add_suspect():
    message = None
    
    if request.method == 'POST':
        name = request.form.get('name', '')
        cnic = request.form.get('cnic', '')
        crime = request.form.get('crime', '')
        status = request.form.get('status', 'Wanted')
        
        # VULNERABLE: Stored XSS - No sanitization
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO suspects (name, cnic, crime, status) VALUES (?, ?, ?, ?)",
            (name, cnic, crime, status)
        )
        conn.commit()
        conn.close()
        
        message = f"✅ Suspect '{name}' added successfully!"
    
    return render_template('add_suspect.html', message=message)

# ============================================
# NEW VULNERABILITY 3: Command Injection
# ============================================
@app.route('/generate-report')
def generate_report():
    suspect_id = request.args.get('id', '')
    output = None
    error = None
    
    if suspect_id:
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM suspects WHERE id = ?", (suspect_id,))
            suspect = cursor.fetchone()
            conn.close()
            
            if suspect:
                name = suspect['name']
                # VULNERABLE: Command injection
                command = f"echo 'Generating report for suspect: {name}'"
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
            else:
                error = "Suspect not found"
        except Exception as e:
            error = str(e)
    
    return render_template('generate_report.html', output=output, error=error)

# ============================================
# NEW VULNERABILITY 4: IDOR
# ============================================
@app.route('/suspect-details/<int:id>')
def suspect_details(id):
    # VULNERABLE: IDOR - No authorization check
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suspects WHERE id = ?", (id,))
    suspect = cursor.fetchone()
    conn.close()
    
    return render_template('suspect_details.html', suspect=suspect)

# ============================================
# NEW VULNERABILITY 5: CSRF (No Token)
# ============================================
@app.route('/delete-suspect/<int:id>', methods=['POST'])
def delete_suspect(id):
    # VULNERABLE: CSRF - No token validation
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM suspects WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('home'))

# ============================================
# NEW VULNERABILITY 6: Path Traversal (Enhanced)
# ============================================
@app.route('/download-report/<filename>')
def download_report(filename):
    # VULNERABLE: Path Traversal
    return send_file(f"reports/{filename}")

# ============================================
# RUN
# ============================================
if __name__ == '__main__':
    app.run(debug=True)