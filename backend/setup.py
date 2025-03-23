import os
import subprocess
import sys
from pathlib import Path

def setup_django_project():
    # Create virtual environment
    subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Determine the pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        pip_path = "venv/bin/pip"
    
    # Install requirements
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    
    # Create Django project
    subprocess.run([f"{pip_path} install django"])
    subprocess.run([f"{pip_path} install djangorestframework"])
    
    # Create the project
    subprocess.run(["django-admin", "startproject", "charity_backend", "."])
    
    # Create main apps
    subprocess.run(["python", "manage.py", "startapp", "users"])
    subprocess.run(["python", "manage.py", "startapp", "campaigns"])
    subprocess.run(["python", "manage.py", "startapp", "donations"])
    
    print("Django project setup completed successfully!")

if __name__ == "__main__":
    setup_django_project() 