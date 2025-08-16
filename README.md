# Learning Management System (LMS) - Authentication Module

## Project Overview

This repository contains the authentication system for a Learning Management System (LMS) built with Django. The module provides secure user registration, login, logout, and access control functionality.

## Features

- **User Authentication**
  - Admin-only user registration
  - Secure login/logout functionality
  - Password protection with Django's built-in security
  - Session management

- **User Types**
  - Superuser/admin (can register new users)
  - Regular users (students/instructors)

- **Security Features**
  - CSRF protection
  - Secure password storage
  - POST-required logout
  - Login redirect protection



## Project Structure

```
lms-auth/
├── accounts/                  # Authentication app
│   ├── migrations/            # Database migrations
│   ├── templates/             # HTML templates
│   │   └── accounts/
│   │       ├── login.html     # Login page
│   │       └── register.html  # Registration page
│   ├── admin.py               # Admin configuration
│   ├── apps.py                # App config
│   ├── forms.py               # Authentication forms
│   ├── models.py              # Custom user models
│   ├── urls.py                # App URLs
│   └── views.py               # View functions
├── lms/                       # Project config
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URLs
│   └── wsgi.py                # WSGI config
├── templates/                 # Base templates
│   └── base.html              # Main template
├── .gitignore                 # Git ignore rules
├── manage.py                  # Django CLI
└── requirements.txt           # Dependencies
```



## API Endpoints

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/accounts/login/` | GET | Login page | All |
| `/accounts/login/` | POST | Process login | All |
| `/accounts/logout/` | POST | Process logout | Authenticated |
| `/admin/register/` | GET | Admin registration page | Admin only |
| `/admin/register/` | POST | Process registration | Admin only |



## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Django documentation
- Bootstrap for frontend components
- ALX Django learning resources

---

**Note**: This is a development version. Not recommended for production use without proper security review and testing.