from setuptools import setup

setup(
    name='time_parser',
    version='0.1.0',
    py_modules=['time_parser'],
    install_requires=[
        'Click',
        'Lark',
        'inflect',
    ],
    entry_points={
        'console_scripts': [
            'time_parser = time_parser:cli',
        ],
    },
)
