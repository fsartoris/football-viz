from setuptools import setup, find_packages

setup(
    name='football-viz',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'adjustText',
        'matplotlib',
        'pandas',
        'sklearn'
    ],
)