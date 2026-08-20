
# 🎓 Learning Management System (LMS) - lxpv1.0

A professional, role-based Learning Management System built with Django. This platform streamlines academic scheduling with conflict detection, student enrollment via the Finance Hub, and resource distribution.

---

## 🚀 Key Features

### 📅 Advanced Timetable Management

* **Weekly Board View:** A clean, Kanban-style layout showing classes from Monday to Friday.
* **Atomic Recurrence:** Create weekly schedules for an entire semester in one click with database rollback protection.
* **Smart Conflict Detection:** Automatically prevents double-booking trainers or locations during creation.
* **FullCalendar Integration:** Toggle between a structured table and an interactive monthly calendar.

### 💰 Finance & Admissions Hub

* **Course-Based Enrollment:** Link students to specific courses (Nursing, Engineering, etc.) to tailor their experience.
* **Staff-Only Access:** Hidden dashboard icons and protected views ensure only authorized personnel manage billing.
* **Billing Overview:** Quick access to update student payments and track outstanding balances.

### 👥 Role-Based Dashboard

* **Dynamic UI & Left Sidebar Navigation:** Responsive left-side navbar layout with drawer toggle for mobile devices.
* **Course-Based Admissions:** Student admission forms directly populate available options from the central Courses and Units module.
* **Hierarchical Results Verification:** Results module organizes student performance verification via a 4-tier drill-down flow (Cohorts → Courses → Students → Unit Results).
* **Trainer Assignment Protection:** Conflict prevention ensures a specific unit in a given cohort can only be assigned to a single trainer.
* **Course Filtering:** Students and Staff can filter the global timetable to see only the schedule for a specific course.
* **Flash Feedback:** Instant success/error alerts for all administrative actions with auto-dismiss functionality.

---

## 🛠️ Technology Stack

| Layer | Technology |
| --- | --- |
| **Backend** | Django 5.1 (Python 3.10+) |
| **Frontend** | Bootstrap 5, FontAwesome 6, Vanilla JS |
| **Database** | SQLite (Development) / PostgreSQL (Production) |
| **Calendar** | FullCalendar.io v6 |
| **Icons** | FontAwesome 6 Free |

---

## 📦 Installation & Setup

### 1. Clone and Branch

```bash
git clone https://github.com/your-username/lms.git
cd lms
git checkout -b lxpv1.0

```

### 2. Environment Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 3. Database & Superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

```

### 4. Launch

```bash
python manage.py runserver

```

Visit `http://127.0.0.1:8000` to view the dashboard.

---

## 📁 Project Structure

```text
lms/
├── finance/             # Course fees, student accounts, and admissions
├── timetable/           # Scheduling logic, conflict checks, and calendar
├── resources/           # Learning materials and file management
├── assignments/         # Quizzes, grading, and submissions
├── templates/           # Global base.html and shared components
├── static/              # CSS, JS, and Brand Assets
└── manage.py

```

---

## 👥 User Roles

### **Super Admin / Registrar**

* Full access to the **Finance Hub** and **Student Directory**.
* Ability to create recurring timetable entries with conflict validation.
* Manage system-wide courses and fee structures.

### **Trainer**

* View the consolidated weekly timetable.
* Upload learning resources and manage assignments.
* Provide feedback on student submissions.

### **Student**

* View a personalized dashboard with learning portal access.
* Filter the timetable by their enrolled course.
* Download resources and track class locations.

---

## 🔧 Configuration (.env)

Create a `.env` file in the root directory to manage your secrets:

```env
DEBUG=True
SECRET_KEY=django-insecure-your-key-here
DATABASE_URL=sqlite:///db.sqlite3

```

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

**Version**: lxpv1.0

**Status**: Development - Feature Complete


