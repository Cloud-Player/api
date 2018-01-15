"""
    cloudplayer.api.controller.image
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.image import Image
from cloudplayer.api.policy import Open
import cloudplayer.api.controller


class ImageController(cloudplayer.api.controller.Controller):

    __model__ = Image
    __policies__ = [Open]
