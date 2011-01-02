"""
Utilities for applying a watermark to an image using PIL.

Original Source: http://code.activestate.com/recipes/362879/
"""

import Image, ImageEnhance
import random
import traceback

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
        raise ValueError('invalid watermark parameter: ' + var)
    return var

def reduce_opacity(img, opacity):
    """
    Returns an image with reduced opacity.
    """
    assert opacity >= 0 and opacity <= 1

    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    else:
        img = img.copy()

    alpha = img.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    img.putalpha(alpha)

    return img

def determine_scale(scale, img, mark):
    """
    Scales an image using a specified ratio or 'F'.  If `scale` is 'F', the
    image is scaled to be as big as possible to fit in `img` without falling off
    the edges.  Returns the scaled `mark`.
    """

    if scale:
        try:
            scale = float(scale)
        except (ValueError, TypeError):
            pass

        if type(scale) in (str, unicode) and scale.lower() == 'f':
            # scale, but preserve the aspect ratio
            scale = min(
                        float(img.size[0]) / mark.size[0],
                        float(img.size[1]) / mark.size[1]
                       )
        elif type(scale) not in (float, int):
            raise ValueError('Invalid scale value "%s"!  Valid values are 1) "F" for ratio-preserving scaling and 2) floating-point numbers and integers greater than 0.' % (scale,))

        # determine the new width and height
        w = int(mark.size[0] * float(scale))
        h = int(mark.size[1] * float(scale))

        # apply the new width and height, and return the new `mark`
        return (w, h)
    else:
        return mark.size

def determine_rotation(rotation, mark):
    """
    Determines the number of degrees to rotate the watermark image.
    """

    if (isinstance(rotation, str) or isinstance(rotation, unicode)) \
        and rotation.lower() == 'r':
        rotation = random.randint(0, 359)
    else:
        rotation = _int(rotation)

    return rotation

def determine_position(position, img, mark):
    """
    Options:
        TL: top-left
        TR: top-right
        BR: bottom-right
        BL: bottom-left
        C: centered
        R: random
        X%xY%: relative positioning on both the X and Y axes
        X%xY: relative positioning on the X axis and absolute positioning on the
              Y axis
        XxY%: absolute positioning on the X axis and relative positioning on the
              Y axis
        XxY: absolute positioning on both the X and Y axes
    """

    max_left = max(img.size[0] - mark.size[0], 0)
    max_top = max(img.size[1] - mark.size[1], 0)

    if not position:
        position = 'r'

    if isinstance(position, tuple):
        left, top = position
    elif isinstance(position, str) or isinstance(position, unicode):
        position = position.lower()

        # corner positioning
        if position in ['tl', 'tr', 'br', 'bl']:
            if 't' in position:
                top = 0
            elif 'b' in position:
                top = max_top
            if 'l' in position:
                left = 0
            elif 'r' in position:
                left = max_left

        # center positioning
        elif position == 'c':
            left = int(max_left / 2)
            top = int(max_top / 2)

        # random positioning
        elif position == 'r':
            left = random.randint(0, max_left)
            top = random.randint(0, max_top)

        # relative or absolute positioning
        elif 'x' in position:
            left, top = position.split('x')

            if '%' in left:
                left = max_left * _percent(left)
            else:
                left = _int(left)

            if '%' in top:
                top = max_top * _percent(top)
            else:
                top = _int(top)

    return (left, top)

def watermark(img, mark, position=(0, 0), opacity=1, scale=1.0, tile=False, greyscale=False, rotation=0, return_name=False, **kwargs):
    """
    Adds a watermark to an image.
    """
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)

    if type(scale) != tuple:
        scale = determine_scale(scale, img, mark)

    mark = mark.resize(scale)

    if greyscale and mark.mode != 'LA':
        mark = mark.convert('LA')

    rotation = determine_rotation(rotation, mark)
    if rotation != 0:
        # give some leeway for rotation overlapping
        new_w = mark.size[0] * 1.5
        new_h = mark.size[1] * 1.5

        new_mark = Image.new('RGBA', (new_w, new_h), (0,0,0,0))

        # center the watermark in the newly resized image
        new_l = (new_w - mark.size[0]) / 2
        new_t = (new_h - mark.size[1]) / 2
        new_mark.paste(mark, (new_l, new_t))

        mark = new_mark.rotate(rotation)

    position = determine_position(position, img, mark)

    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # make sure we have a tuple for a position now
    assert isinstance(position, tuple), 'Invalid position "%s"!' % position

    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', img.size, (0,0,0,0))
    if tile:
        first_y = position[1] % mark.size[1] - mark.size[1]
        first_x = position[0] % mark.size[0] - mark.size[0]

        for y in range(first_y, img.size[1], mark.size[1]):
            for x in range(first_x, img.size[0], mark.size[0]):
                layer.paste(mark, (x, y))
    else:
        layer.paste(mark, position)

    # composite the watermark with the layer
    return Image.composite(layer, img, layer)

def test():
    im = Image.open('test.png')
    mark = Image.open('overlay.png')
    watermark(im, mark,
                tile=True,
                opacity=0.5,
                rotation=30).save('test1.png')

    watermark(im, mark,
                scale='F').save('test2.png')

    watermark(im, mark,
                position=(100, 100),
                opacity=0.5,
                greyscale=True,
                rotation=-45).save('test3.png')

    watermark(im, mark,
                position='C',
                tile=False,
                opacity=0.2,
                scale=2,
                rotation=30).save('test4.png')

if __name__ == '__main__':
    test()
