ARG VERSION=latest
FROM coady/pylucene:$VERSION
WORKDIR /usr/src/recipe-finder
COPY RecipeFinder ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN rm -f requirements.txt