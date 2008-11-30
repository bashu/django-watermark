from django import template
from django.conf import settings
from watermarker.models import Watermark
from watermarker import utils
import Image
import urlparse
import os

register = template.Library()

# determine the quality of the image after the watermark is applied
try:
    QUALITY = settings.WATERMARKING_QUALITY
except AttributeError:
    QUALITY = 85

def _percent(var):
    """
    Just a simple interface to the _val function with a more meaningful name.
    """
    return _val(var, True)

def _int(var):
    """
    Just a simple interface to the _val function with a more meaningful name.
    """
    return _val(var)

def _val(var, is_percent=False):
    """
    Tries to determine the appropriate value of a particular variable that is
    passed in.  If the value is supposed to be a percentage, a whole integer
    will be sought after and then turned into a floating point number between
    0 and 1.  If the value is supposed to be an integer, the variable is cast
    into an integer.
    """
    try:
        if is_percent:
            var = float(int(var.strip('%')) / 100.0)
        else:
            var = int(var)
    except ValueError:
        raise template.TemplateSyntaxError('invalid watermark parameter: ' + var)
    return var

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
                50%x50% - positions the top-left corner of the watermark at the
                    center of the image.
                50%x100 - positions the top-left corner of the watermark at the
                    midpoint of the total width of the image and 100 pixels from
                    the top of the image
                100x50% - positions the top-left corner of the watermark at the
                    midpoint of the total height of the image and 100 pixels
                    from the left edge of the image
                100x100 - positions the top-left corner of the watermark at 100
                    pixels from the top of the image and 100 pixels from the
                    left edge of the image.
        - br, bl, tr, tl where `b` means 'bottom', `t` means 'top', `l` means
            'left', and `r` means 'right'.  This will position the watermark at
            the extreme edge of the original image with just enough room for
            the watermark to "fully show".  This assumes the watermark is not
            as big as the original image.
    - opacity::
        - X where X is an integer from 0 to 100.  This value represents the
            transparency level of the watermark when it is applied.
    - tile::
        - 0 or 1 to specify whether or not the watermark shall be tiled across
            the entire image.  Takes precedence over the `position` parameter
            but not the `scale` parameter.
    - scale::
        - 0 or 1 to specify whether or not to scale the watermark to cover the
            whole image.  Takes precedence over both the `position` and `tile`
            parameters.

    A full example for using this filter follows::

        {{ image|watermark:"My Watermark,position=100x100,opacity=35,tile=0,scale=0" }}
    """

    basedir = os.path.dirname(url) + '/'
    base, ext = os.path.splitext(os.path.basename(url))

    args = args.split(',')
    name = args.pop(0)
    top = left = 0
    opacity = 0.5
    tile = False
    scale = False
    mode = None
    b_edge = t_edge = l_edge = r_edge = False

    # look for the specified watermark by name.  If it's not there, go no further
    try:
        watermark = Watermark.objects.get(name=name
                                          is_active=True)
    except:
        return url

    # iterate over all parameters to see what we need to do
    for arg in args:
        key, value = arg.split('=')
        if key == 'position':
            # try to figure out what kind of positioning they want
            pos = value.split('x')

            if len(pos) != 1:
                # relative and absolute positioning
                o_left, o_top = pos

                if '%' in o_left:
                    left = _percent(o_left)
                else:
                    left = _int(o_left)

                if '%' in o_top:
                    top = _percent(o_top)
                else:
                    top = _int(o_top)
            else:
                # corner positioning--only take the first two characters
                pos = pos[0][:2]

                b_edge = 'b' in pos
                t_edge = 't' in pos
                l_edge = 'l' in pos
                r_edge = 'r' in pos
        elif key == 'opacity':
            opacity = _percent(value)
        elif key == 'tile':
            tile = bool(int(value))
        elif key == 'scale':
            scale = bool(int(value))

    # come up with a good filename for this watermarked image
    wm_name = '%(base)s_wm_w%(watermark)i_o%(opacity)i'
    if scale:
        wm_name += '_scaled'
        mode = 'scale'
    elif tile:
        wm_name += '_tiled'
        mode = 'tile'
    else:
        if b_edge or t_edge or l_edge or r_edge:
            wm_name += '_p%s' % pos
        else:
            wm_name += '_p%(left)sx%(top)s'
    wm_name += '%(ext)s'

    # make thumbnail filename
    wm_name = wm_name % {'base': base,
                         'watermark': watermark.id,
                         'opacity': opacity * 100,
                         'left': left,
                         'top': top,
                         'ext': ext
                        }

    new_file = urlparse.urljoin(basedir, wm_name)
    old_path = _get_path_from_url(url)
    new_path = _get_path_from_url(new_file)

    # see if the image already exists on the filesystem.  If it does, use it.
    if os.access(new_path, os.R_OK):
        return new_file

    # open the original image file
    orig = Image.open(old_path)
    mark = Image.open(watermark.image.path)

    # determine the actual position based on the size of the image
    if not mode:
        if b_edge or t_edge or l_edge or r_edge:
            # corner positioning
            if t_edge:
                top = 0
            elif b_edge:
                top = orig.size[1] - mark.size[1]
            if l_edge:
                left = 0
            elif r_edge:
                left = orig.size[0] - mark.size[0]

            if top < 0: top = 0
            if left < 0: left = 0
        else:
            # relative/absolute positioning
            if '%' in o_left:
                left = int(orig.size[0] * left)

            if '%' in o_top:
                top = int(orig.size[1] * top)

        mode = (left, top)

    # create the watermarked image on the filesystem
    wm_image = utils.watermark(orig, mark, mode, opacity)
    wm_image.save(new_path, quality=QUALITY)

    # send back the URL to the new, watermarked image
    return urlparse.urljoin(basedir, wm_name)

register.filter(watermark)