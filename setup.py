# -*- coding: utf-8 -*-
from setuptools import setup

install_requires = open('requirements.txt').read().split('\n')

setup(
    name='oton_converter',
    version='1.1.0',
    description='A CLI tool for converting OCR-D workflows to Nextflow workflow scripts',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Mehmed Mustafa',
    author_email='mehmed.mustafa@gwdg.de',
    url='https://github.com/MehmedGIT/OtoN_Converter',
    license='Apache License 2.0',
    packages=['oton'],
    package_data={'': ['workflow*.txt', 'nextflow*.nf', 'config.toml']},
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'oton=oton.cli:cli',
        ]
    },
)
