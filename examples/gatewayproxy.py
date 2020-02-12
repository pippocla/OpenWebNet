import asyncio
from time import sleep

from reopenwebnet.gatewayproxy import GatewayProxy
from reopenwebnet import messages

import logging

KITCHEN_LIGHT = '13'


async def gatewayproxy_demo():
    gw = GatewayProxy()
    await gw.start()
    await example_print_status(gw)


async def example_print_status(gateway):
    print("Printing all light statuses with 3 second intervals")
    print(
        "Try toggling lights and causing network interruptions. Gateway should return to stable state after network "
        "is restored")

    while True:
        gateway.print_states()
        await asyncio.sleep(2)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(gatewayproxy_demo())
