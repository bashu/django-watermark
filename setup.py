import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

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
    url='http://github.com/bashu/django-watermark/',
    author='Josh VanderLinden',
    author_email='codekoala@gmail.com',
    maintainer='Basil Shubin',
    maintainer_email='basil.shubin@gmail.com',
    install_requires=[
        'django>=1.4',
        'django-appconf',
        'pillow',
        'six',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Artistic Software',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics'
    ],
    zip_safe=False
)
