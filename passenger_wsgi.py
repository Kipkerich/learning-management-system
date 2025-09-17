import sys, os

project_home = '/home/wamahosp/lms'   # REPLACE
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Ensure project package dir is on path
sys.path.insert(0, os.path.join(project_home))

# Use your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')

# Optionally activate virtualenv (passenger usually handles it, but safe)
activate_this = os.path.join('/home/wamahosp/venv/bin/activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
