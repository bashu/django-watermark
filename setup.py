#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import watermarker
import sys, os

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
watermarker_dir = 'watermarker'

for path, dirs, files in os.walk(watermarker_dir):
    # ignore hidden directories and files
    for i, d in enumerate(dirs):
        if d.startswith('.'): del dirs[i]

    if '__init__.py' in files:
        packages.append('.'.join(fullsplit(path)))
    elif files:
        data_files.append((path, [os.path.join(path, f) for f in files]))

setup(
    name='django-watermark',
    version=watermarker.version(),
    url='http://code.google.com/p/django-watermark/',
    author='Josh VanderLinden',
    author_email='codekoala@gmail.com',
    license='BSD',
    packages=packages,
    data_files=data_files,
    description="Quick and efficient way to apply watermarks to images in Django.",
    long_description="""
This project provides a simple way for you to apply custom watermarks to images on your Django-powered website.

Features
--------

  * Opacity: the filter allows you to specify the transparency level for your watermark image
  * Watermark positioning: you have several options for positioning watermarks on your images

    * Absolute: you can specify exact pixel locations for your watermark
    * Relative: you can use percentages to place your watermark
    * Corners: you can position your watermark in the corners of your images
    * Random: you can tell the filter to randomly generate a position for your watermark

  * Scaling: the watermark can be scaled to cover your images
  * Tiling: the watermark can be tiled across your images
  * Greyscale: you can convert the watermark to be greyscale before having it applied to the target image.
  * Rotation: you can rotate your watermark a certain number of degrees or have the rotation be random.
""",
    keywords='django, watermark, image, photo, logo',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Artistic Software',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics'
    ]
)
