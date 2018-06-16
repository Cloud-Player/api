from unittest import mock
import re

import pytest
import tornado.web

from cloudplayer.api.routing import ProtocolMatches


def test_protocol_matcher_should_ensure_regex_termination():
    matcher = ProtocolMatches('proto')
    assert matcher.protocol_pattern.pattern == 'proto$'


def test_protocol_matcher_should_allow_regex_as_pattern():
    matcher = ProtocolMatches(re.compile('^reg.*ex$'))
    assert matcher.protocol_pattern.pattern == '^reg.*ex$'


@pytest.mark.asyncio
async def test_protocol_matcher_should_route_requests_based_on_protocol():

    async def app_one(*_):
        return 'ONE'

    async def app_two(*_):
        return 'TWO'

    async def catch_all(*_):
        return 'ALL'

    request = mock.Mock()
    routes = [
        (ProtocolMatches('^one[s]?$'), app_one),
        (ProtocolMatches('two'), app_two),
        (ProtocolMatches('.*'), catch_all)]
    base_app = tornado.web.Application(routes)

    async def assert_route(proto, expected):
        request.protocol = proto
        delegate = base_app.find_handler(request)
        response = await delegate.request_callback(base_app, request)
        assert response == expected

    await assert_route('ones', 'ONE')
    await assert_route('one', 'ONE')
    await assert_route('two', 'TWO')
    await assert_route('three', 'ALL')
