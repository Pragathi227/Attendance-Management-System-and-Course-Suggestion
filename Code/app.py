from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# File upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# === DB Connection ===
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mysql@123",
        database="attendance_db"
    )


# === Home/Login Page ===
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            if user['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            error = 'Invalid username or password.'

    return render_template('login.html', error=error)


# === Logout ===
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# === Teacher Dashboard ===
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    return render_template('dashboard_teacher.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    if request.method == 'POST':
        low_attendance_link = request.form['low_attendance_link']
        avg_attendance_link = request.form['avg_attendance_link']
        high_attendance_link = request.form['high_attendance_link']

        # TODO: Save to DB (we're skipping DB here just for testing)
        print("🔗 Low:", low_attendance_link)
        print("🔗 Avg:", avg_attendance_link)
        print("🔗 High:", high_attendance_link)

        return redirect(url_for('teacher_dashboard'))

    return render_template('dashboard_teacher.html')




# === Student Dashboard ===
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT link FROM class_links ORDER BY uploaded_at DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    class_link = row['link'] if row else None
    return render_template('dashboard_student.html', class_link=class_link)


# === Upload Attendance Excel (Teacher) ===
@app.route('/upload_attendance', methods=['POST'])
def upload_attendance():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    if 'attendance_file' in request.files and 'subject' in request.form:
        subject = request.form['subject']
        file = request.files['attendance_file']
        if file.filename.endswith('.xlsx'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            process_attendance(filepath, subject)
            return redirect(url_for('teacher_dashboard'))
    return "Invalid file format or subject missing", 400


def process_attendance(filepath, subject):
    df = pd.read_excel(filepath)

    if not all(col in df.columns for col in ['Student Name', 'Roll Number', 'Date', 'Status']):
        raise ValueError("Excel must have: Student Name, Roll Number, Date, Status")

    df['Date'] = pd.to_datetime(df['Date'])
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert attendance records
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO attendance (student_name, roll_number, date, status, subject)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            row['Student Name'], row['Roll Number'], row['Date'].date(), row['Status'], subject
        ))

    conn.commit()

    # Calculate attendance percentage
    cursor.execute("SELECT DISTINCT student_name, roll_number FROM attendance WHERE subject = %s", (subject,))
    students = cursor.fetchall()

    for student in students:
        name, roll = student
        cursor.execute("""
            SELECT COUNT(*) FROM attendance
            WHERE subject = %s
        """, (subject,))
        total_classes = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM attendance
            WHERE subject = %s AND student_name = %s AND status = 'Present'
        """, (subject, name))
        days_present = cursor.fetchone()[0]

        percentage = round((days_present / total_classes) * 100, 2) if total_classes > 0 else 0

        cursor.execute("""
            INSERT INTO attendance_summary (student_name, roll_number, subject, total_classes, days_present, attendance_percentage)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            total_classes = VALUES(total_classes),
            days_present = VALUES(days_present),
            attendance_percentage = VALUES(attendance_percentage)
        """, (name, roll, subject, total_classes, days_present, percentage))

    conn.commit()
    cursor.close()
    conn.close()




# === Upload Class Link (Teacher) ===
@app.route('/upload_class_link', methods=['POST'])
def upload_class_link():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    link = request.form['class_link']
    uploader = session['username']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO class_links (link, uploaded_by) VALUES (%s, %s)", (link, uploader))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('teacher_dashboard'))


# === Attendance Report (Student & Teacher) ===
@app.route('/report')
def report():
    if 'username' not in session:
        return redirect(url_for('login'))

    student_name = session['username']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all subjects
    cursor.execute("SELECT DISTINCT subject FROM attendance")
    subjects = [row['subject'] for row in cursor.fetchall()]

    summary = []

    for subject in subjects:
        # Total distinct dates (i.e., total classes conducted)
        cursor.execute("""
            SELECT COUNT(DISTINCT date) AS total_classes
            FROM attendance
            WHERE subject = %s
        """, (subject,))
        total_classes = cursor.fetchone()['total_classes']

        # Count of presents for the student
        cursor.execute("""
            SELECT COUNT(*) AS days_present
            FROM attendance
            WHERE subject = %s AND student_name = %s AND LOWER(status) = 'present'
        """, (subject, student_name))
        days_present = cursor.fetchone()['days_present']

        # Avoid division by zero
        if total_classes == 0:
            percentage = 0
        else:
            percentage = round((days_present / total_classes) * 100, 2)

        # Fetch YouTube link suggestion
        if percentage < 50:
            level = 'low'
        elif percentage < 80:
            level = 'average'
        else:
            level = 'high'

        cursor.execute("""
            SELECT link FROM youtube_links WHERE subject = %s AND level = %s
        """, (subject, level))
        yt_result = cursor.fetchone()
        suggested_link = yt_result['link'] if yt_result else None

        summary.append({
            "subject": subject,
            "total_classes": total_classes,
            "days_present": days_present,
            "attendance_percentage": percentage,
            "suggested_link": suggested_link
        })

    cursor.close()
    conn.close()

    return render_template("report.html", summary=summary)




if __name__ == '__main__':
    app.run(debug=True)
