import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

from watermarker import __version__

setup(
    name='django-watermark',
    version=__version__,
    packages=find_packages(exclude=['example']),
    include_package_data=True,
    license='BSD License',
    description="Quick and efficient way to apply watermarks to images in Django.",
    long_description=README,
    keywords='django, watermark, image, photo, logo',
    url='http://github.com/codekoala/django-watermark/',
    author='Josh VanderLinden',
    author_email='codekoala@gmail.com',
    maintainer='Basil Shubin',
    maintainer_email='basil.shubin@gmail.com',
    classifiers=[
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
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics'
    ],
    zip_safe=False
)
