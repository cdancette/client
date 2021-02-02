"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.message
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor = ...

class TelemetryRecord(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    python_version: typing.Text = ...
    cli_version: typing.Text = ...
    huggingface_version: typing.Text = ...

    @property
    def imports_init(self) -> global___Imports: ...

    @property
    def imports_finish(self) -> global___Imports: ...

    @property
    def feature(self) -> global___Feature: ...

    @property
    def env(self) -> global___Env: ...

    def __init__(self,
        *,
        imports_init : typing.Optional[global___Imports] = ...,
        imports_finish : typing.Optional[global___Imports] = ...,
        feature : typing.Optional[global___Feature] = ...,
        python_version : typing.Text = ...,
        cli_version : typing.Text = ...,
        huggingface_version : typing.Text = ...,
        env : typing.Optional[global___Env] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal[u"env",b"env",u"feature",b"feature",u"imports_finish",b"imports_finish",u"imports_init",b"imports_init"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal[u"cli_version",b"cli_version",u"env",b"env",u"feature",b"feature",u"huggingface_version",b"huggingface_version",u"imports_finish",b"imports_finish",u"imports_init",b"imports_init",u"python_version",b"python_version"]) -> None: ...
global___TelemetryRecord = TelemetryRecord

class Imports(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    torch: builtins.bool = ...
    keras: builtins.bool = ...
    tensorflow: builtins.bool = ...
    fastai: builtins.bool = ...
    sklearn: builtins.bool = ...
    xgboost: builtins.bool = ...
    catboost: builtins.bool = ...
    lightgbm: builtins.bool = ...
    pytorch_lightning: builtins.bool = ...
    pytorch_ignite: builtins.bool = ...
    transformers: builtins.bool = ...

    def __init__(self,
        *,
        torch : builtins.bool = ...,
        keras : builtins.bool = ...,
        tensorflow : builtins.bool = ...,
        fastai : builtins.bool = ...,
        sklearn : builtins.bool = ...,
        xgboost : builtins.bool = ...,
        catboost : builtins.bool = ...,
        lightgbm : builtins.bool = ...,
        pytorch_lightning : builtins.bool = ...,
        pytorch_ignite : builtins.bool = ...,
        transformers : builtins.bool = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal[u"catboost",b"catboost",u"fastai",b"fastai",u"keras",b"keras",u"lightgbm",b"lightgbm",u"pytorch_ignite",b"pytorch_ignite",u"pytorch_lightning",b"pytorch_lightning",u"sklearn",b"sklearn",u"tensorflow",b"tensorflow",u"torch",b"torch",u"transformers",b"transformers",u"xgboost",b"xgboost"]) -> None: ...
global___Imports = Imports

class Feature(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    watch: builtins.bool = ...
    finish: builtins.bool = ...
    save: builtins.bool = ...
    offline: builtins.bool = ...
    resumed: builtins.bool = ...
    grpc: builtins.bool = ...

    def __init__(self,
        *,
        watch : builtins.bool = ...,
        finish : builtins.bool = ...,
        save : builtins.bool = ...,
        offline : builtins.bool = ...,
        resumed : builtins.bool = ...,
        grpc : builtins.bool = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal[u"finish",b"finish",u"grpc",b"grpc",u"offline",b"offline",u"resumed",b"resumed",u"save",b"save",u"watch",b"watch"]) -> None: ...
global___Feature = Feature

class Env(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    jupyter: builtins.bool = ...
    kaggle: builtins.bool = ...
    windows: builtins.bool = ...
    m1_gpu: builtins.bool = ...

    def __init__(self,
        *,
        jupyter : builtins.bool = ...,
        kaggle : builtins.bool = ...,
        windows : builtins.bool = ...,
        m1_gpu : builtins.bool = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal[u"jupyter",b"jupyter",u"kaggle",b"kaggle",u"m1_gpu",b"m1_gpu",u"windows",b"windows"]) -> None: ...
global___Env = Env
