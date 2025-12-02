import os

# Use a local directory in your home folder
DATA_DIR = os.path.join(os.path.expanduser('~'), '.pgadmin4')
LOG_FILE = os.path.join(os.path.expanduser('~'), '.pgadmin4', 'pgadmin4.log')
SQLITE_PATH = os.path.join(os.path.expanduser('~'), '.pgadmin4', 'pgadmin4.db')
SESSION_DB_PATH = os.path.join(os.path.expanduser('~'), '.pgadmin4', 'sessions')
STORAGE_DIR = os.path.join(os.path.expanduser('~'), '.pgadmin4', 'storage')

# Create the directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SESSION_DB_PATH, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)
