FROM debian:11

ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=quiz_app

COPY . .

EXPOSE 5500

CMD ["flask", "--app", "quiz_app", "run","--host=0.0.0.0","--port=5500", "--debug"]


# docker build -t imageName .
# docker run -d -p 5500:5500 imageName
# docker run -d -p 5500:5500 -v "$(pwd)/instance:/app/instance" --name containerName imageName