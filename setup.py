from setuptools import setup

setup(
    name='rfs-parts-db',
    version='2.0.4',
    description='Python-based queue for Rexroth ctrlX AUTOMATION platform ',
    author='bostroemc',
    install_requires = ['ctrlx-datalayer', 'ctrlx_fbs', 'jsonschema', 'names'],    
    packages=['app'],
    scripts=['main.py'],
    license='Copyright (c) 2020-2022 Bosch Rexroth AG, Licensed under MIT License'
)
