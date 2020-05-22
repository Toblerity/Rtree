#!/usr/bin/env python
import os, sys

import setuptools, pathlib, subprocess
from setuptools import setup, Extension
from setuptools.dist import Distribution
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
import itertools as it

# Get text from README.txt
with open('docs/source/README.txt', 'r') as fp:
    readme_text = fp.read()

# Get __version without importing
with open('rtree/__init__.py', 'r') as fp:
    # get and exec just the line which looks like "__version__ = '0.9.4'"
    exec(next(line for line in fp if '__version__' in line))

def check_cmake():
    try:
        out = subprocess.check_output(['cmake', '--version'])
        return True
    except OSError:
        return False

class cmake_extension(Extension):
    def __init__(self, name):
        Extension.__init__(self, name, sources=[])

class cmake_build(build_ext):
    def run(self):
        if not check_cmake():
            raise RuntimeError('CMake is not available. CMake 3.12 is required.')

        # The path where CMake will be configured and Arbor will be built.
        build_directory = os.path.abspath(self.build_temp)
        print("build dir:", build_directory)
        # The path where the package will be copied after building.
        lib_directory = os.path.abspath(self.build_lib)
        print("lib dir:", lib_directory)
        # The path where the Python package will be compiled.
        source_path = build_directory + '/python/arbor'
        # Where to copy the package after it is built, so that whatever the next phase is
        # can copy it into the target 'prefix' path.
        dest_path = lib_directory + '/libspatialindex'

        cmake_args = [
            '-DCMAKE_BUILD_TYPE=Release' # we compile with debug symbols in release mode.
        ]

        print('-'*5, 'cmake arguments: {}'.format(cmake_args))

        build_args = ['--config', 'Release']

        # Assuming Makefiles
        build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{}'.format(env.get('CXXFLAGS', ''))
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # CMakeLists.txt is in the same directory as this setup.py file
        cmake_list_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "libspatialindex")
        print('-'*20, 'Configure CMake')
        subprocess.check_call(['cmake', cmake_list_dir] + cmake_args,
                              cwd=self.build_temp, env=env)

        print('-'*20, 'Build')
        cmake_cmd = ['cmake', '--build', '.'] + build_args
        subprocess.check_call(cmake_cmd,
                              cwd=self.build_temp)

        # Copy from build path to some other place from whence it will later be installed.
        # ... or something like that
        # ... setuptools is an enigma monkey patched on a mystery
        if not os.path.exists(dest_path):
            os.makedirs(dest_path, exist_ok=True)
        self.copy_tree(source_path, dest_path)

setup(
    name='Rtree',
    version=__version__,
    description='R-Tree spatial index for Python GIS',
    license='MIT',
    keywords='gis spatial index r-tree',
    author='Sean Gillies',
    author_email='sean.gillies@gmail.com',
    maintainer='Howard Butler',
    maintainer_email='howard@hobu.co',
    url='https://github.com/Toblerity/rtree',
    long_description=readme_text,
    long_description_content_type='text/markdown',
    packages=['rtree'],
    package_data={"rtree": ["lib/*", "include/**/*", "include/**/**/*" ]},
    zip_safe=False,
    ext_modules=[cmake_extension('libspatialindex')],
    cmdclass={
        'build_ext': cmake_build,
    },
    include_package_data = True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: C++',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Database',
    ],
)
