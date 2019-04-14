# ReOpenWebNet

Python client for interaction with ReOpenWebNet bus.
There's a synchronous client for command sessions and an asynchronous client for event sessions.

This is a fork from https://github.com/pippocla/openwebnet (I felt there were some shortcomings in the original project & I could not easily reach the owner to share my changes)

## Example usage:

### CommandClient

The CommandClient connects to the gateway and establishes a comand session.
The CommandClient works synchronously.

See examples/commandclient.py

### EventClient

The EventClient connects to the gateway and establishes an event session.
The EventClient works asynchronously
