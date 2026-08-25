#!/usr/bin/env python3
"""
CalorieApp Setup Script

Historical metadata for the inactive CalorieApp Testnet prototype.

This file is retained as evidence and is not a supported publication or
installation path. See README.md, LICENSE, and docs/REGULATORY_BOUNDARY.md.
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
    description="Inactive historical CalorieApp XRPL Testnet prototype",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="CalorieApp contributors",
    author_email="info@calorietoken.net",
    url="https://calorietoken.net",
    license="Proprietary - historical grants may apply; see LICENSE",
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
        "Development Status :: 7 - Inactive",
        "Private :: Do Not Upload",
        "Intended Audience :: End Users/Desktop",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Operating System :: Android",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Health :: Nutrition",
    ],
    keywords="blockchain, cryptocurrency, wallet, xrpl, kivy, kivymd, calorie, tracking, testnet, calorietoken",
    project_urls={
        "Homepage": "https://calorietoken.net",
        "Repository": "https://github.com/CalorieToken/CalorieAppTestnet",
        "Bug Reports": "https://github.com/CalorieToken/CalorieAppTestnet/issues",
        "Documentation": "https://github.com/CalorieToken/CalorieAppTestnet/blob/main/docs/README.md",
        "Whitepaper": "https://calorietoken.net/index.php/whitepaper/",
        "Twitter": "https://twitter.com/CalorieToken",
        "Telegram": "https://t.me/+7YxaKdQYWNA0NDA0",
        "Discord": "https://discord.gg/hcjJgdyDGd",
    },
    include_package_data=True,
    package_data={
        "core": ["kv/*.kv"],
        "": ["assets/images/*"],
    },
)
