# Essential SQLAlchemy, 2nd Edition

My workspace containing code listings from the book ["Essential SQLAlchemy,
2nd Edition"](http://shop.oreilly.com/product/0636920035800.do), by Rick
Copeland and Jason Myers.

This workspace uses `pyenv` to manage Python interpreter versions, `pipenv`
to manage dependencies, and `docker-compose` to setup a local postgres
instance to execute code against.

To start up a local postgres instance, execute:

```console
$ docker-compose up
```

While the database container is up, you can execute `psql` commands against
it by using `docker exec`. The following example lists all available
databases within the postgres container instance.

```console
$ docker exec -it esqla_postgres psql esqla_db -U esqla -c "\l"
```

To shut down the local postgres instance, execute:

```console
$ docker-compose down
```