import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyfrbcatdb",
    version = "0.0.1",
    author = "Ronald van Haren, Oscar Martinez-Rubi",
    author_email = "r.vanharen@esciencecenter.nl",
    description = (""),
    license = "Apache 2.0",
    keywords = "VOEvent, FRBCAT",
    url = "https://github.com/AA-ALERT/frbcatdb",
    packages=['pyfrbcatdb'],
    package_data={'pyfrbcatdb': ['mapping.txt', 'rop_params.txt',
                                 'rmp_params.txt']},
    scripts=['pyfrbcatdb/scripts/decode_VOEvent',
             'pyfrbcatdb/scripts/create_VOEvent'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved ::Apache Software License",
    ],
)
