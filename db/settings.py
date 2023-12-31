import os
import dotenv

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Load env variables from file
dotenv_file = BASE_DIR / "secrets/.env"
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

DB_URL = os.getenv("DATABASE_URL")