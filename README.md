# About

repository containing utilities for generating random data, for the DW laboratories.

## Getting started

1. install dependencies with `pipenv install`
2. install package with `pipenv install .` or `pipenv run pip install -e .` (for development)
3. `airbase-gen --help`

   ```bash
   usage: airbase-gen [-h] {csv,sql} ...

   positional arguments:
   {csv,sql}   sub-command help

   optional arguments:
   -h, --help  show this help message and exit
   ```

## Load to csv

```bash
$airbase-gen csv --help
usage: airbase-gen csv [-h] [-r ROWS] [-o OUT_PATH]

optional arguments:
  -h, --help            show this help message and exit
  -r ROWS, --rows ROWS  number of rows to create (default: 1000)
  -o OUT_PATH, --out-path OUT_PATH
                        path to output folder (default: /home/diego/Insync/die
                        go.quintana@ciae.uchile.cl/Google Drive - Shared with
                        me/beca-abello/acme-data-generation/out)
```

## Using docker-compose

1. install `docker` and `docker-compose`
2. run `docker-compose up -d` and wait until it finishes
3. You have now access to a _postgres_ database at `0.0.0.0:54320` with `postgres:admin` credentials, and a _pgadmin4_ instance at `0.0.0.0:5050` with `admin@pgadmin.com:pgadmin` credentials. **Note that these two are different credentials for different services.**

## Load to database

```bash
$airbase-gen sql --help
usage: airbase-gen sql [-h] [-r ROWS] [--hard] [-v] [--db-name DB_NAME]
                       [--db-user DB_USER] [--db-pwd DB_PWD]
                       [--db-host DB_HOST] [--db-port DB_PORT]

optional arguments:
  -h, --help            show this help message and exit
  -r ROWS, --rows ROWS  number of rows to store (default: 1000)
  --hard                wipe database before insertion (default: False)
  -v, --verbose         sets SQLAlchemy as verbose (default: False)
  --db-name DB_NAME     database name (default: postgres)
  --db-user DB_USER     database user (default: postgres)
  --db-pwd DB_PWD       database password (default: admin)
  --db-host DB_HOST     database host (default: 0.0.0.0)
  --db-port DB_PORT     database port. The default is 54320, set by docker-
                        compose (default: 54320)
```

## More control over the generation process

The library uses a `BaseConfig` class with more settings that can be overriden.

## Testing

run `pytest tests/`.

### Caveats

1. Some tests require an alive database named `testdb`, at the same postgres address that the one being used by the `airbase-gen sql` command.
2. This database is provided automatically using the docker postgres instance.
3. Some tests are not implemented and others are not passing as of 0.9

## Other goodies

1. `pipenv install --dev`
2. `make coverage` to run tests with coverage

   > poor man's badge: test coverage 77%

3. `make memprofile.generate` to produce a memory usage profile

   > poor man's badge: memory consumption: 21.1[MB]@1000[rows].
