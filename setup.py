from setuptools import find_packages
from setuptools import setup


def get_version(name):
    import os
    version = None
    script_dir = os.path.dirname(os.path.realpath(__file__))
    script_dir = os.path.join(script_dir, name)
    if not os.path.exists(os.path.join(script_dir, 'VERSION')):
        version = '0.0.1.dev0'
    else:
        with open(os.path.join(script_dir, 'VERSION'), 'r') as version_file:
            version = version_file.read().rstrip()
    return version


title = "nixnetconfig"
description = "NI-XNET Command Line Utility"
version = get_version(title)

setup(
    name=title,
    version=version,
    description=description,
    author="National Instruments",
    maintainer="Tyler Krehbiel",
    maintainer_email="tyler.krehbiel@ni.com",
    include_package_data=False,
    install_requires=[
        'nisyscfg2',
        'nisyscfg2-xnet',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'nixnetconfig=nixnetconfig.__main__:main'
        ]
    },
)
