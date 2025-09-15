from setuptools import setup
from setuptools import Extension
from setuptools.command.build_ext import build_ext
import sys
import sysconfig

try:
    import pybind11  # noqa: F401
    from pybind11.setup_helpers import Pybind11Extension, build_ext as build_ext_pybind
except Exception:
    Pybind11Extension = Extension
    build_ext_pybind = build_ext


ext_modules = [
    Pybind11Extension(
        name="animfetch.providers.source.planets_cpp",
        sources=["animfetch/providers/source/planets_cpp.cpp"],
        extra_compile_args=["-std=c++20", "-O3", "-DNDEBUG"],
    )
]


setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext_pybind},
)
