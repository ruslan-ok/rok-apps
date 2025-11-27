import json
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR/'rok/secrets.json') as secrets_file:
    secrets = json.load(secrets_file)

def get_secret(setting, secrets=secrets):
    """Get secret setting or fail with ImproperlyConfigured.

    For DATABASE_POSTGRES, if environment variables are set (e.g., in devcontainer),
    they will be used to override the JSON configuration.
    """
    try:
        value = secrets[setting]

        # Override database configuration if environment variables are set
        # if setting == 'DATABASE_POSTGRES' and isinstance(value, dict):
        #     # Check if we're in a containerized environment
        #     db_config = value.copy()
        #     if os.environ.get('PGHOST'):
        #         db_config['HOST'] = os.environ.get('PGHOST')
        #     if os.environ.get('PGPORT'):
        #         db_config['PORT'] = int(os.environ.get('PGPORT'))
        #     if os.environ.get('PGUSER'):
        #         db_config['USER'] = os.environ.get('PGUSER')
        #     if os.environ.get('PGPASSWORD'):
        #         db_config['PASSWORD'] = os.environ.get('PGPASSWORD')
        #     if os.environ.get('PGDATABASE'):
        #         db_config['NAME'] = os.environ.get('PGDATABASE')
        #     return db_config

        return value
    except KeyError:
        raise ImproperlyConfigured("Set the {} setting".format(setting))
