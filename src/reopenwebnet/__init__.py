# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

from reopenwebnet import messages
from reopenwebnet import client_factory
from reopenwebnet import commandclient
from reopenwebnet import eventclient
from reopenwebnet import gatewayproxy

__all__=[messages, client_factory, commandclient, eventclient, gatewayproxy]


try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound
