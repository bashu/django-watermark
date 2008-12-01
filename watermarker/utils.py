"""
Utilities for applying a watermark to an image using PIL.

Source: http://code.activestate.com/recipes/362879/
"""
import Image, ImageEnhance

def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1

    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()

    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)

    return im

def watermark(img, mark, position, opacity=1, greyscale=False, rotation=0):
    """Adds a watermark to an image."""
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)

    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    if greyscale and mark.mode != 'LA':
        mark = mark.convert('LA')

    if rotation != 0:
        rotmark = Image.new('RGBA', mark.size, (0,0,0,0))
        rotmark.paste(mark, (0,0))
        mark = rotmark.rotate(rotation)

    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', img.size, (0,0,0,0))
    if position == 'tile':
        for y in range(0, img.size[1], mark.size[1]):
            for x in range(0, img.size[0], mark.size[0]):
                layer.paste(mark, (x, y))
    elif position == 'scale':
        # scale, but preserve the aspect ratio
        ratio = min(
            float(img.size[0]) / mark.size[0], float(img.size[1]) / mark.size[1])
        w = int(mark.size[0] * ratio)
        h = int(mark.size[1] * ratio)
        mark = mark.resize((w, h))
        layer.paste(mark, ((img.size[0] - w) / 2, (img.size[1] - h) / 2))
    else:
        layer.paste(mark, position)

    # composite the watermark with the layer
    return Image.composite(layer, img, layer)

def test():
    im = Image.open('test.png')
    mark = Image.open('overlay.png')
    watermark(im, mark, 'tile', 0.5).show()
    watermark(im, mark, 'scale', 1.0).show()
    watermark(im, mark, (100, 100), 0.5).show()

if __name__ == '__main__':
    test()
