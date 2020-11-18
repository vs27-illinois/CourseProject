ARG VERSION=latest
FROM coady/pylucene:$VERSION
WORKDIR /usr/src/app
COPY requirements.txt *.py ./dataset ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN rm -f requirements.txt
