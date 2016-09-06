#!/usr/bin/python
from setuptools import find_packages
from distutils.core import setup
import glob

setup(name="MirrorMirror2",
      version="1.0.7",
      packages=["mirror_mirror"],  # find_packages(),
      scripts=[],

      # Project uses reStructuredText, so ensure that the docutils get
      # installed or upgraded on the target machine
      install_requires=['PyGGI>=1.1.2',
                        'google-api-python-client>=1.5.2',
                        'requests>=2.11.1',
                        'webapp2>=2.5.2',
                        'jinja2>=2.8'
                        ],
      include_package_data=True,
      exclude_package_data={'': []},
      # metadata for upload to PyPI
      author="John Rusnak",
      author_email="john.j.rusnak@att.net",
      description="A mirror mirror GUI",
      license="LGPL",
      keywords="mirror mirror_mirror",
      #package_dir={'MirrorMirro2':'.'},
      #package_data={'MirrorMirror2': ['mirror_mirror/resources/css/*.css']},
      url="http://github.com/nak/mirror_mirror",  # project home page, if any
      data_files=[('mirror_mirror/resources/css', glob.glob('mirror_mirror/resources/css/*.css')),
                  ('mirror_mirror/resources/events', glob.glob('mirror_mirror/resources/events/*')),
                  ('mirror_mirror/resources/js', glob.glob('mirror_mirror/resources/js/*.js')),
                  ('mirror_mirror/resources/js/vendor', glob.glob('mirror_mirror/resources/js/vendor/*.js')),
                  ],
       entry_points = { 'console_scripts': ["mirror_mirror = mirror_mirror.main:main"]},
      # dependency_links = []

      # could also include long_description, download_url, classifiers, etc.
      )
