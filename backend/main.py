"""PromptLab API Server

Not a working entry point with the pinned uvicorn 0.27.0: ``uvicorn.run``
needs the app as an import string when ``reload=True``, so ``python main.py``
logs an error and exits with code 1. Start the server with
``uvicorn app.api:app --reload`` from ``backend/`` instead (see the README).
"""

import uvicorn
from app.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
