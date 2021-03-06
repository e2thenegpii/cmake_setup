import os
import subprocess
import shutil
import sys
from setuptools import Extension
from setuptools.command.build_ext import build_ext
from distutils.spawn import find_executable

CMAKE_EXE = os.environ.get('CMAKE_EXE', find_executable('cmake'))


def check_for_cmake():
    if not CMAKE_EXE:
        print('cmake executable not found. '
              'Set CMAKE_EXE environment or update your path')
        sys.exit(1)


class CMakeExtension(Extension):
    """
    setuptools.Extension for cmake
    """

    def __init__(self, name, sourcedir=''):
        check_for_cmake()
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuildExt(build_ext):
    """
    setuptools build_exit which builds using cmake & make
    You can add cmake args with the CMAKE_COMMON_VARIABLES environment variable
    """

    def build_extension(self, ext):
        check_for_cmake()
        if isinstance(ext, CMakeExtension):
            output_dir = os.path.abspath(
                os.path.dirname(self.get_ext_fullpath(ext.name)))

            build_type = 'Debug' if self.debug else 'Release'
            cmake_args = [CMAKE_EXE,
                          ext.sourcedir,
                          '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + output_dir,
                          '-DCMAKE_BUILD_TYPE=' + build_type]
            cmake_args.extend(
                [x for x in
                 os.environ.get('CMAKE_COMMON_VARIABLES', '').split(' ')
                 if x])

            env = os.environ.copy()
            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)
            print(" ".join(cmake_args))
            subprocess.check_call(cmake_args,
                                  cwd=self.build_temp,
                                  env=env)
            subprocess.check_call(['make', '-j', ext.name],
                                  cwd=self.build_temp,
                                  env=env)
        else:
            super().build_extension(ext)


__all__ = ['CMakeBuildExt', 'CMakeExtension']
