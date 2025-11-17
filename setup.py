#!/usr/bin/env python3
"""
CalorieApp Setup Script

Setup script for the CalorieApp application.
This provides installation and development tools.
"""

from setuptools import setup, find_packages
import os

# Read README.md for long description
def read_readme():
    readme_path = "README.md"
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "CalorieApp - A blockchain-based calorie tracking application"

# Read requirements from requirements.txt
def read_requirements():
    req_path = "requirements.txt"
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="calorieapp",
    version="1.1.0",
    description="A mobile-first cryptocurrency wallet and food tracking application",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="CalorieToken",
    author_email="info@calorietoken.net",
    url="https://github.com/CalorieToken/CalorieAppTestnet",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.12",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "calorieapp=core.app:CalorieAppTestnet.run",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Operating System :: Android",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Cryptocurrency",
        "Topic :: Health :: Nutrition",
    ],
    keywords="blockchain, cryptocurrency, wallet, xrpl, kivy, kivymd, calorie, tracking, testnet",
    project_urls={
        "Bug Reports": "https://github.com/CalorieToken/CalorieAppTestnet/issues",
        "Source": "https://github.com/CalorieToken/CalorieAppTestnet",
        "Documentation": "https://github.com/CalorieToken/CalorieAppTestnet/blob/main/docs/README.md",
    },
    include_package_data=True,
    package_data={
        "core": ["kv/*.kv"],
        "": ["assets/images/*"],
    },
)