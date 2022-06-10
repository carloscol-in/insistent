from setuptools import setup
import setuptools

setup(
    name='insistent',
    version='1.0.0',
    description='Insistent is used to easily integrate retry logics into your workflows\' error handling',
    author='Carlos Colin',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where='src')
)
