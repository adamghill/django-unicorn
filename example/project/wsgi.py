import os
import sys

from django.core.wsgi import get_wsgi_application


# Add square directory to sys.path so that 'example' can be imported as a package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.project.settings")

application = get_wsgi_application()
