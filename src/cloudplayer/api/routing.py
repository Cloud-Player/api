"""
    cloudplayer.api.routing
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import re

from tornado.routing import Matcher
from tornado.util import basestring_type


class ProtocolMatches(Matcher):
    """Matches requests based on `protocol_pattern` regex."""

    def __init__(self, protocol_pattern):
        if isinstance(protocol_pattern, basestring_type):
            if not protocol_pattern.endswith('$'):
                protocol_pattern += '$'
            self.protocol_pattern = re.compile(protocol_pattern)
        else:
            self.protocol_pattern = protocol_pattern

    def match(self, request):
        if self.protocol_pattern.match(request.protocol):
            return {}
        return None
