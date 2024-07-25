import asyncio

from ftgo_utils.errors import ErrorCodes
from rabbitmq_rpc import RPCClient, RabbitMQConfig

from data_access import get_logger
from config.broker import BrokerConfig
from config import LayerNames, MessageBusError
from utils.error_handler import handle_error

class RPCBroker:
    _instance: 'RPCBroker' = None

    def __init__(self, rpc_client: RPCClient):
        self._rpc_client = rpc_client

    @classmethod
    async def initialize(cls, loop: asyncio.AbstractEventLoop = None) -> None:
        if cls._instance is not None:
            return

        broker_config = BrokerConfig()
        logger = get_logger(layer_name=LayerNames.MESSAGE_BUS.value)

        try:
            config = RabbitMQConfig(
                host=broker_config.host,
                port=broker_config.port,
                user=broker_config.user,
                password=broker_config.password,    
                vhost=broker_config.vhost,
                ssl=False,
            )
            rpc_client = await RPCClient.create(config=config)
            if loop is not None:
                rpc_client.set_event_loop(loop)

            cls._instance = cls(rpc_client)
        except Exception as e:
            logger.error(f"Failed to create an RPC Client: config={config}, error={e}")
            raise handle_error(e=e, error_code=ErrorCodes.RABBITMQ_CONNECTION_ERROR, layer=LayerNames.MESSAGE_BUS.value)

    @classmethod
    def get_instance(cls) -> 'RPCBroker':
        if cls._instance is None:
            raise Exception("RPCBroker has not been initialized. Call 'initialize' first.")
        return cls._instance

    @classmethod
    def get_client(cls) -> RPCClient:
        if cls._instance is None:
            raise Exception("RPCBroker has not been initialized. Call 'initialize' first.")
        return cls._instance._rpc_client

    @classmethod
    async def close(cls) -> None:
        if cls._instance is not None:
            await cls._instance._rpc_client.close()
            cls._instance = None
