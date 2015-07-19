# -*- coding: utf-8 -*-

import watermarker
from setuptools import setup, find_packages

setup(
    name='django-watermark',
    version=watermarker.version(),
    description="Quick and efficient way to apply watermarks to images in Django.",
    long_description=open('README.rst', 'r').read(),
    keywords='django, watermark, image, photo, logo',
    author='Josh VanderLinden',
    author_email='codekoala@gmail.com',
    url='http://bitbucket.org/codekoala/django-watermark/',
    license='BSD',
    package_dir={'watermarker': 'watermarker'},
    include_package_data=True,
    packages=find_packages(),
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
        'Programming Language :: Python :: 3',
        'Topic :: Artistic Software',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics'
    ],
    zip_safe=False
)
