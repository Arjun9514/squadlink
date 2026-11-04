"""SquadLink Root Entrypoint.

Allows running the Streamlit app directly from the repository root:
    streamlit run app.py
"""

import os
import sys
from pathlib import Path

# Add directories to system path
ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"
NOSQL_DIR = ROOT_DIR / "nosql"

sys.path.extend([str(ROOT_DIR), str(FRONTEND_DIR), str(NOSQL_DIR)])

# Change working directory context to frontend if needed
os.chdir(str(FRONTEND_DIR))

# Execute frontend app
import runpy
runpy.run_path(str(FRONTEND_DIR / "app.py"), run_name="__main__")
