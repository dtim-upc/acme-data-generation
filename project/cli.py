import argparse
import logging
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL

from project.base.config import BaseConfig
from project.scripts.db_utils import create_all, delete_all, get_session
from project.scripts.generate import AircraftGenerator

logging.basicConfig(level=logging.INFO)


# configure argparser
# default path definitions
basepath = Path(__file__).parent
default_output_path = basepath.parent.joinpath("out")


# ---------------------------------------------------------------------------- #
#                               command handling                               #
# ---------------------------------------------------------------------------- #


def to_csv(args):

    config = BaseConfig(size=args.rows)
    ag = AircraftGenerator(config)
    ag.populate()
    ag.to_csv(path=args.out_path)


def to_sql(args):

    config = BaseConfig(size=args.rows)

    _sqla_url = {
        "drivername": "postgres",
        "username": args.db_user,
        "password": args.db_pwd,
        "host": args.db_host,
        "port": args.db_port,
        "database": args.db_name,
    }

    engine = create_engine(URL(**_sqla_url), echo=args.verbose)

    # create session
    if args.hard:
        logging.info("Wiping database")
        delete_all(engine)
        logging.info("Creating tables from scratch")
        create_all(engine)

    #     # select *
    #     result = engine.execute(
    #         """
    # select
    #   *
    # from
    #   pg_catalog.pg_tables
    # where
    #   schemaname != 'information_schema'
    #   and schemaname != 'pg_catalog';"""
    #     )

    #     for _r in result:
    #         print(_r)

    session = get_session(engine)
    ag = AircraftGenerator(config)
    ag.populate()
    ag.to_sql(session)


# ---------------------------------------------------------------------------- #
#                                argparse begin                                #
# ---------------------------------------------------------------------------- #


base_parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=True
)

# ---------------------------------------------------------------------------- #
#                            to csv argument parsing                           #
# ---------------------------------------------------------------------------- #

subparsers = base_parser.add_subparsers(help="sub-command help")


csv_parser = subparsers.add_parser(
    "csv", formatter_class=argparse.ArgumentDefaultsHelpFormatter
)


csv_parser.add_argument(
    "-r", "--rows", help="number of rows to create", default=1000, type=int,
)
csv_parser.add_argument(
    "-o",
    "--out-path",
    help="path to output folder",
    default=default_output_path,
    type=Path,
)
csv_parser.set_defaults(func=to_csv)

# ---------------------------------------------------------------------------- #
#                            to sql argument parsing                           #
# ---------------------------------------------------------------------------- #

sql_parser = subparsers.add_parser(
    "sql", formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

sql_parser.add_argument(
    "-r", "--rows", help="number of rows to store", default=1000, type=int,
)

sql_parser.add_argument(
    "--hard", help="wipe database before insertion", action="store_true"
)
sql_parser.add_argument(
    "-v", "--verbose", help="sets SQLAlchemy as verbose", action="store_true"
)

sql_parser.add_argument(
    "--db-name", help="database name", default="postgres", type=str,
)
sql_parser.add_argument(
    "--db-user", help="database user", default="postgres", type=str,
)
sql_parser.add_argument(
    "--db-pwd", help="database password", default="admin", type=str,
)
sql_parser.add_argument("--db-host", help="database host", default="0.0.0.0", type=str)
sql_parser.add_argument(
    "--db-port",
    help="database port. The default is 54320, set by docker-compose",
    default=54320,
    type=int,
)

sql_parser.set_defaults(func=to_sql)


def cli():
    args = base_parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        base_parser.print_help()


if __name__ == "__main__":
    cli()
