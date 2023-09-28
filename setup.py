#!/usr/bin/env python3

from distutils.core import setup

setup(name='AudioPhil',
      version='0.4.2',
      description='AudioPhil Media Player',
      author='Lorenz Quack',
      author_email='don@amberfisharts.com',
      url='http://www.sourceforge.net/projects/audiophil/',
#      requires=['PyQt4'],
      packages=['audiophil'],
      package_dir={'': 'src'},
      scripts=['scripts/audiophil'],
      data_files=[('share/applications/', ['misc/audiophil.desktop']),
                  ('share/icons/hicolor/scalable/apps/', ['resources/audiophil.svg'])],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: X11 Applications :: Qt',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3',
                   'Topic :: Multimedia :: Sound/Audio :: Players']
     )

