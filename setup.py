"""add headers to cmake libraries
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cmake-c-includes',
    use_scm_version={"root": ".", "relative_to": __file__},
    setup_requires=['setuptools_scm'],
    description='add headers to cmake libraries',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bozzzzo/cmake-c-includes',
    author='Bozo Dragojevic',
    author_email='bozzo@digiverse.si',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='cmake add_library',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7, <4',
    install_requires=[
                      'docopt',
                      'cmakeast',
                      'importlib-metadata'],
    extras_require={
        'dev': ['check-manifest',
                'flake8',
                'pytest',
                'tox'],
        'test': ['coverage'],
    },
    entry_points={
        'console_scripts': [
            'cmake-c-includes=cmakeincludes.cmd:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/bozzzzo/cmake-c-includes/issues',
        'Source': 'https://github.com/bozzzzo/cmake-c-includes/',
    },
)
