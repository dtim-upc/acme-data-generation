import os
from setuptools import find_namespace_packages, setup

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version:
    VERSION = version.read()

setup(
    name="acme-data-generator",
    version=VERSION,
    packages=find_namespace_packages(),
    include_package_data=True,
    license="MIT",
    description="Python application for generating fake airport data",
    author="Diego Quintana",
    author_email="diego.quintana@estudiantat.upc.edu",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
    ],
    py_modules=["acme_data_generation"],
    entry_points='''
        [console_scripts]
        airbase-gen=acme_data_generation.cli:cli
    ''',

)
