FROM python:3.11-slim

WORKDIR /app

COPY . .

# Never bake the API key into the image
RUN rm -f config.py

EXPOSE 8765

CMD ["python3", "server.py"]
