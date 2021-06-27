import asyncio
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncIterator, Iterator

import aiormq
import attr
import docker
from yarl import URL


@attr.s(auto_attribs=True, slots=True, frozen=True)
class RabbitmqConfig:
    host: str
    port: int

    def get_url(self) -> URL:
        return URL.build(
            scheme="amqp",
            host=self.host,
            port=self.port,
        )


@contextmanager
def rabbitmq_docker_container_upped(config: RabbitmqConfig) -> Iterator[None]:
    docker_client = docker.from_env()

    container = docker_client.containers.run(
        image="rabbitmq:3-alpine",
        detach=True,
        ports={
            "5672": (config.host, config.port),
        },
    )
    try:
        yield
    finally:
        container.remove(force=True)
        docker_client.close()


@asynccontextmanager
async def rabbitmq_connection_upped(
    config: RabbitmqConfig,
) -> AsyncIterator[aiormq.Connection]:
    connection = await _wait_rabbitmq_setup(config)
    try:
        yield connection
    finally:
        _ = 1
        await connection.close()


async def _wait_rabbitmq_setup(config: RabbitmqConfig) -> aiormq.Connection:
    for _ in range(50):
        try:
            connection = await aiormq.connect(config.get_url())
        except aiormq.connection.AMQPFrameError:
            await asyncio.sleep(0.5)
        else:
            return connection
    raise RuntimeError("Could not connect to the Rabbitmq")
