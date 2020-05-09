from setuptools import setup


def main():
    setup(
        name='setuptools-proto',
        version='0.0.1',
        description='setuptools plugin to generate python file from protobuf',
        long_description=open('README.md').read(),
        url='https://github.com/jameslan/setuptools-proto',
        py_modules=['setuptools_proto'],
        install_requires=['setuptools-cmd-deps'],
    )


if __name__ == '__main__':
    main()
