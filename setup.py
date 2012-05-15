#!/usr/bin/env python

from distutils.core import setup

if __name__ == '__main__':
    setup(
        name="beastcommentparser",
        version="1.0",
        description="extracts comment information from BEAST summary files",
        long_description=open("README.rst").read(),
        author="Jonathan Chang, Michael Alfaro",
        author_email="jonathan.chang@ucla.edu",
        url="https://github.com/jonchang/beastcommentparser/",
        license="http://www.opensource.org/licenses/BSD-3-Clause",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Operating System :: OS Independent",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python",
            "Topic :: Scientific/Engineering :: Bio-Informatics",
        ],
        install_requires=["DendroPy >= 3.9.0"],
        scripts=["bin/bcp.py"],
        packages=["beastcommentparser"]
    )
