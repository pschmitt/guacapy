from setuptools import find_packages, setup


setup(
    name="guacapy",
    version="0.9.6.post1",
    license="GPL3",
    description="REST API client for Guacamole",
    author="Philipp Schmitt",
    author_email="philipp@schmitt.co",
    url="https://github.com/pschmitt/guacapy",
    packages=find_packages(),
    install_requires=["requests", "simplejson"],
)
