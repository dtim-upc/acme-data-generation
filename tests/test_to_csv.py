import pytest
import csv
import typing as T
from acme_data_generation.scripts.generate import AircraftGenerator
from acme_data_generation.base.config import BaseConfig


def test_csv_files_written(tmp_path, gen):

    # prepare existing folder
    d = tmp_path / "acme-out"
    d.mkdir()

    # gen is already populated
    gen.to_csv(path=d)

    # ensure one csv per entity is stored
    assert len(list(d.iterdir())) == gen.total_entities
    entity_names = set(f"{name}.csv" for name in gen.state.keys())

    # assert the csv filenames match the entity names
    assert set(dir.name for dir in d.iterdir()) == entity_names

    # assuming the previous test passed,
    for file in d.iterdir():
        with file.open("rt") as fp:
            csvreader = csv.reader(fp)
            next(csvreader)  # pop header
            row_count = sum(
                1 for _ in csvreader
            )  # row_count =+ 1 if we don't pop the header
            assert row_count == len(gen.state[file.stem])


@pytest.mark.skip("Not implemented yet")
def test_csv_contents(tmp_path, gen):
    # not implemented
    assert False
