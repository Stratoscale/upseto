import os
from setuptools import setup

SITE_PACKAGES = '/usr/lib/python2.7/site-packages'
DIST_PACKAGES = '/usr/lib/python2.7/dist-packages'


data_files = []

# add in case we are running as root
if os.geteuid() == 0:
    data_files += [
        ('/etc/bash_completion.d', ['conf/bash_completion.d/upseto.sh']),
        (SITE_PACKAGES if os.path.exists(SITE_PACKAGES) else DIST_PACKAGES, ['conf/upseto.pth']),
    ]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="upseto",
    version="1.0",
    author="Shlomo Matichin",
    author_email="shlomi@stratoscale.com",
    description=(
        "Split your projects across git repos without the disatvantages"
        " of git submodule"),
    keywords="git repos repositories python scm",
    url="http://packages.python.org/upseto",
    packages=['upseto'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
    ],
    install_requires=[
        "PyYAML==3.11"
    ],
    data_files=data_files,
    scripts=['sh/upseto'],
)
