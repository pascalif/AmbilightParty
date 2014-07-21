from setuptools import setup, find_packages

setup(
    name = "AmbilightParty",
    version = "1.0",
    description = "Have fun with your Philips Ambilight TV",
    author = "Pascalif",
    url = "https://github.com/pascalif/AmbilightParty",
    packages = find_packages(),
    keywords = "Ambilight Philips JointSpace television",
    entry_points = {
        'console_scripts':
        [
            'ambilight-party=ambilight.party:main'
        ]
    },
    package_data = {
        'ambilight': ['data/*.json']
    },
    install_requires = ['requests>=2.2.1'],
    license = 'GPL'
)