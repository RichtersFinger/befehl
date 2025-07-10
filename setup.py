import os
from pathlib import Path
from setuptools import setup


try:
    long_description = (Path(__file__).parent / "README.md").read_text(
        encoding="utf8"
    )
except FileNotFoundError:
    long_description = (
        "See docs at https://github.com/RichtersFinger/mini-cli"
    )


setup(
    version=os.environ.get("VERSION", "0.1.0"),
    name="mini-cli",
    description=(
        "a declarative, modular, lightweight, and versatile python library "
        + "for building cli applications"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Steffen Richters-Finger",
    author_email="srichters@uni-muenster.de",
    license="MIT",
    url="https://pypi.org/project/mini-cli/",
    project_urls={"Source": "https://github.com/RichtersFinger/mini-cli"},
    python_requires=">=3.10",
    install_requires=[],
    extras_require={},
    packages=[
        "mini_cli",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
