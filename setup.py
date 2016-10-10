from distutils.core import setup

setup(
    name='guacapy',
    version='0.8.1',
    description='REST API client for Guacamole',
    author='Philipp Schmitt',
    author_email='philipp.schmitt@post.lu',
    url='https://github.com/pschmitt/guacapy',
    packages=['guacapy'],
    install_requires=['requests'],
)
