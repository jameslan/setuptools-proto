import os.path
from unittest.mock import patch
import pytest
from setuptools_proto import ProtoModule, ProtoBuild, proto_modules


@pytest.fixture()
def dist():
    from distutils.dist import Distribution
    return Distribution()


class TestProtoModule:
    def test_default_args(self):
        module1 = ProtoModule([])
        assert module1.sources == []
        assert module1.out_dir == '.'
        assert module1.cwd == '.'
        assert module1.include_dirs == []

        module2 = ProtoModule([])
        assert module1.include_dirs is not module2.include_dirs

    def test_valid_include_dirs(self):
        ProtoModule([], out_dir='.', include_dirs=[
            'tests',
            os.path.abspath(os.path.dirname(__file__)),
        ])

    def test_file_as_include_dir(self):
        with pytest.raises(AssertionError) as excinfo:
            ProtoModule([], out_dir='.', include_dirs=['tests/service.proto'])
        assert str(excinfo.value) == 'tests/service.proto is not an existing directory.'

    def test_nonexist_include_dir(self):
        with pytest.raises(AssertionError) as excinfo:
            ProtoModule([], out_dir='.', include_dirs=['nonexist.dir'])
        assert str(excinfo.value) == 'nonexist.dir is not an existing directory.'


class TestProtoBuild:
    def test_protoc_environ(self, dist):
        with patch.dict('os.environ', {'PROTOC': __file__}):
            build = ProtoBuild(dist)
            build.finalize_options()
            assert build.protoc == __file__

    def test_invalid_environ(self, dist):
        with patch.dict('os.environ', {'PROTOC': 'mock_protoc'}):
            build = ProtoBuild(dist)
            with pytest.raises(AssertionError) as excinfo:
                build.finalize_options()
            assert str(excinfo.value) == 'Protobuf compiler mock_protoc does not exist.'

    def test_find_protoc(self, dist):
        build = ProtoBuild(dist)
        build.finalize_options()
        assert os.path.isfile(build.protoc)  # able to find a protoc compiler

    def test_module_missing(self, dist):
        build = ProtoBuild(dist)
        with pytest.raises(AssertionError) as excinfo:
            build.run()

        assert str(excinfo.value) == 'Need to define proto_modules to run build_proto command'

    def test_build(self, dist):
        with patch('subprocess.check_call') as check_call, \
                patch('distutils.spawn.find_executable') as find_executable:
            find_executable.return_value = 'mock_protoc'
            dist.proto_modules = [ProtoModule(['tests/proto/echo/echo.proto'], cwd='tests')]
            build = ProtoBuild(dist)
            build.run()
            assert check_call.call_count == 1
            assert check_call.call_args == (
                ([
                     'mock_protoc',
                     '--python_betterproto_out=.',
                     '-I.',
                     'proto/echo/echo.proto',
                 ],),
                {'cwd': 'tests'},
            )

    def test_multiple_module(self, dist):
        with patch('subprocess.check_call') as check_call, \
                patch('distutils.spawn.find_executable') as find_executable:
            find_executable.return_value = 'mock_protoc'
            dist.proto_modules = [
                ProtoModule(['tests/proto/*/*.proto'], cwd='tests/proto'),
                ProtoModule(
                    ['tests/proto/**/*.proto'],
                    out_dir='tests/proto',
                    cwd='tests',
                    include_dirs=['tests/proto/echo'],
                ),
            ]
            build = ProtoBuild(dist)
            build.run()
            assert [call_args[:] for call_args in check_call.call_args_list] == [
                (
                    ([
                        'mock_protoc',
                        '--python_betterproto_out=.',
                        '-I.',
                        'echo/echo.proto',
                     ],),
                    {'cwd': 'tests/proto'},
                ), (
                    ([
                        'mock_protoc',
                        '--python_betterproto_out=proto',
                        '-I.',
                        '-Iproto/echo',
                        'proto/service.proto',
                        'proto/echo/echo.proto',
                     ],),
                    {'cwd': 'tests'},
                ),
            ]


class TestSetupKeywordHandler:
    def test_wrong_keyword(self, dist):
        proto_modules(dist, 'wrong_keyword', [])

        assert not hasattr(dist, 'wrong_keyword')
        assert getattr(dist, 'proto_modules') is None

    def test_invalid_module(self, dist):
        with pytest.raises(AssertionError) as excinfo:
            proto_modules(dist, 'proto_modules', 'incorrect')
        assert str(excinfo.value) == 'proto_modules is not a ProtoModule or a list of ProtoModules'

        with pytest.raises(AssertionError) as excinfo:
            proto_modules(dist, 'proto_modules', ['incorrect'])
        assert str(excinfo.value) == 'proto_modules is not a ProtoModule or a list of ProtoModules'

    def test_set_proto_module(self, dist):
        module = ProtoModule([])
        proto_modules(dist, 'proto_modules', module)
        assert dist.proto_modules == [module]

    def test_set_proto_modules(self, dist):
        modules = [ProtoModule([]), ProtoModule([])]
        proto_modules(dist, 'proto_modules', modules)
        assert dist.proto_modules == modules
