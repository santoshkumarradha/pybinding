import os
import sys
import shutil
import platform
import subprocess

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.egg_info import manifest_maker


if sys.version_info[:2] < (3, 4):
    print("Python >= 3.4 is required. It must also be 64-bit.")
    sys.exit(-1)

if sys.maxsize <= 2**32:
    print("A 64-bit version of Python >= 3.4 is required")
    sys.exit(-1)


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        super().__init__(name, sources=[])
        self.sourcedir = sourcedir


class CMakeBuild(build_ext):
    def run(self):
        if shutil.which('cmake') is None:
            print("CMake 3.0 or newer is required to build pybinding")
            sys.exit(-1)

        for ext in self.extensions:
            build_dir = os.path.join(os.path.dirname(__file__), 'build', 'cmake')
            os.makedirs(build_dir, exist_ok=True)
            cmake_dir = os.path.abspath(ext.sourcedir)

            extpath = self.get_ext_fullpath(ext.name)
            extfulldir = os.path.abspath(os.path.dirname(extpath))
            cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extfulldir]

            if platform.system() == "Windows":
                cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE=' + extfulldir]
                cmake_args += ['-G', 'Visual Studio 14 2015 Win64']

            subprocess.check_call(['cmake', cmake_dir] + cmake_args, cwd=build_dir)
            subprocess.check_call(['cmake', '--build', '.', '--config', 'Release'], cwd=build_dir)


manifest_maker.template = "setup.manifest"
setup(
    name='pybinding',
    version='0.6.0',
    description='Python tight-binding package',
    long_description='',
    url='https://github.com/dean0x7d/pybinding',
    license='BSD',
    keywords='pybinding tight-binding physics cmt',

    author='Dean Moldovan',
    author_email='dean.moldovan@uantwerpen.be',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: C++',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',

    ],

    packages=find_packages(exclude=['dependencies', 'test*']),
    ext_modules=[CMakeExtension('_pybinding')],
    install_requires=['numpy>=1.9.0', 'scipy>=0.15', 'matplotlib>=1.5.0',
                      'py-cpuinfo>=0.1.4', 'pytest>=2.8'],
    zip_safe=False,
    cmdclass=dict(build_ext=CMakeBuild)
)
