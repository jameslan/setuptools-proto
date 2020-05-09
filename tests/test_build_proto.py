from subprocess import check_output


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


def test_build_proto():
    output = check_output([
        'python',
        '-c',
        setup_code,
        'build_proto',
    ]).decode()
    assert 'running build_proto' in output
