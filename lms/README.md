# 🎓 Learning Management System (LMS) - lxpv1.0

A professional, role-based Learning Management System built with Django. This platform streamlines academic scheduling with conflict detection, student enrollment via the Finance Hub, course & unit management, cohort tracking, trainer assignments, CAT/exam score processing, academic transcripts, and graduation eligibility management.

---

## 🚀 Key Features

### 📚 Courses & Units Management

* **Course Catalog:** Create, edit, and manage academic courses (e.g., Diploma in IT, Certificate in Nursing) and set school fees.
* **Automated Fee Sync:** Signals automatically create or update corresponding `CourseFee` records in the finance module whenever a course or its fee is modified.
* **Unit Mapping:** Define academic units with codes and descriptions mapped directly to specific courses.

### 👥 Cohort Management & Enhanced Admissions

* **Cohort Tracking:** Create and manage student intake cohorts (e.g., Jan 2026 Cohort, May 2026 Cohort).
* **Enhanced Student Registration:** Registration form featuring visual section indicators (`* Required` vs Optional), validation summary error alerts, physical address fields, and cohort assignment.
* **Student Directory:** Grouped student directory categorized by Course and Cohort, with direct profile editing capabilities.

### 👨‍🏫 Trainer Unit Assignments & Assessment Portal

* **Role-Filtered Assignments:** Assign trainers (`user_type == 'trainer'`) to specific units within a cohort.
* **Conflict Prevention:** Strict database and form-level constraints prevent assigning the same unit within a cohort to multiple trainers.
* **Dynamic Course Filtering:** Assign trainer form features dynamic JavaScript filtering of units based on the chosen course.
* **Trainer Results Portal:** Trainers enter CAT and Exam scores for students enrolled in their assigned unit and cohort. Automatic calculation of total score and letter grades (A, B, C, D, F).

### 📊 Results Verification, Transcripts & Graduation Eligibility

* **Hierarchical Drill-Down:** Admin results verification follows a 4-level drill-down flow: **Cohort $\rightarrow$ Course $\rightarrow$ Student $\rightarrow$ Unit Results**.
* **Publishing Controls:** Toggle visibility of student results (published vs. unpublished) prior to official release.
* **Official Transcripts:** Generate printable academic transcripts displaying unit breakdown, total marks, letter grades, pass count, and mean score.
* **Graduation Management:** Toggle student graduation eligibility, set status (`Eligible`, `Ineligible`, `Pending`), and append administrative clearance notes.

### 📅 Advanced Timetable Management

* **Weekly Board View:** A clean, Kanban-style layout showing classes from Monday to Friday.
* **Atomic Recurrence:** Create weekly schedules for an entire semester in one click with database rollback protection.
* **Smart Conflict Detection:** Automatically prevents double-booking trainers or locations during creation.
* **FullCalendar Integration:** Toggle between a structured table and an interactive monthly calendar.

### 💰 Finance & Admissions Hub

* **Course-Based Enrollment:** Link students to specific courses to tailor their billing and academic experience.
* **Staff-Only Access:** Protected views ensure only authorized personnel manage billing.
* **Billing Overview:** Quick access to update student payments and track outstanding balances.

### 🎨 Responsive Left Sidebar & Role-Based Navigation

* **Left Navigation Sidebar:** Replaced top navigation bar with a dark fixed left sidebar on desktop and a mobile offcanvas menu.
* **Breadcrumb Trails:** Navigation breadcrumbs across all admin modules (Cohorts, Courses, Student Directory, Trainer Assignments, Results Verification).
* **Role-Based Views:** Custom portal links and dashboard action cards tailored for Super Admin/Staff, Trainers, and Students.

---

## 🛠️ Technology Stack

| Layer | Technology |
| --- | --- |
| **Backend** | Django 5.2 (Python 3.12+) |
| **Frontend** | Bootstrap 5, FontAwesome 6, Vanilla JS |
| **Database** | SQLite (Development) / PostgreSQL (Production) |
| **Calendar** | FullCalendar.io v6 |
| **Testing** | Pytest-Django |

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
├── accounts/            # User profiles, cohorts, student directory, and authentication
├── courses/             # Courses, units, and fee synchronization signals
├── results/             # Trainer assignments, CAT/exam score entry, transcripts, and graduation
├── finance/             # Course fees, student accounts, and payment tracking
├── timetable/           # Scheduling logic, conflict checks, and calendar
├── resources/           # Learning materials and file management
├── assignments/         # Quizzes, grading, and coursework submissions
├── templates/           # Base responsive left-sidebar layout and shared components
├── static/              # CSS, JS, and Brand Assets
└── manage.py
```

---

## 👥 User Roles & Privileges

### **Super Admin / Registrar / Administrator**

* Full access to **Courses & Units**, **Cohort Management**, **Finance Hub**, **Student Directory**, **Trainer Assignments**, and **Hierarchical Results Verification**.
* Ability to toggle result publication, edit student scores, view transcripts, and manage graduation clearance.

### **Trainer**

* Access to **Trainer Portal** listing assigned units by cohort.
* Enter and update CAT/Exam scores for students in assigned units.
* Upload learning resources and grade assignments.

### **Student**

* Access to **My Results** portal to view published CAT and Exam grades.
* Download official academic transcripts once published.
* Access learning resources, submit assignments, and filter class timetables.

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

**Version**: lxpv1.0

**Status**: Development - Feature Complete
