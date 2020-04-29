from os import environ
import os.path
import subprocess
from distutils.spawn import find_executable
from setuptools import Command


class ProtoBuild(Command):
    user_options = ['protoc']

    def initialize_options(self):
        self.protoc = environ.get('PROTOC') or find_executable('protoc')

    def finalize_options(self):
        assert os.path.exists(self.protoc), f'Protobuf compiler {self.protoc} does not exist.'

    def run(self):
        subprocess.check_call([self.protoc])
