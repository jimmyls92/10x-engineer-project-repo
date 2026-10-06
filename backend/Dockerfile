FROM python:3.12-slim

WORKDIR /app

# Copied before the code so the install layer is reused when only the code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

EXPOSE 8000

# Not `python main.py`: main.py:10 passes the app object with reload=True, which uvicorn 0.27.0 rejects and exits.
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
