# 🏠 Hostel Management System

## 📌 Project Overview
The **Hostel Management System** is a **basic working prototype** built for demonstrating how database management can be used to efficiently handle hostel operations like room booking, mess management, student complaints, and feedback.

This project is developed using **Python (Flask Framework)** for the backend, **HTML/CSS** for the frontend, and a **SQL database** for storing and managing hostel-related data.

---

## 🎯 Objective
To create a simple and interactive web application that helps both **students** and **administrators** manage hostel activities such as:
- Room allocation and booking  
- Mess management  
- Complaint and feedback submission  
- User authentication and access control

---

## 🧠 Key Features
### 👨‍💼 Admin Module
- Admin login and dashboard  
- Manage rooms and mess schedules  
- View complaints and feedback from students  
- Track access logs and user activity  

### 👨‍🎓 Student Module
- Student registration and login  
- Book rooms and mess services  
- Submit feedback and complaints  
- Update personal profiles and passwords  

---

## 🛠️ Technologies Used
- **Python (Flask Framework)**
- **HTML, CSS (Frontend)**
- **SQLite / MySQL (Database)**
- **Jinja2 Templates**
- **Bootstrap (Optional for styling)**
## 📁 Project Structure
hostel_management_system/
│
├── static/
│ └── style.css # Stylesheet for the website
│
├── templates/
│ ├── admin_dashboard.html
│ ├── admin_login.html
│ ├── admin_profile.html
│ ├── book_room.html
│ ├── complaint.html
│ ├── index.html
│ ├── login.html
│ ├── manage_rooms.html
│ ├── mess_booking.html
│ ├── student_registration.html
│ ├── submit_feedback.html
│ ├── user_dashboard.html
│ ├── user_profile.html
│ └── ... (other pages)
│
└── app.py # Main Flask application file

---

## ⚙️ How to Run the Project

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Hari0218/hostel_management_system.git
   cd hostel_management_system

virtual environment for this
python -m venv venv
venv\Scripts\activate

---
install applicaations 
pip install flask

run the apllications
python app.py



