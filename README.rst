This project provides a simple way for you to apply custom watermarks to images
on your Django-powered website.

Features
========

* Opacity: the filter allows you to specify the transparency level for your
  watermark image
* Watermark positioning: you have several options for positioning watermarks on
  your images

    * Absolute: you can specify exact pixel locations for your watermark
    * Relative: you can use percentages to place your watermark
    * Corners: you can position your watermark in the corners of your images
    * Random: you can tell the filter to randomly generate a position for your
      watermark
    * Center: you can place watermarks in the center of the target image

* Scaling: the watermark can be scaled to cover your images or specify a
  scaling factor to use
* Tiling: the watermark can be tiled across your images
* Greyscale: you can convert the watermark to be greyscale before having it
  applied to the target image.
* Rotation: you can rotate your watermark a certain number of degrees or have
  the rotation be random.

Credits
=======

I didn't write any of the code that actually applies the watermark.  I snagged
it from http://code.activestate.com/recipes/362879/ and turned it into a Django
pluggable application.  Props to Shane Hathaway.

Requirements
============

``django-watermark`` requires a modern version of the Django framework.  By
modern I simply mean a version with the ``newforms-admin`` functionality.  If
you're running on Django 1.0 or later, you're good.

``django-watermark`` also relies upon the built-in ``django.contrib.admin`` and
the [http://www.pythonware.com/products/pil/ Python Imaging Library] (PIL).  I
built it using PIL 1.1.6, but it may work with previous versions.

Installation
============

Download ``django-watermark`` using *one* of the following methods:

easy_install/pip
----------------

You can download the package from the `CheeseShop
<http://pypi.python.org/pypi/django-watermark/>`_ or use one of these commands::

    easy_install django-watermark
    pip install -U django-watermark

to download and install ``django-watermark``.

Package Download
----------------

Download the latest ``.tar.gz``, ``.tar.bz2``, or ``.zip`` file from the
downloads section and extract it somewhere you'll remember.  Use ``python
setup.py install`` to install it.

Clone From Version Control
--------------------------

You can get the latest copy of the source from any of these official mirrors::

    hg clone http://bitbucket.org/codekoala/django-watermark
    git clone http://github.com/codekoala/django-watermark.git
    hg clone http://django-watermark.googlecode.com/hg django-watermark

Verifying Installation
----------------------

The easiest way to ensure that you have successfully installed Pendulum is to
execute a command such as::

    python -c "import watermarker; print watermarker.get_version()"

If that displays the version of ``django-watermark`` that you tried to install,
you're good to roll.  If you see something other than that, you probably need
to check your ``PYTHONPATH`` environment variable.

Configuration
=============

First of all, you must add this project to your list of ``INSTALLED_APPS`` in
``settings.py``::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
        'watermarker',
        ...
    )

Run ``manage.py syncdb``.  This creates the tables in your database that are
necessary for operation.

While we're in this section, I might as well mention a settings variable that
you can override: ``WATERMARKING_QUALITY``.  This should be an integer between
0 and 100.  The default is 85.

By default, ``django-watermark`` obscures the original image's file name, as
the original requirements were to make it impossible to download the
watermark-less image.  As of version 0.1.6, you can specify
``WATERMARK_OBSCURE_ORIGINAL = False`` in your ``setings.py`` to make the
original image file name accessible to the user.

``django-watermark`` also lets you configure how random watermark positioning
should work.  By default, a when a watermark is to be positioned randomly, only
one watermarked image will be generated.  If you wish to generate a random
position for an image's watermark on each request, set
``WATERMARK_RANDOM_POSITION_ONCE`` to ``False`` in your ``settings.py``.

Usage
=====

As mentioned above, you have several options when using ``django-watermark``.
The first thing you must do is load the filter for the template in which you
wish to apply watermarks to your images.

::

    {% load watermark %}

From the Django admin, go ahead and populate your database with some watermarks
that you want to apply to your regular images.  Simply specify a name for the
watermark and upload the watermark image itself.  *It's probably not a good
idea to put commas in your watermark names.*  Watermarks should be transparent
PNG files for best results.  I can't make any guarantees that other formats
will work nicely.

The first parameter to the ``watermark`` filter _must_ be the name you
specified for the watermark in the Django admin.  You can then choose from a
few other parameters to customize the application of the watermark.  Here they
are:

* ``position`` - This one is quite customizable.  First, you can plug your
  watermark into one corner of your images by using one of ``BR``, ``BL``,
  ``TR``, and ``TL``.  These represent 'bottom-right', 'bottom-left',
  'top-right', and 'top-left' respectively.

  Alternatively, you can use relative or absolute positioning for the
  watermark.  Relative positioning uses percentages; absolute positioning uses
  exact pixels.  You can mix and match these two modes of positioning, but you
  cannot mix and match relative/absolute with the corner positioning.  When
  using relative/absolute positioning, the value for the ``position`` parameter
  is ``XxY``, where ``X`` is the left value and ``Y`` is the top value.  The
  left and top values must be separated with a lowercase ``x``.

  If you wanted your watermark image to show up in the center of any image you
  want to watermark, you would use a position parameter such as
  ``position=50%x50%`` or even ``position=C``.  If you wanted the watermark to
  show up half-way between the left and right edges of the image and 100 pixels
  from the top, you would use a position parameter such as
  ``position=50%x100``.

  Finally, you may tell the filter to generate a position for your watermark
  dynamically.  To do this, use ``position=R``.
* ``opacity`` - This parameter allows you to specify the transparency of the
  applied watermark.  The value must be an integer between 0 and 100, where 0
  is fully transparent and 100 is fully opaque.  By default, the opacity is set
  at 50%.
* ``tile`` - If you want your watermark to tile across the entire image, you
  simply specify a parameter such as ``tile=1``.
* ``scale`` - If you'd like to have the watermark as big as possible on the
  target image and fully visible, you might want to use ``scale=F``.  If you
  want to specify a particular scaling factor, just use something like
  ``scale=1.43``.
* ``greyscale`` - If you want your watermark to be greyscale, you can specify
  the parameter ``greyscale=1`` and all color saturation will go away.
* ``rotation`` - Set this parameter to any integer between 0 and 359 (really
  any integer should work, but for your own sanity I recommend keeping the
  value between 0 and 359).  If you want the rotation to be random, use
  ``rotation=R`` instead of an integer.
* ``obscure`` - Set this parameter to 0 to make the original image's filename
  visible to the user.  Default is 1 (or True) to obscure the original
  filename.
* ``quality`` - Set this to an integer between 0 and 100 to specify the quality
  of the resulting image.  Default is 85.
* ``random_position_once`` - Set this to 0 or 1 to specify the random
  positioning behavior for the image's watermark.  When set to 0, the watermark
  will be randomly placed on each request.  When set to 1, the watermark will
  be positioned randomly on the first request, and subsequent requests will use
  the produced image.  Default is ``True`` (random positioning only happens on
  first request).

Examples
========

* ``{{ image_url|watermark:"My Watermark,position=br,opacity=35" }}``

  Looks for a watermark named "My Watermark", place it in the bottom-right
  corner of the target image, using a 35% transparency level.

* ``{{ image_url|watermark:"Your Watermark,position=tl,opacity=75" }}``

  Looks for a watermark named "Your Watermark", place it in the top-left corner
  of the target image, using a 75% transparency level.

* ``{{ image_url|watermark:"The Watermark,position=43%x80%,opacity=40" }}``

  Looks for a watermark named "The Watermark", places it at 43% on the x-axis
  and 80% of the y-axis of the target image, at a transparency level of 40%.

* ``{{ image_url|watermark:"The Watermark,position=R,opacity=10,rotation=45" }}``

  Looks for a watermark named "The Watermark", randomly generates a position
  for it, at a transparency level of 10%, rotated 45 degrees.

* ``{{ image_url|watermark:"w00t,opacity=40,tile=1" }}``

  Looks for a watermark called "w00t", tiles it across the entire target image,
  at a transparency level of 40%.
