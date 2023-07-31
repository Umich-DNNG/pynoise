'''The setup file for using PyNoise as a Python package.'''



# Necessary imports.
from setuptools import setup, find_packages



# Global variables set to be easily modified if needed at a later date.
VERSION = '1.0.0' 
DESCRIPTION = 'PyNoise Package'
LONG_DESCRIPTION = 'The goal of this Python suite is to process and analyze radiation data recorded from fission.'



# Set up the package with the following details.
setup(
        name="pyNoise", 
        version=VERSION,
        author="Flynn Darby, Katherine McGraw, Max Tennant, Vincent Weng",
        author_email="<>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['numpy', 'pandas', 'scipy', 'matplotlib'],
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)