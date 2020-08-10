import pytest
import typing as T
from project.scripts.generate import AircraftGenerator
from project.base.config import BaseConfig


def test_db_is_accessible(session, gen):

    assert gen.config.db_url
    # gen is already populated
    gen.to_sql(db_url = gen.config.db_url)
    
    # assert that at least some elements are in the tables
    count_query = 'SELECT COUNT(*) FROM "%s".%s' # "schema".table
    count_aims_flights = count_query % ("AIMS", "flights")


#     result = sess(
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


 
