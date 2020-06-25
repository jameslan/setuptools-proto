# setuptools-proto

`setuptools` plugin to compile `.proto` files using `python-betterproto`.

## Prerequisite

- Protobuf compiler `protoc`
- Python 3.6+

## Enable `setuptools-proto`

In either of the following scenarios, `setuptools-proto` will take effects.

* Option 1, install `setuptools-proto` using `pip` or other tools:

```shell script
$ pip install setuptools-proto
```

* Option 2, require `setuptools-proto` in `setup_requires` keyword of `setuptools`.

So, add it either in `setup.py` in a imperative fashion,

```python
setuptools.setup(
    setup_requires=['setuptools-proto'],
)
```

or in `seutp.cfg` in a declarative manner.

```ini
[options]
setup_requires =
    setuptools-proto
```

## Configuration

### Protobuf modules

To let `setuptools-proto` know what to compile,
define `proto_modules` as a `ProtoModule` list.

```python
from setuptools import setup
from setuptools_proto import ProtoModule

module1 = ProtoModule(
    ['proto/sample/**/*.proto'],
    cwd='proto/sample',
)
module2 = ProtoModule(
    ['demo/grpc/echo.proto', 'demo/grpc/hello.proto'],
    cwd='demo/grpc',
    out_dir='proto',
    include_dirs=['demo/schema'],
)


setup(
    proto_modules=[module1, module2],
)
```

### `protoc` compiler

By default, `setuptools-proto` will use the system `protoc` compiler.
If there's a custom install of `protoc`, which is not in the `PATH`,
You can point environment variable `PROTOC` to it,
or command line argument `--protoc` to it.

For example,

```shell script
$ python setup.py --protoc /path/to/protoc build_proto
```

## Execute

An extra setuptools command `build_proto` is added, to compile `.proto` to python code.
This command will be automatically run before setuptools command `build_py`.
