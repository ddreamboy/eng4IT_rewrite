from setuptools import find_packages, setup


def get_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
    name='eng4IT',
    version='0.1.0',
    packages=find_packages(),
    install_requires=get_requirements(),
    python_requires='>=3.12',
)
