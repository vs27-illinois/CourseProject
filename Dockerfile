ARG VERSION=latest
FROM coady/pylucene:$VERSION
WORKDIR /usr/src/recipe-finder
COPY backend ./
COPY frontend/dist/frontend static/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN rm -f requirements.txt
RUN unzip index.zip
RUN rm -f index.zip
RUN mkdir templates
RUN mv static/index.html templates/
ENTRYPOINT python retriever.py
