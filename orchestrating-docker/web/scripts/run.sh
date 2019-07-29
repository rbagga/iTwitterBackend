#!/usr/bin/env bash
# run from the orchestrating-docker dir

docker-compose down
> ./web/logs/app.log

docker-compose run web /usr/local/bin/python ./create_db.py
docker-compose up --build

date=`date '+%Y-%m-%d_%H-%M-%S'`
mkdir -p ./web/logs
mkdir ./web/logs/$date
docker cp orchestratingdocker_web_1:/code/logs/app.log ./web/logs/$date
docker cp orchestratingdocker_postgres_1:/var/lib/postgresql/data/log/psql.log ./web/logs/$date
docker stop $(docker ps -aq)
