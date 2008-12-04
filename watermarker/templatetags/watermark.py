from django import template
from django.conf import settings
from watermarker.models import Watermark
from watermarker import utils
from datetime import datetime
import Image
import urlparse
import os
import random

register = template.Library()

# determine the quality of the image after the watermark is applied
try:
    QUALITY = settings.WATERMARKING_QUALITY
except AttributeError:
    QUALITY = 85

def _get_path_from_url(url, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """
    Makes a filesystem path from the specified URL
    """

    if url.startswith(url_root):
        url = url[len(url_root):] # strip media root url

    return os.path.normpath(os.path.join(root, url))

def watermark(url, args=''):
    """
    A filter to create a watermarked copy of an image.  The parameters are as
    follows::

    - [name]::
        This is the name of the Watermark object that you wish to apply to the
        image.

    - position::
        - XxY where X is either a specific pixel position on the x-axis or a
            percentage of the total width of the image and Y is a specific
            pixel position on the y-axis of the image or a percentage of the
            total height of the image.  If either X or Y is a percentage, you
            must use a percent sign.  This is not used if either one of the
            `tiled` or `scale` parameters are true.

            Examples::
                50%x50% - positions the watermark at the center of the image.
                50%x100 - positions the watermark at the midpoint of the total
                    width of the image and 100 pixels from the top of the image
                100x50% - positions the watermark at the midpoint of the total
                    height of the image and 100 pixels from the left edge of
                    the image
                100x100 - positions the top-left corner of the watermark at 100
                    pixels from the top of the image and 100 pixels from the
                    left edge of the image.
        - br, bl, tr, tl where `b` means 'bottom', `t` means 'top', `l` means
            'left', and `r` means 'right'.  This will position the watermark at
            the extreme edge of the original image with just enough room for
            the watermark to "fully show".  This assumes the watermark is not
            as big as the original image.
        - just R for random placement
        - just C to center the watermark
    - opacity::
        - X where X is an integer from 0 to 100.  This value represents the
            transparency level of the watermark when it is applied.
    - tile::
        - 0 or 1 to specify whether or not the watermark shall be tiled across
            the entire image.
    - scale::
        - a floating-point number above 0 to specify the scaling for the 
            watermark.  If you want the watermark to be scaled to its maximum
            without falling off the edge of the target image, use 'F'.  By 
            default, scale is set to 1.0, or 1:1 scaling.
    - greyscale::
        - 0 or 1 to specify whether or not the watermark should be converted to
            a greyscale image before applying it to the target image.
    - rotation::
        - 0 to 359 to specify the number of degrees to rotate the watermark
            before applying it to the target image.  Alternatively, you may
            set rotation=R for a random rotation value.
    """

    basedir = os.path.dirname(url) + '/'
    base, ext = os.path.splitext(os.path.basename(url))

    # initialize some variables
    args = args.split(',')
    name = args.pop(0)
    top = left = 0
    opacity = 0.5
    tile = False
    scale = 1.0
    greyscale = False
    rotation = 0
    position = None

    # look for the specified watermark by name.  If it's not there, go no further
    try:
        watermark = Watermark.objects.get(name=name, is_active=True)
    except Watermark.DoesNotExist:
        return url

    # iterate over all parameters to see what we need to do
    for arg in args:
        key, value = arg.split('=')
        if key == 'position':
            position = value
        elif key == 'opacity':
            opacity = _percent(value)
        elif key == 'tile':
            tile = bool(int(value))
        elif key == 'scale':
            scale = value
        elif key == 'greyscale':
            greyscale = bool(int(value))
        elif key == 'rotation':
            rotation = value

    # open the target image file along with the watermark image
    target_path = _get_path_from_url(url)
    target = Image.open(target_path)
    mark = Image.open(watermark.image.path)
    
    # determine the actual value that the parameters provided will render
    params = utils.determine_parameter_values(target, mark, position, opacity, scale, tile, greyscale, rotation)
    params.update({
                    'base': base,
                    'watermark': watermark.id,
                    'opacity': params['opacity'] * 100,
                    'left': params['position'][0],
                    'top': params['position'][1],
                    'ext': ext
                   })

    # come up with a good filename for this watermarked image
    wm_name = '%(base)s_wm_w%(watermark)i_o%(opacity)i_gs%(greyscale)i_r%(rotation)i'
    if params['position']:
        wm_name += '_p%(left)sx%(top)s'
    if params['scale'] and params['scale'] != mark.size:
        wm_name += '_s%i' % (float(params['scale'][0]) / mark.size[0] * 100)
    if params['tile']:
        wm_name += '_tiled'
    wm_name += '%(ext)s'

    # make thumbnail filename
    wm_name = wm_name % params

    # figure out where the watermark would be saved on the filesystem
    new_file = urlparse.urljoin(basedir, wm_name)
    new_path = _get_path_from_url(new_file)

    # see if the image already exists on the filesystem.  If it does, use it.
    if os.access(new_path, os.R_OK):
        # see if the Watermark object was modified since the file was created
        modified = datetime.fromtimestamp(os.path.getmtime(new_path))

        # only return the old file if things appear to be the same
        if modified >= watermark.date_updated:
            return new_file

    # create the watermarked image on the filesystem
    wm_image = utils.watermark(target, 
                               mark, 
                               position=position, 
                               opacity=opacity, 
                               scale=scale,
                               tile=tile,
                               greyscale=greyscale, 
                               rotation=rotation)
    wm_image.save(new_path, quality=QUALITY)

    # send back the URL to the new, watermarked image
    return urlparse.urljoin(basedir, wm_name)

register.filter(watermark)
