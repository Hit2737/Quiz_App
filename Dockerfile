FROM python:3.8-alpine3.19

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=quiz_app
COPY . .
EXPOSE 5500
CMD ["flask", "--app", "quiz_app", "run","--host=0.0.0.0","--port=5500", "--debug"]