FROM python:3.8

RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' > /etc/timezone

RUN apt-get update && \
    apt-get install -y cmake libgl1 && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app

ADD ts-avatar-service/ /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:17001", "app:app"]

EXPOSE 17001