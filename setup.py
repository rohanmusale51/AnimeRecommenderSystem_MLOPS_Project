from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="AnimeRecommenderSystem",
    version="0.1",
    author="rohanmusale51",
    packages=find_packages(),
    install_requires = requirements
)