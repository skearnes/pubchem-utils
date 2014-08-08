from setuptools import setup, find_packages


def main():
    setup(
        name='pubchem_utils',
        version='0.1',
        license='3-clause BSD',
        url='https://github.com/skearnes/pubchem-utils',
        description='Utilities for interacting with PubChem',
        packages=find_packages(),
    )

if __name__ == '__main__':
    main()
