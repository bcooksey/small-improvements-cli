from setuptools import setup

setup(
    name='small-improvements-cli',
    version='1.0',
    py_modules=[
        'caches',
        'commands',
        'constants',
        'small_improvements',
        'utils',
        'client',
    ],
    install_requires=[
        'click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        small-improvements=commands:cli
    ''',
)
