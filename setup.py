from setuptools import setup

setup(
    name="destroybg",
    packages=["src"],
    entry_points={"console_scripts": ["destroybg = src.main:start"]},
    version="0.1.0",
    description="Python command line application bare bones template.",
    long_description="",
    author="Maciej Błędkowski",
    author_email="pub@mble.dk",
    url="",
)
