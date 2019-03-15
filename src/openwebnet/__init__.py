# -*- coding: utf-8 -*-
from openwebnet import messages
from openwebnet.client import OpenWebNet
from openwebnet.eventclient import EventClient
from pkg_resources import get_distribution, DistributionNotFound

__all__=[OpenWebNet, EventClient, messages]

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound
