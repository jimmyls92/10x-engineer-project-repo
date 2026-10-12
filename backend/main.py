"""PromptLab API Server

Run ``python main.py`` from ``backend/`` to start the development server on
port 8000, with auto-reload. It is equivalent to ``uvicorn app.api:app --reload
--host 0.0.0.0``. The Docker image starts uvicorn directly, without reload.
"""

import uvicorn

if __name__ == "__main__":
    # An import string, not the app object: uvicorn reloads only an app it can re-import.
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
