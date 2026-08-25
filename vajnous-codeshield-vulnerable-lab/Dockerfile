# INTENTIONALLY INSECURE DOCKERFILE - CodeShield lab only
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

# VULNERABILITY: overly permissive file permissions
RUN chmod -R 777 /app

# VULNERABILITY: container runs as root (no USER directive)
ENV FLASK_ENV=development
ENV APP_DEBUG=true
EXPOSE 5000
CMD ["python", "app.py"]
