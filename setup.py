from setuptools import setup
from src.h2kf.constants import __version__

setup(
    name             = "h2kf",
    author           = "Edouard Desparois-Perrault",
    description      = "Formatting tool and additional helper tools for H2K.",
    long_description = open("README.md").read(),
    package_dir      = {
        '': 'src'
    },
    packages         = ["h2kf"],
    install_requires = ["wand==0.6.9"],
    entry_points     = {
        "console_scripts": ['h2kf = h2kf.cli:main']
    },
    version          = __version__
)