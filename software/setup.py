from setuptools import find_packages, setup

setup(
    name='fpvcar',
    packages=find_packages(include=['fpvcar']),
    version='0.1.2',
    description='Biblioteca FPV',
    author='Dener Ribeiro',
    # install_requires=['opencv-python', 'websockets'],
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest==4.4.1'],
    # test_suite='tests',
)

