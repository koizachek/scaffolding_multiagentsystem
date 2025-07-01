"""
Setup script for the Multi-Agent Scaffolding System.
"""

from setuptools import setup, find_packages  # type: ignore

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="multi-agent-scaffolding",
    version="0.1.0",
    author="CLINE",
    author_email="example@example.com",
    description="A modular, experiment-ready prototype of a multi-agent scaffolding system for higher education research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/multi-agent-scaffolding",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mas=cli:main",
        ],
    },
)
