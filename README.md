**📘 Student Attendance Management System**


**📌 Project Overview**

The Student Attendance Management System is a web-based application developed using Flask and MySQL that simplifies the process of managing student attendance for educational institutions. The system supports role-based access for teachers and students, allowing teachers to upload attendance records, class links, and YouTube course suggestions, while students can view attendance reports, join subject-wise classes, and access personalized learning resources based on their attendance performance.

---
**🎯 Objectives**

- Automate student attendance management
- Provide subject-wise latest class links
- Generate attendance reports with percentage calculation
- Suggest learning resources based on attendance levels
- Enable secure role-based access for teachers and students
  
---
**🛠️ Technologies Used**

- Backend: Python (Flask)
- Frontend: HTML, CSS
- Database: MySQL
- Data Processing: Pandas
- Tools: VS Code, MySQL Workbench

---
**✨ Features**

**👩‍🏫 Teacher Module**

- Secure login
- Upload attendance via Excel files
- Upload subject-wise class links
- Upload YouTube course suggestions
- View student attendance reports

**👨‍🎓 Student Module**

 Secure login
- View subject-wise latest class links
- View attendance percentage
- Access personalized YouTube learning recommendations

---
**🗂️ Project Structure**

```bash
student-attendance-management/
│
├── app.py
├── requirements.txt
├── uploads/
├── static/
│   └── style.css
├── templates/
│   ├── login.html
│   ├── dashboard_teacher.html
│   ├── dashboard_student.html
│   ├── report.html
└── README.md
```

---
**🧩 Database Tables Used**

- users
- attendance
- attendance_summary
- class_links
- youtube_links

---
**⚙️ Installation & Setup**

- Clone the repository

git clone https://github.com/your-username/student-attendance-management.git


- Navigate to project directory

cd student-attendance-management


- Install dependencies

pip install -r requirements.txt


- Configure MySQL database and update credentials in app.py

Run the application

python app.py


- Open browser and visit

http://127.0.0.1:5000/

---
**📈 Future Enhancements**

- Automated attendance using face recognition
- Email and notification alerts
- Graphical attendance analytics
- Mobile application support
- Integration with LMS platforms

---
**✅ Conclusion**

This project successfully demonstrates how web technologies can be used to automate attendance management while enhancing student learning through personalized course suggestions. The system is scalable, user-friendly, and suitable for academic institutions.
