import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version:
    VERSION = version.read()

setup(
    name="airbase-gen",
    version=VERSION,
    packages=find_packages(),
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
    py_modules=["project"],
)
