import asyncio
import logging

from reopenwebnet.config import read_environment_config
from reopenwebnet.gatewayproxy import GatewayProxy

KITCHEN_LIGHT = '13'


async def gatewayproxy_demo():
    def on_state_change(msg):
        print("State change", msg)

    gw = GatewayProxy(read_environment_config(), on_state_change)
    gw.start()
    await example_print_status(gw)


async def example_print_status(gateway):
    print("Printing all light statuses with 3 second intervals")
    print(
        "Try toggling lights and causing network interruptions. Gateway should return to stable state after network "
        "is restored")

    while True:
        print(gateway.states)
        await asyncio.sleep(2)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(gatewayproxy_demo())
