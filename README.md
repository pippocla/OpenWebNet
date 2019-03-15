# OpenWebNet

Python client for interaction with OpenWebNet bus.
There's a synchronous client for command sessions and an asynchronous client for event sessions.

## Example usage:

```
from openwebnet import OpenWebNet

client = OpenWebNet('192.168.1.10', 20000, '951753')

client.light_on('11')
```
