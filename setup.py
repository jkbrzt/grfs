import codecs

from setuptools import setup


def long_description():
    with codecs.open('README.rst', encoding='utf8') as f:
        return f.read()


setup(
    name='grfs',
    version='0.1.1',
    description='Ricoh GR II file system',
    long_description=long_description(),
    url='https://github.com/jkbrzt/grfs',
    download_url='https://github.com/jkbrzt/grfs',
    author='Jakub Roztocil',
    author_email='jakub@roztocil.co',
    license='MIT',
    modules='grfs',
    entry_points={
        'console_scripts': [
            'grfs = grfs:main',
        ],
    },
    install_requires=[
        'fusepy==2.0.4',
        'requests==2.10.0'
    ],
    classifiers=[],
)
