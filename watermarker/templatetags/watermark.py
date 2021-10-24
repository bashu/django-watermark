# -*- coding: utf-8 -*-

import errno
import hashlib
import logging
import os
import traceback
from datetime import datetime

from PIL import Image

from urllib.parse import unquote
from urllib.request import url2pathname

from django import template
from django.utils.encoding import smart_str
from django.utils.timezone import get_default_timezone, is_aware, make_aware

from watermarker import utils
from watermarker.conf import settings
from watermarker.models import Watermark

QUALITY = settings.WATERMARK_QUALITY
OBSCURE_ORIGINAL = settings.WATERMARK_OBSCURE_ORIGINAL
RANDOM_POSITION_ONCE = settings.WATERMARK_RANDOM_POSITION_ONCE

register = template.Library()

logger = logging.getLogger("watermarker")


class Watermarker(object):
    def __call__(
        self,
        url,
        name,
        position=None,
        opacity=0.5,
        tile=False,
        scale=1.0,
        greyscale=False,
        rotation=0,
        noalpha=True,
        quality=QUALITY,
        obscure=OBSCURE_ORIGINAL,
        random_position_once=RANDOM_POSITION_ONCE,
    ):
        """
        Creates a watermarked copy of an image.
        """
        # look for the specified watermark by name.  If it's not there, go no
        # further
        try:
            watermark = Watermark.objects.get(name__exact=name, is_active=True)
        except Watermark.DoesNotExist:
            logger.error('Watermark "%s" does not exist... Bailing out.' % name)
            return url

        # make sure URL is a string
        url = smart_str(url)

        basedir = "%s/watermarked/" % os.path.dirname(url)
        original_basename, ext = os.path.splitext(os.path.basename(url))

        # open the target image file along with the watermark image
        target = Image.open(self._get_filesystem_path(url))
        mark = Image.open(watermark.image.path)

        # determine the actual value that the parameters provided will render
        random_position = bool(position is None or str(position).lower() == "r")
        scale = utils.determine_scale(scale, target, mark)
        mark = mark.resize(scale, resample=Image.ANTIALIAS)
        rotation = utils.determine_rotation(rotation, mark)
        pos = utils.determine_position(position, target, mark)

        # see if we need to create only one randomly positioned watermarked
        # image
        if not random_position or (not random_position_once and random_position):
            logger.debug("Generating random position for watermark each time")
            position = pos
        else:
            logger.debug("Random positioning watermark once")

        params = {
            "position": position,
            "opacity": opacity,
            "scale": scale,
            "tile": tile,
            "greyscale": greyscale,
            "rotation": rotation,
            "original_basename": original_basename,
            "ext": ext,
            "noalpha": noalpha,
            "quality": quality,
            "watermark": watermark.id,
            "left": pos[0],
            "top": pos[1],
            "fstat": os.stat(self._get_filesystem_path(url)),
        }
        logger.debug("Params: %s" % params)

        fname = self.generate_filename(mark, **params)
        url_path = self.get_url_path(basedir, original_basename, ext, fname, obscure)
        fpath = self._get_filesystem_path(url_path)

        logger.debug(
            "Watermark name: %s; URL: %s; Path: %s"
            % (
                fname,
                url_path,
                fpath,
            )
        )

        # see if the image already exists on the filesystem. If it does, use it.
        if os.access(fpath, os.R_OK):
            # see if the ``Watermark`` object was modified since the
            # file was created
            modified = make_aware(datetime.fromtimestamp(os.path.getmtime(fpath)), get_default_timezone())
            date_updated = watermark.date_updated
            if not is_aware(date_updated):
                date_updated = make_aware(date_updated, get_default_timezone())
            # only return the old file if things appear to be the same
            if modified >= date_updated:
                logger.info("Watermark exists and has not changed. Bailing out.")
                return url_path

        # make sure the position is in our params for the watermark
        params["position"] = pos

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

        kwargs["opacity"] = int(kwargs["opacity"] * 100)
        kwargs["st_mtime"] = kwargs["fstat"].st_mtime
        kwargs["st_size"] = kwargs["fstat"].st_size

        params = [
            "%(original_basename)s",
            "wm",
            "w%(watermark)i",
            "o%(opacity)i",
            "gs%(greyscale)i",
            "r%(rotation)i",
            "fm%(st_mtime)i",
            "fz%(st_size)i",
            "p%(position)s",
        ]

        scale = kwargs.get("scale", None)
        if scale and scale != mark.size:
            params.append("_s%i" % (float(kwargs["scale"][0]) / mark.size[0] * 100))

        if kwargs.get("tile", None):
            params.append("_tiled")

        # make thumbnail filename
        filename = "%s%s" % ("_".join(params), kwargs["ext"])

        return filename % kwargs

    def get_url_path(self, basedir, original_basename, ext, name, obscure=True):
        """Determines an appropriate watermark path"""

        try:
            hash = hashlib.sha1(smart_str(name)).hexdigest()
        except TypeError:
            hash = hashlib.sha1(smart_str(name).encode("utf-8")).hexdigest()

        # figure out where the watermark would be saved on the filesystem
        if obscure is True:
            logger.debug("Obscuring original image name: %s => %s" % (name, hash))
            url_path = os.path.join(basedir, hash + ext)
        else:
            logger.debug("Not obscuring original image name.")
            url_path = os.path.join(basedir, hash, original_basename + ext)

        # make sure the destination directory exists
        try:
            fpath = self._get_filesystem_path(url_path)
            os.makedirs(os.path.dirname(fpath))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass  # not to worry, directory exists
            else:
                logger.error("Error creating path: %s" % traceback.format_exc())
                raise
        else:
            logger.debug("Created directory: %s" % os.path.dirname(fpath))

        return url_path

    def create_watermark(self, target, mark, fpath, quality=QUALITY, **kwargs):
        """Create the watermarked image on the filesystem"""

        im = utils.watermark(target, mark, **kwargs)
        if not kwargs.get("noalpha", True) is False:
            im = im.convert("RGB")
        im.save(fpath, quality=quality)
        return im


@register.filter
def watermark(url, args=""):
    """
    Returns the URL to a watermarked copy of the image specified.

    """
    # initialize some variables
    args = args.split(",")

    params = dict(
        name=args.pop(0),
        opacity=0.5,
        tile=False,
        scale=1.0,
        greyscale=False,
        rotation=0,
        position=None,
        noalpha=True,
        quality=QUALITY,
        obscure=OBSCURE_ORIGINAL,
        random_position_once=RANDOM_POSITION_ONCE,
    )

    params["url"] = unquote(url)

    # iterate over all parameters to see what we need to do
    for arg in args:
        key, value = arg.split("=")
        key, value = key.strip(), value.strip()
        if key == "position":
            params["position"] = value
        elif key == "opacity":
            params["opacity"] = utils._percent(value)
        elif key == "tile":
            params["tile"] = bool(int(value))
        elif key == "scale":
            params["scale"] = value
        elif key == "greyscale":
            params["greyscale"] = bool(int(value))
        elif key == "rotation":
            params["rotation"] = value
        elif key == "noalpha":
            params["noalpha"] = bool(int(value))
        elif key == "quality":
            params["quality"] = int(value)
        elif key == "obscure":
            params["obscure"] = bool(int(value))
        elif key == "random_position_once":
            params["random_position_once"] = bool(int(value))

    return Watermarker()(**params)
