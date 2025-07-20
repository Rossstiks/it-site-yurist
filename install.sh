#!/bin/bash
# Automated installation and launch script for it-site-yurist
set -e

if ! command -v python3 >/dev/null; then
  echo "Python 3 is required but not installed." >&2
  exit 1
fi

# Create virtual environment if not already present
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Initialize the database
python - <<'PY'
from app.models import Base
from app.core.db import engine
Base.metadata.create_all(bind=engine)
PY

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
