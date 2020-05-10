from subprocess import check_output, check_call
import pytest


setup_code = """
from setuptools_proto import ProtoModule
from setuptools import setup


setup(proto_modules=ProtoModule(
    ["tests/space in name/*.proto"],
    out_dir="build/test_output",
    include_dirs=['tests/proto/echo'],
    cwd='tests',
))
"""


@pytest.fixture(scope='module', autouse=True)
def build_proto():
    check_call(['python', 'setup.py', 'develop'])
    yield
    check_call(['pip', 'uninstall', '-y', 'setuptools-proto'])


def test_build_proto():
    output = check_output([
        'python',
        '-c',
        setup_code,
        'build_proto',
    ]).decode()
    assert 'running build_proto' in output
