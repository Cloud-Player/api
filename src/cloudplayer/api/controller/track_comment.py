"""
    cloudplayer.api.controller.track_comment
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime

import tornado.gen

from cloudplayer.api.access import Available
from cloudplayer.api.controller import Controller
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.image import Image
from cloudplayer.api.model.track_comment import TrackComment


class SoundcloudTrackCommentController(Controller):

    DATE_FORMAT = '%Y/%m/%d %H:%M:%S %z'

    @tornado.gen.coroutine
    def search(self, ids, kw, fields=Available):
        response = yield self.fetch(
            ids['track_provider_id'],
            '/tracks/{}/comments'.format(ids['track_id']))
        comments = tornado.escape.json_decode(response.body)

        entities = []
        for comment in comments:
            user = comment['user']
            writer = Account(
                id=user['id'],
                provider_id=ids['track_provider_id'],
                title=user['username'],
                image=Image.from_soundcloud(user.get('avatar_url')))
            entity = TrackComment(
                id=comment['id'],
                provider_id=ids['track_provider_id'],
                body=comment['body'],
                timestamp=comment['timestamp'],
                track_id=ids['track_id'],
                track_provider_id=ids['track_provider_id'],
                account=writer,
                created=datetime.datetime.strptime(
                    comment['created_at'], self.DATE_FORMAT))
            entities.append(entity)

        account = self.get_account(entity.provider_id)
        self.policy.grant_read(account, entities, fields)
        return entities
