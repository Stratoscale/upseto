import os
from setuptools import setup
import subprocess
from distutils import sysconfig

PKG_INFO = 'PKG-INFO'

site_packages_path = sysconfig.get_python_lib()
data_files = [(site_packages_path, ["conf/upseto.pth"])]
data_files += [
    ('/etc/bash_completion.d', ['conf/bash_completion.d/upseto.sh']),
]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def version():
    if os.path.exists(PKG_INFO):
        with open(PKG_INFO) as package_info:
            for key, value in (line.split(':', 1) for line in package_info):
                if key.startswith('Version'):
                    return value.strip()

    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()


setup(
    name="upseto",
    # version="1.2.2",
    version=version(),
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
        "PyYAML==3.12"
    ],
    data_files=data_files,
    scripts=['sh/upseto'],
)
