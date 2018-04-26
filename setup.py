import os
import re
import sys
import platform
import subprocess
from glob import glob

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion


# PACKAGE is the name of the python package (= its folder name)
PACKAGE = 'py_cpp'

# credentials
AUTHOR = 'Thomas Khyn'
AUTHOR_EMAIL = 'thomas@ksytek.com'
URL = 'https://bitbucket.org/tkhyn/py_cpp/'


# imports versioning variables without importing the package
exec(open(os.path.join(PACKAGE, 'version.py')).read())

dev_status = __version_info__[3]
if dev_status == 'alpha' and not __version_info__[4]:
    dev_status = 'pre'

DEV_STATUS = {
    'pre': '2 - Pre-Alpha',
    'alpha': '3 - Alpha',
    'beta': '4 - Beta',
    'rc': '4 - Beta',
    'final': '5 - Production/Stable'
}


# from https://github.com/pybind/cmake_example
class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        super(CMakeExtension, self).__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeExtensionBuilder(object):
    """
    Base extension builder mixin that can be used to build extensions out of
    setup.py (for example in tests/conftests.py)
    """

    extensions = [
        CMakeExtension(d.split(os.sep)[-2], d)
        for d in glob(os.path.join(PACKAGE, "*", ""))
        if os.path.isfile(os.path.join(d, 'CMakeLists.txt'))
    ]
    package = PACKAGE

    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                'CMake must be installed to build the following extensions: '
                ', '.join(e.name for e in self.extensions)
            )

        if platform.system() == "Windows":
            cmake_version = LooseVersion(
                re.search(r'version\s*([\d.]+)', out.decode()).group(1)
            )
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    @staticmethod
    def target(name):
        return name

    def build_extension(self, ext):
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name))
        )
        cfg = 'Debug' if self.debug else 'Release'

        cmake_args = ['-DCMAKE_BUILD_TYPE=' + cfg] + [
            '-DCMAKE_%s_OUTPUT_DIRECTORY=%s' % (t, extdir)
            for t in ('LIBRARY', 'RUNTIME')
        ]

        build_args = ['--config', cfg, '--target', self.target(ext.name)]

        if platform.system() == "Windows":
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '%s -DVERSION_INFO=\\"%s\\"' % (
            env.get('CXXFLAGS', ''), get_version()
        )
        build_temp = os.path.join(self.build_temp, ext.name)
        if not os.path.exists(build_temp):
            os.makedirs(build_temp)

        try:
            kwargs = self.get_subprocess_kwargs()
        except AttributeError:
            kwargs = {}

        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args,
                              cwd=build_temp, env=env, **kwargs)
        subprocess.check_call(['cmake', '--build', '.'] + build_args,
                              cwd=build_temp, **kwargs)


class CMakeBuild(CMakeExtensionBuilder, build_ext):

    def initialize_options(self):
        super(CMakeBuild, self).initialize_options()
        self.package = CMakeExtensionBuilder.package


if __name__ == '__main__':
    # we're importing setup.py from tests.conftest, and we don't want setup()
    # to execute
    setup(
        name=PACKAGE,
        version=__version__,
        description='Template Python project with C/C++ modules',
        long_description=open(os.path.join('README.rst')).read(),
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        keywords=[],
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Development Status :: %s' % DEV_STATUS[dev_status],
            'Environment :: Console'
        ],
        ext_modules=CMakeExtensionBuilder.extensions,
        cmdclass={
            'build_ext': CMakeBuild
        },
        packages=find_packages(),
        install_requires=(),
        entry_points={
            'console_scripts': [
                '%s = %s.main:run' % ((PACKAGE,)*2)
            ],
        },
        zip_safe=False
    )
