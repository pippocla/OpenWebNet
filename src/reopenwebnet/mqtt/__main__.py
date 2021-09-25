import asyncio

from reopenwebnet.config import read_environment_config
from reopenwebnet.mqtt import MqttBridge

async def main():
    bridge = MqttBridge(read_environment_config())
    print("starting bridge")
    await bridge.start()
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
