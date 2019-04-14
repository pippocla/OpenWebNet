# ReOpenWebNet

Python client for interaction with ReOpenWebNet bus.
There's a synchronous client for command sessions and an asynchronous client for event sessions.

## Example usage:

### CommandClient

The CommandClient connects to the gateway and establishes a comand session.
The CommandClient works synchronously.

See examples/commandclient.py

### EventClient

The EventClient connects to the gateway and establishes an event session.
The EventClient works asynchronously
