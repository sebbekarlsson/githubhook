from setuptools import setup, find_packages


setup(
    name='githubhook',
    version='1.0.0',
    install_requires=[
        'flask',
        'requests',
        'gitpython',
        'jinja2',
        'pytest',
        'mock'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
        ]
    }
)
