# -*- coding: utf-8 -*-

import os
import errno
import logging
import traceback
import hashlib

from PIL import Image
from datetime import datetime

try:
    from urllib.parse import unquote
    from urllib.request import url2pathname
except ImportError:
    from urllib import unquote, url2pathname

from django import template
from django.utils.encoding import smart_str
from django.utils.timezone import make_aware, get_default_timezone

from watermarker import utils
from watermarker.conf import settings
from watermarker.models import Watermark

QUALITY = settings.WATERMARK_QUALITY
OBSCURE_ORIGINAL = settings.WATERMARK_OBSCURE_ORIGINAL
RANDOM_POSITION_ONCE = settings.WATERMARK_RANDOM_POSITION_ONCE

register = template.Library()

logger = logging.getLogger('watermarker')


class Watermarker(object):

    def __call__(self, url, name, position=None, opacity=0.5,
                 tile=False, scale=1.0, greyscale=False, rotation=0,
                 obscure=OBSCURE_ORIGINAL, quality=QUALITY, random_position_once=RANDOM_POSITION_ONCE):
        """
        Creates a watermarked copy of an image.

        * ``name``: This is the name of the Watermark object that you wish to
          apply to the image.
        * ``position``:  There are several options.

            * ``R``: random placement, which is the default behavior.
            * ``C``: center the watermark
            * ``XxY`` where ``X`` is either a specific pixel position on the
              x-axis or a percentage of the total width of the target image and
              ``Y`` is a specific pixel position on the y-axis of the image or
              a percentage of the total height of the target image.  These
              values represent the location of the top and left edges of the
              watermark.  If either ``X`` or ``Y`` is a percentage, you must
              use a percent sign.  This is not used if either one of the
              ``tiled`` or ``scale`` parameters are true.

              Examples:

                * ``50%x50%``: positions the watermark at the center of the
                  image.
                * ``50%x100``: positions the watermark at the midpoint of the
                  total width of the image and 100 pixels from the top of the
                  image
                * ``100x50%``: positions the watermark at the midpoint of the
                  total height of the image and 100 pixels from the left edge
                  of the image
                * ``100x100``: positions the top-left corner of the watermark
                  at 100 pixels from the top of the image and 100 pixels from
                  the left edge of the image.

            * ``br``, ``bl``, ``tr``, ``tl`` where ``b`` means "bottom", ``t``
              means "top", ``l`` means "left", and ``r`` means "right".  This
              will position the watermark at the extreme edge of the original
              image with just enough room for the watermark to "fully show".
              This assumes the watermark is not as big as the original image.

        * ``opacity``: an integer from 0 to 100.  This value represents the
          transparency level of the watermark when it is applied.  A value of
          100 means the watermark is completely opaque while a value of 0 means
          the watermark will be invisible.
        * ``tile``: ``True`` or ``False`` to specify whether or not the
          watermark shall be tiled across the entire image.
        * ``scale``: a floating-point number above 0 to specify the scaling for
          the watermark.  If you want the watermark to be scaled to its maximum
          without falling off the edge of the target image, use ``F``.  By
          default, scale is set to ``1.0``, or 1:1 scaling, meaning the
          watermark will be placed on the target image at its original size.
        * ``greyscale``: ``True`` or ``False`` to specify whether or not the
          watermark should be converted to a greyscale image before applying it
          to the target image.  Default is ``False``.
        * ``rotation``: 0 to 359 to specify the number of degrees to rotate the
          watermark before applying it to the target image.  Alternatively, you
          may set ``rotation=R`` for a random rotation value.
        * ``obscure``: set to ``False`` if you wish to expose the original
          image's filename.  Defaults to ``True``.
        * ``quality``: the quality of the resulting watermarked image.  Default
          is 85.

        """
        # look for the specified watermark by name.  If it's not there, go no
        # further
        try:
            watermark = Watermark.objects.get(name=name, is_active=True)
        except Watermark.DoesNotExist:
            logger.error('Watermark "%s" does not exist... Bailing out.' % name)
            return url

        # make sure URL is a string
        url = smart_str(url)

        basedir = '%s/watermarked/' % os.path.dirname(url)
        original_basename, ext = os.path.splitext(os.path.basename(url))

        # open the target image file along with the watermark image
        target = Image.open(self._get_filesystem_path(url))
        mark = Image.open(watermark.image.path)

        # determine the actual value that the parameters provided will render
        random_position = bool(position is None or str(position).lower() == 'r')
        scale = utils.determine_scale(scale, target, mark)
        mark = mark.resize(scale, resample=Image.ANTIALIAS)
        rotation = utils.determine_rotation(rotation, mark)
        pos = utils.determine_position(position, target, mark)

        # see if we need to create only one randomly positioned watermarked
        # image
        if not random_position or (not random_position_once and random_position):
            logger.debug('Generating random position for watermark each time')
            position = pos
        else:
            logger.debug('Random positioning watermark once')

        params = {
            'position':    position,
            'opacity':     opacity,
            'scale':       scale,
            'tile':        tile,
            'greyscale':   greyscale,
            'rotation':    rotation,
            'original_basename':    original_basename,
            'ext':         ext,
            'quality':     quality,
            'watermark':   watermark.id,
            'left':        pos[0],
            'top':         pos[1],
            # 'fstat':       os.stat(self._get_filesystem_path(url)),
        }
        logger.debug('Params: %s' % params)

        fname = self.generate_filename(mark, **params)
        url_path = self.get_url_path(basedir, original_basename, ext, fname, obscure)
        fpath = self._get_filesystem_path(url_path)

        logger.debug('Watermark name: %s; URL: %s; Path: %s' % (
            fname, url_path, fpath,
        ))

        # see if the image already exists on the filesystem. If it does, use it.
        if os.access(fpath, os.R_OK):
            # see if the ``Watermark`` object was modified since the
            # file was created
            modified = make_aware(
                datetime.fromtimestamp(os.path.getmtime(fpath)), get_default_timezone())

            # only return the old file if things appear to be the same
            if modified >= watermark.date_updated:
                logger.info('Watermark exists and has not changed. Bailing out.')
                return url_path

        # make sure the position is in our params for the watermark
        params['position'] = pos

        self.create_watermark(target, mark, fpath, **params)

        # send back the URL to the new, watermarked image
        return url_path

    def _get_filesystem_path(self, url_path, basedir=settings.MEDIA_ROOT):
        """Makes a filesystem path from the specified URL path"""

        if url_path.startswith(settings.MEDIA_URL):
            url_path = url_path[len(settings.MEDIA_URL):]  # strip media root url

        return os.path.normpath(os.path.join(basedir, url2pathname(url_path)))

    def generate_filename(self, mark, **kwargs):
        """Comes up with a good filename for the watermarked image"""

        kwargs = kwargs.copy()

        kwargs['opacity'] = int(kwargs['opacity'] * 100)
        # kwargs['st_mtime'] = kwargs['fstat'].st_mtime
        # kwargs['st_size'] = kwargs['fstat'].st_size
        
        params = [
            '%(original_basename)s',
            'wm',
            'w%(watermark)i',
            'o%(opacity)i',
            'gs%(greyscale)i',
            'r%(rotation)i',
            # 'fm%(st_mtime)i',
            # 'fz%(st_size)i',
            'p%(position)s',
        ]

        scale = kwargs.get('scale', None)
        if scale and scale != mark.size:
            params.append('_s%i' % (float(kwargs['scale'][0]) / mark.size[0] * 100))

        if kwargs.get('tile', None):
            params.append('_tiled')

        # make thumbnail filename
        filename = '%s%s' % ('_'.join(params), kwargs['ext'])

        return filename % kwargs

    def get_url_path(self, basedir, original_basename, ext, name, obscure=True):
        """Determines an appropriate watermark path"""

        try:
            hash = hashlib.sha1(smart_str(name)).hexdigest()
        except TypeError:
            hash = hashlib.sha1(smart_str(name).encode('utf-8')).hexdigest()

        # figure out where the watermark would be saved on the filesystem
        if obscure is True:
            logger.debug('Obscuring original image name: %s => %s' % (name, hash))
            url_path = os.path.join(basedir, hash + ext)
        else:
            logger.debug('Not obscuring original image name.')
            url_path = os.path.join(basedir, hash, original_basename + ext)

        # make sure the destination directory exists
        try:
            fpath = self._get_filesystem_path(url_path)
            os.makedirs(os.path.dirname(fpath))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass  # not to worry, directory exists
            else:
                logger.error('Error creating path: %s' % traceback.format_exc())
                raise
        else:
            logger.debug('Created directory: %s' % os.path.dirname(fpath))

        return url_path

    def create_watermark(self, target, mark, fpath, quality=QUALITY, **kwargs):
        """Create the watermarked image on the filesystem"""

        im = utils.watermark(target, mark, **kwargs)
        im.save(fpath, quality=quality)
        return im


@register.filter
def watermark(url, args=''):
    """
    Returns the URL to a watermarked copy of the image specified.

    """
    # initialize some variables
    args = args.split(',')

    params = dict(
        name=args.pop(0),
        opacity=0.5,
        tile=False,
        scale=1.0,
        greyscale=False,
        rotation=0,
        position=None,
        quality=QUALITY,
        obscure=OBSCURE_ORIGINAL,
        random_position_once=RANDOM_POSITION_ONCE,
    )

    params['url'] = unquote(url)

    # iterate over all parameters to see what we need to do
    for arg in args:
        key, value = arg.split('=')
        key, value = key.strip(), value.strip()
        if key == 'position':
            params['position'] = value
        elif key == 'opacity':
            params['opacity'] = utils._percent(value)
        elif key == 'tile':
            params['tile'] = bool(int(value))
        elif key == 'scale':
            params['scale'] = value
        elif key == 'greyscale':
            params['greyscale'] = bool(int(value))
        elif key == 'rotation':
            params['rotation'] = value
        elif key == 'quality':
            params['quality'] = int(value)
        elif key == 'obscure':
            params['obscure'] = bool(int(value))
        elif key == 'random_position_once':
            params['random_position_once'] = bool(int(value))

    return Watermarker()(**params)

