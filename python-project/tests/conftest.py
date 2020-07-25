import pytest

from project.scripts.config import Config


@pytest.fixture()
def config():
    config = Config()
    config.SIZE = 10
    yield config
