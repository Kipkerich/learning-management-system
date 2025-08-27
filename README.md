# Learning Management System (LMS)

A comprehensive Django-based Learning Management System designed for educational institutions. This platform enables trainers to create and manage courses, assignments, and resources, while providing students with an intuitive learning experience.

![Django](https://img.shields.io/badge/Django-5.2.5-green.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-teal.svg)

## 🚀 Features

### 👥 User Management
- **Role-based Access Control**: Super Admin, Trainers, and Students
- **Admin-only Registration**: Only super admins can register new users
- **User Profiles**: Editable profiles with Django REST Framework integration
- **Secure Authentication**: Django's built-in auth system with custom enhancements

### 📚 Assignment Module
- **Multiple Question Types**: Multiple choice and text input answers
- **Automated Grading**: Automatic scoring for multiple choice questions
- **Manual Grading**: Trainers can grade text responses with feedback
- **Submission Tracking**: Real-time submission status and due date management
- **Grade Management**: Comprehensive grading system with feedback

### 📅 Timetable Management
- **Recurring Schedules**: Weekly and monthly recurrence patterns
- **Admin CRUD Operations**: Create, read, update, delete schedules
- **Trainer/Student View**: Read-only access for non-admin users
- **Calendar Integration**: FullCalendar integration for visual scheduling
- **Smart Recurrence**: Configurable recurrence intervals and end dates

### 📁 Resource Management
- **File Uploads**: Support for document, video, and link resources
- **Role-based Access**: Trainers can upload/edit, students can view/download
- **Organization**: Categorized resources with search functionality
- **Access Control**: Published/draft status management

### 🎯 User Dashboard
- **Personalized Homepage**: Welcome message with user-specific content
- **Quick Access Cards**: Direct links to timetable, resources, assignments, and CATS
- **Statistics Overview**: Quick stats for students and trainers
- **Responsive Design**: Mobile-friendly interface

## 🛠️ Technology Stack

### Backend
- **Django 5.2.5**: Python web framework
- **Django REST Framework**: API endpoints for profile management
- **PostgreSQL**: Production database (SQLite for development)
- **Pillow**: Image processing for file uploads

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icons and visual elements
- **Vanilla JavaScript**: Custom functionality without jQuery dependency
- **FullCalendar**: Calendar visualization for timetable
- **HTML5/CSS3**: Modern web standards

### Development Tools
- **Virtual Environment**: Python environment isolation
- **Git**: Version control
- **Pip**: Python package management

## 📦 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite for development)
- pip package manager

### Quick Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/kipkerich/lms.git
   cd lms
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv myVenv
   source myVenv/bin/activate  # On Windows: myVenv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**
   - Main App: http://127.0.0.1:8000
   - Admin Panel: http://127.0.0.1:8000/admin

## 📁 Project Structure

```
lms/
├── accounts/                 # Authentication app
│   ├── models.py            # User profile models
│   ├── views.py             # Auth views and profile management
│   ├── forms.py             # User registration and profile forms
│   ├── urls.py              # Authentication routes
│   └── templates/           # Auth templates
│
├── assignments/             # Assignment management app
│   ├── models.py            # Assignment, Question, Submission models
│   ├── views.py             # Assignment creation and grading views
│   ├── forms.py             # Assignment and question forms
│   ├── urls.py              # Assignment routes
│   └── templates/           # Assignment templates
│
├── timetable/               # Timetable management app
│   ├── models.py            # Schedule and recurrence models
│   ├── views.py             # Timetable CRUD operations
│   ├── forms.py             # Schedule forms with recurrence
│   ├── urls.py              # Timetable routes
│   └── templates/           # Timetable templates
│
├── resources/               # Resource management app
│   ├── models.py            # Resource model
│   ├── views.py             # Resource upload and management
│   ├── forms.py             # Resource forms
│   ├── urls.py              # Resource routes
│   └── templates/           # Resource templates
│
├── lms/                     # Project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI configuration
│
├── templates/               # Base templates
│   ├── base.html            # Main template
    ├── cats.html            # CAT template
│   └── dashboard.html       # Dashboard template
│
├── static/                  # Static files
│   ├── css/                 # Global styles
│   ├── js/                  # Global JavaScript
│   └── images/              # Images and assets
│
├── media/                   # Uploaded files (created automatically)
├── requirements.txt         # Python dependencies
└── manage.py               # Django management script
```

## 👥 User Roles

### Super Admin
- Register new users (trainers and students)
- Manage all system content including timetables
- Access Django admin interface
- View system-wide statistics
- CRUD operations on all resources

### Trainer
- Create and manage assignments with questions
- Upload and organize learning resources
- Grade student submissions and provide feedback
- View student progress and performance
- Read-only access to timetable

### Student
- View and submit assignments before due dates
- Access learning resources and download materials
- View grades and instructor feedback
- Update personal profile information
- View class timetable and schedules
- Track learning progress and history

## 📡 API Endpoints Summary

### 🔐 Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout  
- `POST /api/auth/token/refresh/` - Refresh access token

### 👤 User Profiles
- `GET /api/profile/` - Get user profile
- `PUT /api/profile/update/` - Update profile & change password

### 📚 Assignments
- `GET /api/assignments/` - List all assignments
- `GET /api/assignments/{id}/` - Get assignment details
- `POST /api/assignments/{id}/submit/` - Submit assignment (Students)
- `POST /api/assignments/create/` - Create assignment (Trainers)

### 📅 Timetable
- `GET /api/timetable/` - Get schedule data
- `POST /api/timetable/create/` - Create schedule (Admin)
- `GET /api/timetable/json/` - Calendar JSON data

### 📁 Resources
- `GET /api/resources/` - List all resources
- `POST /api/resources/upload/` - Upload resource (Trainers)
- `GET /api/resources/{id}/download/` - Download resource

### 📊 Dashboard
- `GET /api/dashboard/` - Get dashboard overview

## 🎯 Usage Examples

### Creating a Recurring Timetable (Admin)
1. Navigate to Timetable → Add Schedule
2. Select day, time, subject, and trainer
3. Choose recurrence pattern (weekly/monthly)
4. Set start date and end date for recurrence
5. Configure recurrence interval (every X weeks)

### Grading Assignments (Trainer)
1. Go to Assignments → View Submissions
2. Select student submission to grade
3. Provide scores and feedback
4. Submit grades for student viewing

### Submitting Assignments (Student)
1. View available assignments on Dashboard
2. Click "Take Assignment" before due date
3. Answer all questions (multiple choice or text)
4. Submit before deadline

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Database Configuration (Production)
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lms_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in settings
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up static files serving with WhiteNoise or Nginx
- [ ] Configure media file storage (AWS S3 or similar for production)
- [ ] Set up SSL certificate for HTTPS
- [ ] Configure email backend for notifications
- [ ] Set up backup system for database
- [ ] Configure logging for production environment

### Deployment Option
- **PythonAnywhere**: Easy Django hosting solution

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 coding standards
- Write tests for new functionality
- Update documentation for new features
- Use descriptive commit messages
- Test thoroughly before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


### Current Version
- **Version**: 1.0.0
- **Status**: Production Ready
- **Django Version**: 5.2.5
- **Python Version**: 3.8+
- **Database**: PostgreSQL & SQLite

---

**Note**: This is a production-ready version. Always test in staging environment before deploying to production.

