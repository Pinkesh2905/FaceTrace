"""
WSGI config for FaceCognitionPlatform project.
"""

import os
from django.core.wsgi import get_wsgi_application

# LOAD ENVIRONMENT VARIABLES
try:
    from dotenv import load_dotenv
    project_folder = os.path.expanduser('~/FaceCognitionPlatform')  # Adjust as needed
    load_dotenv(os.path.join(project_folder, '.env'))
    load_dotenv() # Load local .env if present
except ImportError:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceCognitionPlatform.settings')

application = get_wsgi_application()