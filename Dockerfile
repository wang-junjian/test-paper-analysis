FROM ubuntu
LABEL maintainer="wang-junjian@qq.com"

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nano \
    libzbar-dev \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /text-paper-analysis/
WORKDIR /text-paper-analysis
RUN pip3 install --no-cache-dir -r requirements.txt

ADD *.py /text-paper-analysis/
ADD test.png /text-paper-analysis/

EXPOSE 5000

ENTRYPOINT ["python3", "main.py"]
