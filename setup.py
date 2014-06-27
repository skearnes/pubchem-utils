from setuptools import setup, find_packages


def main():
    setup(
        name='pubchem',
        version='0.1',
        license='3-clause BSD',
        url='https://github.com/skearnes/pubchem',
        description='Utilities for interacting with PubChem',
        packages=find_packages(),
    )

if __name__ == '__main__':
    main()
