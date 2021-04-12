import os

if os.getenv("OWM_DB_PWD", None) is None:
    raise Exception("OWM_DB_PWD not set")
DB_URL = f"postgresql://owmuser:{os.getenv('OWM_DB_PWD')}@localhost/owmdb"
DB_TIMEOUT = 5
NODE_DATA_DIR = "/var/opt/ffmapdata/"
if not os.path.isdir(NODE_DATA_DIR):
    NODE_DATA_DIR = "/dev/shm/ffmapdata/"
    os.makedirs(NODE_DATA_DIR, exist_ok=True)
    print("******************** DEVELOPMENT MODE! Using temp dir for storing node data.")
