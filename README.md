# About

repository containing utilities for generating random data, for the DW laboratories.

## Getting started

0. Have [poetry](https://python-poetry.org/docs/#installation) installed.
1. Install package with `poetry install`
2. Run `poetry run airbase-gen --help`

   ```bash

   usage: airbase-gen [-h] {csv,sql} ...

   positional arguments:
   {csv,sql}   sub-command help

   optional arguments:
   -h, --help  show this help message and exit
   ```
3. Alternatively you can spawn a shell

## Load to csv

```bash
$poetry run airbase-gen csv --help
usage: airbase-gen csv [-h] [--prob-noisy PROB_NOISY] [--prob-bad PROB_BAD] [-r ROWS] OUT_PATH

positional arguments:
  OUT_PATH              path to output folder

optional arguments:
  -h, --help            show this help message and exit
  --prob-noisy PROB_NOISY
                        A probability that a row is generated with noisy quality of data (default: 0.0)
  --prob-bad PROB_BAD   A probability that a row is generated with bad quality of data (default: 0.0)
  -r ROWS, --rows ROWS  number of rows to create (default: 1000)
```

## Using docker-compose

1. install `docker` and `docker-compose`
2. run `docker-compose up -d` and wait until it finishes
3. You have now access to a _postgres_ database at `0.0.0.0:54320` with `postgres:admin` credentials, and a _pgadmin4_ instance at `0.0.0.0:5050` with `admin@pgadmin.com:pgadmin` credentials. **Note that these two are different credentials for different services.**

## Load to database

```bash
$poetry run airbase-gen sql --help
usage: airbase-gen sql [-h] [--prob-noisy PROB_NOISY] [--prob-bad PROB_BAD] [-r ROWS] [--hard] [-v] [--db-name DB_NAME] [--db-user DB_USER] --db-pwd DB_PWD [--db-host DB_HOST]
                       [--db-port DB_PORT]

optional arguments:
  -h, --help            show this help message and exit
  --prob-noisy PROB_NOISY
                        A probability that a row is generated with noisy quality of data (default: 0.0)
  --prob-bad PROB_BAD   A probability that a row is generated with bad quality of data (default: 0.0)
  -r ROWS, --rows ROWS  number of rows to store (default: 1000)
  --hard                wipe database before insertion (default: False)
  -v, --verbose         sets SQLAlchemy as verbose (default: False)
  --db-name DB_NAME     database name (default: postgres)
  --db-user DB_USER     database user (default: postgres)
  --db-pwd DB_PWD       database password (default: None)
  --db-host DB_HOST     database host (default: 0.0.0.0)
  --db-port DB_PORT     database port. The default is 54320, set by docker-compose (default: 54320)
```

## Writing your own generator

The library uses a `BaseConfig` class with more settings that can be overriden. To write
your own generator, you can look at how this is done within the code

- look at `cli.py`
- look at the tests in `/tests`

The baseline is

1. Instantiate a `config` object from the `BaseConfig` class, with custom parameters
   1. Alternatively, overwrite parameters of the instance afterwards, because Python (yay)
2. Pass this `config` object to the constructor of `AircraftGenerator`, creating a generator `ag` instance
3. Call `ag.populate()` to generate random elements in memory. These are stored in lists as attributes of `ag`
4. Inspect the generated elements, and if you are okay with them, call `ag.to_csv()` or `ag.to_sql()` depending on what you want

In code, this is roughly equivalent to

```python
from acme_data_generation.base.config import BaseConfig
from acme_data_generation.scripts.generate import AircraftGenerator

config = BaseConfig(
   size=rows,
   prob_good=(1 - (prob_noisy + prob_bad)),
   prob_noisy=prob_noisy,
   prob_bad=prob_bad,
   **other_args
)

ag = AircraftGenerator(config)
ag.populate()
ag.to_csv(path=out_path)
```

Make sure to read more about the program in the [rationale](docs/rationale.md)

## Testing

run `pytest tests/`.

### Caveats

1. Some tests require an alive database named `testdb`, at the same postgres address that the one being used by the `airbase-gen sql` command.
2. This database is provided automatically using the docker postgres instance.
3. Some tests are not implemented and others are not passing as of 0.9

## Other goodies

1. `make coverage` to run tests with coverage

   > poor man's badge: test coverage 77%

2. `make memprofile.generate` to produce a memory usage profile

   > poor man's badge: memory consumption: 21.1[MB]@1000[rows].

## Business rules enforcement

Data generated with this program should

- Enforce specific business rules, defined by unique identifiers. Read more about these in [business_rules](docs/business_rules.md)
- Provide a deterministic way to produce random, noisy data that breaks these business rules.

## Rationale

You can read more about how this generator was developed here in this short [document](docs/rationale.md)
