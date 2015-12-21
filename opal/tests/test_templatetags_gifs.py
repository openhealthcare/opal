"""
Unittests for templatetags.gifs
"""
from opal.core.test import OpalTestCase

from opal.templatetags import gifs

class LoadingGifTestCase(OpalTestCase):

    def test_in_list(self):
        valid_gifs = [
            'img/svg-loaders/ball-triangle.svg',
            'img/svg-loaders/rings.svg',
            'img/svg-loaders/grid.svg',
            'img/svg-loaders/three-dots.svg',
            'img/svg-loaders/puff.svg',
            'img/svg-loaders/circles.svg']
        gif = gifs.loading_gif()
        self.assertIn(gif['loading_gif'], valid_gifs)
