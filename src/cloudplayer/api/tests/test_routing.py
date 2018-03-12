import mock
import pytest
import tornado.web
import tornado.gen

from cloudplayer.api.routing import ProtocolMatches


def test_protocol_matcher_should_ensure_regex_termination():
    matcher = ProtocolMatches('proto')
    assert matcher.protocol_pattern.pattern == 'proto$'


@pytest.mark.gen_test
def test_protocol_matcher_should_route_requests_based_on_protocol():

    @tornado.gen.coroutine
    def app_one(*_):
        return 'ONE'

    @tornado.gen.coroutine
    def app_two(*_):
        return 'TWO'

    @tornado.gen.coroutine
    def catch_all(*_):
        return 'ALL'

    request = mock.Mock()
    routes = [
        (ProtocolMatches('^one[s]?$'), app_one),
        (ProtocolMatches('two'), app_two),
        (ProtocolMatches('.*'), catch_all)]
    base_app = tornado.web.Application(routes)

    @tornado.gen.coroutine
    def assert_route(proto, expected):
        request.protocol = proto
        delegate = base_app.find_handler(request)
        response = yield delegate.request_callback(base_app, request)
        assert response == expected

    assert_route('ones', 'ONE')
    assert_route('one', 'ONE')
    assert_route('two', 'TWO')
    assert_route('three', 'ALL')
