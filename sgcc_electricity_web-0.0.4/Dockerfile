FROM python:3.9-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

WORKDIR /app

COPY src .
COPY ./requirements.txt /tmp/requirements.txt

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && apt-get --allow-releaseinfo-change update \
    && apt-get install -y --no-install-recommends jq chromium chromium-driver tzdata\
    && ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*  \
    && apt-get clean

RUN cd /tmp \
    && pip config --global set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip config --global set install.trusted-host pypi.tuna.tsinghua.edu.cn \
    && python3 -m pip install --upgrade pip \
    && PIP_ROOT_USER_ACTION=ignore pip install \
    --disable-pip-version-check \
    --no-cache-dir \
    -r requirements.txt \
    && rm -rf /tmp/* \
    && pip cache purge \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*

CMD ["python", "main.py"]