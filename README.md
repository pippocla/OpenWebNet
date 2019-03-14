# OpenWebNet

Python client for interaction with OpenWebNet bus

## Example usage:

```
from openwebnet import OpenWebNet

client = OpenWebNet('192.168.1.10', 20000, '951753')

client.light_on('11')
```
