import os
import subprocess
from distutils import spawn
from typing import List, Optional

from setuptools import Command
from glob import glob


class ProtoBuild(Command):
    user_options = [('protoc', None, 'path of compiler protoc')]
    description = 'build .proto files using betterproto plugin'

    def initialize_options(self):
        self.protoc = os.environ.get('PROTOC') or spawn.find_executable('protoc')

    def finalize_options(self):
        assert os.path.exists(self.protoc), f'Protobuf compiler {self.protoc} does not exist.'

    def run(self):
        modules = getattr(self.distribution, 'proto_modules', None) or []

        if not modules:
            print('Warning: No proto_modules defined')

        for module in modules:
            cmd = [
                self.protoc,
                f'--python_betterproto_out={os.path.relpath(module.out_dir, module.cwd)}',
                '-I.',
            ]
            cmd.extend(f'-I{os.path.relpath(d, module.cwd)}' for d in module.include_dirs)
            for source in module.sources:
                cmd.extend(
                    os.path.relpath(p, module.cwd)
                    for p in glob(source, recursive=True)
                )
            print('[', ' '.join(cmd), ']')
            os.makedirs(module.out_dir, exist_ok=True)
            subprocess.check_call(cmd, cwd=module.cwd)


class ProtoModule:
    def __init__(
            self,
            sources: List[str],
            *,
            out_dir: str = None,
            cwd: Optional[str] = None,
            include_dirs: Optional[List[str]] = None,
    ):
        """
        Protobuf module: A collection of .proto source file names, as well as compilation flags.


        :param sources: [string]
          List of source file name patterns. Recursive wildcard (**) is supported.
        :param out_dir: string
          Directory where protoc to put output python files.
        :param cwd: string
          Working directory for the protoc compiler, set to current working directory if omitted.
          Note that select appropriate cwd could shorten the command line to invoke protoc,
          especially there are many .proto files and very long paths
        :param include_dirs: [string]
          The include directories for protoc. `cwd` will be added by default.
        """
        self.sources = sources
        self.cwd = cwd or '.'
        self.out_dir = out_dir or self.cwd
        self.include_dirs = include_dirs or []
        for include_dir in self.include_dirs:
            assert os.path.isdir(include_dir), \
                f'{include_dir} is not an existing directory.'


def proto_modules(dist, keyword, value):
    if keyword != 'proto_modules':
        return

    dist.proto_modules = value if isinstance(value, list) else [value]

    assert all(isinstance(m, ProtoModule) for m in dist.proto_modules), \
        'proto_modules is not a ProtoModule or a list of ProtoModules'
