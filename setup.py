from setuptools import setup, find_packages

setup(
    name             = "h2kf",
    author           = "Edouard Desparois-Perrault",
    description      = "Formatting tool and additional helper tools for H2K.",
    long_description = open("README.md").read(),
    package_dir      = {
        'h2kf': 'src'
    },
    packages         = ["h2kf"],
    entry_points     = {
        "console_scripts": ['h2kf = h2kf.cli:main']
    },
    version          = "0.0.1"
)