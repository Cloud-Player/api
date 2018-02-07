"""
    cloudplayer.api.routing
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import re

from tornado.routing import Matcher
from tornado.util import basestring_type


class ProtocolMatches(Matcher):

    def __init__(self, protocol):
        if isinstance(protocol, basestring_type):
            if not protocol.endswith('$'):
                protocol += '$'
            self.protocol = re.compile(protocol)
        else:
            self.protocol = protocol

    def match(self, request):
        if self.protocol.match(request.protocol):
            return {}
        return None
