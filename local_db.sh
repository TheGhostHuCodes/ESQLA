docker pull postgres:11
docker run --name ESQLA-postgres --env POSTGRES_PASSWORD=postgres --detach --publish 5432:5432 postgres:11
