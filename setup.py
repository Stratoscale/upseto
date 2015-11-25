import os
import sys
from setuptools import setup


SITE_PACKAGES = [path for path in sys.path if '-packages' in path][-1]
BASH_COMPLETION = os.path.expanduser('~/.bash_completion') if os.getuid() != 0 else '/etc/bash_completion.d'


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
    data_files=[
        (SITE_PACKAGES, ['conf/upseto.pth']),
        (BASH_COMPLETION, ['conf/bash_completion.d/upseto.sh']),
    ],
    scripts=['sh/upseto'],
)
