from setuptools import setup, find_packages
import os


APP_NAME = 'py_cpp'


# imports versionning variables, avoiding to import the `app` module
exec(open('app/version.py').read())

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

setup(
    name=APP_NAME,
    version=__version__,
    description='Boilerplate Python app with C/C++ modules',
    long_description=open(os.path.join('README.rst')).read(),
    author='Thomas Khyn',
    author_email='thomas@ksytek.com',
    url='https://bitbucket.org/tkhyn/py_cpp/',
    keywords=['directory', 'folder', 'update', 'synchronisation'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: %s' % DEV_STATUS[dev_status],
        'Environment :: Console'
    ],
    packages=find_packages(),
    install_requires=(),
    entry_points={
        'console_scripts': [
            '%s = app.main:run' % APP_NAME
        ],
    }
)
