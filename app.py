from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
import sqlite3
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling

# Hardcoded admin credentials (Change as needed)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

@app.route('/')
def index():
    return render_template('index.html', selected_date='', no_data=False, attendance_data=[])

@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (formatted_date,))
    attendance_data = cursor.fetchall()

    conn.close()

    if not attendance_data:
        return render_template('index.html', selected_date=selected_date, no_data=True, attendance_data=[])

    return render_template('index.html', selected_date=selected_date, attendance_data=attendance_data, no_data=False)

@app.route('/download_attendance', methods=['POST'])
def download_attendance():
    selected_date = request.form.get('selected_date')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (formatted_date,))
    attendance_data = cursor.fetchall()
    conn.close()

    if not attendance_data:
        return render_template('index.html', selected_date=selected_date, no_data=True, attendance_data=[])

    df = pd.DataFrame(attendance_data, columns=["Name", "Time"])
    file_path = f"attendance_{formatted_date}.xlsx"
    df.to_excel(file_path, index=False, engine='openpyxl')

    return send_file(file_path, as_attachment=True)

@app.route('/delete_attendance', methods=['POST'])
def delete_attendance():
    selected_date = request.form.get('selected_date')
    username = request.form.get('username')
    password = request.form.get('password')

    # Authenticate admin credentials
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
        formatted_date = selected_date_obj.strftime('%Y-%m-%d')

        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance WHERE date = ?", (formatted_date,))
        conn.commit()
        conn.close()

        flash("Attendance deleted successfully!", "success")
    else:
        flash("Invalid credentials! Attendance not deleted.", "danger")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
