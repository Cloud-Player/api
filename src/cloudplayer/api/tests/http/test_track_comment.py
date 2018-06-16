from unittest import mock
import json

import pytest

from cloudplayer.api.controller import Controller


@pytest.mark.gen_test
async def test_track_comment_http_handler_should_convert_and_output_comments(
        user_fetch, monkeypatch):
    response = [{
        'id': 412581320,
        'created_at': '2018/02/08 11:15:30 +0000',
        'user_id': 1580910,
        'track_id': 28907786,
        'timestamp': 747293,
        'body': 'The moment on 21:07 is the best!',
        'user': {
            'id': 1580910,
            'permalink': 'foo-bar',
            'username': 'foo bar',
            'last_modified': '2015/11/19 07:27:30 +0000',
            'avatar_url': 'https://host.img/02-large.jpg'}
    }, {
        'id': 427684554,
        'created_at': '2018/01/28 14:56:40 +0000',
        'user_id': 1397300,
        'track_id': 28907786,
        'timestamp': 18562,
        'body': 'love this bit!!!!',
        'user': {
            'id': 1397300,
            'permalink': 'user-who-comments',
            'username': 'user-who-comments',
            'last_modified': '2016/11/28 19:22:00 +0000',
            'avatar_url': 'https://host.img/92-large.jpg'}
    }]

    async def fetch(self, *args, **kw):
        return mock.Mock(body=json.dumps(response))

    monkeypatch.setattr(Controller, 'fetch', fetch)

    response = await user_fetch('/track/soundcloud/28907786/comment')
    assert response.json() == [{
        'account': {
            'id': '1580910',
            'image': {
                'large': 'https://host.img/02-t500x500.jpg',
                'medium': 'https://host.img/02-t300x300.jpg',
                'small': 'https://host.img/02-large.jpg'},
            'provider_id': 'soundcloud',
            'title': 'foo bar'},
        'body': 'The moment on 21:07 is the best!',
        'created': '2018-02-08T11:15:30+00:00',
        'id': '412581320',
        'provider_id': 'soundcloud',
        'timestamp': 747293,
        'track_id': '28907786',
        'track_provider_id': 'soundcloud'
        }, {
        'account': {
            'id': '1397300',
            'image': {
                'large': 'https://host.img/92-t500x500.jpg',
                'medium': 'https://host.img/92-t300x300.jpg',
                'small': 'https://host.img/92-large.jpg'},
            'provider_id': 'soundcloud',
            'title': 'user-who-comments'},
        'body': 'love this bit!!!!',
        'created': '2018-01-28T14:56:40+00:00',
        'id': '427684554',
        'provider_id': 'soundcloud',
        'timestamp': 18562,
        'track_id': '28907786',
        'track_provider_id': 'soundcloud'}]
