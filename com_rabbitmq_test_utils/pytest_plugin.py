# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name

import asyncio
from typing import AsyncIterator, Final, Iterator

import aiormq
import pytest
from aiohttp.test_utils import unused_port
from yarl import URL

from .utils import (
    RabbitmqConfig,
    rabbitmq_connection_upped,
    rabbitmq_docker_container_upped,
)

pytest_plugins: Final = ("aiohttp.pytest_plugin",)


@pytest.fixture(scope="session")
def com_rabbitmq_config() -> RabbitmqConfig:
    return RabbitmqConfig(
        host="127.0.0.1",
        port=unused_port(),
    )


@pytest.fixture(scope="session")
def com_rabbitmq_url(com_rabbitmq_config: RabbitmqConfig) -> Iterator[URL]:
    with rabbitmq_docker_container_upped(com_rabbitmq_config):
        yield com_rabbitmq_config.get_url()


@pytest.fixture
async def com_rabbitmq_connection(
    com_rabbitmq_url: URL,
    com_rabbitmq_config: RabbitmqConfig,
    loop: asyncio.AbstractEventLoop,
) -> AsyncIterator[aiormq.Connection]:
    assert loop.is_running()

    async with rabbitmq_connection_upped(com_rabbitmq_config) as connection:
        yield connection
