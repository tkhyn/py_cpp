import os
import sys
import shutil
import re
from copy import copy
from subprocess import Popen, PIPE, STDOUT

from fabric.tasks import Task
from fabric.api import env

from sphinx import build_main as build
from sphinx.ext.apidoc import main as build_apidoc

from breathe.apidoc import main as breathe_apidoc

from doc.conf import breathe_projects


SOURCE_DIR = 'py_cpp'

APIDOC_DIR = 'apidoc'

PY_EXCLUDE = ['version.py']
PY_DIR = 'py'

CPP_DIR = 'cpp'


class SphinxBuilder(Task):

    def run(self, apidoc=False, *args, **kwargs):

        root_dir = os.path.dirname(env.real_fabfile)
        src_dir = os.path.join(root_dir, SOURCE_DIR)
        doc_dir = os.path.join(root_dir, 'doc')
        html_output = os.path.join(doc_dir, 'build', 'html')

        apidoc_output = os.path.join(doc_dir, APIDOC_DIR, PY_DIR)

        # generate auto documentation
        if apidoc:

            # cleanup
            try:
                shutil.rmtree(apidoc_output)
            except OSError:
                # dir already removed
                pass
            os.makedirs(apidoc_output)

            build_apidoc([
                '--implicit-namespaces', '--separate', '--force',
                '-o', apidoc_output, src_dir] + [
                os.path.join(src_dir, os.path.normpath(p)) for p in PY_EXCLUDE
            ])

            os.chdir(apidoc_output)

            root_pkg_name = os.path.basename(src_dir)

            os.remove('modules.rst')
            os.rename(root_pkg_name + '.rst', 'modules.rst')

            for f in os.listdir(apidoc_output):

                # 1. calculate new file path
                f_spl = f.split('.')

                d = f_spl[1:-2]

                # 2. search and replace root package name in file + change paths
                fh = open(f, 'r')
                content = fh.readlines()
                fh.close()

                for i in range(len(content)):
                    line = re.sub('\\\\(?P<char>[_-])', '\g<char>', content[i])

                    if '.. toctree::' in line:
                        # replace reference by relative path
                        i += 2
                        line = content[i]
                        while line != '\n':
                            path = line.replace(root_pkg_name + '.', '') \
                                       .strip().split('.')
                            new_path = []
                            for j in range(len(path)):
                                if j < len(d) and d[j] == path[j]:
                                    continue
                                new_path.append(path[j])
                            content[i] = '    %s\n' % '/'.join(new_path)
                            i += 1
                            line = content[i]
                        continue

                    if (root_pkg_name + '.') in line \
                    and ('.. automodule:: ' + root_pkg_name) not in line:
                        content[i] = re.sub(
                            root_pkg_name + r'\.', '', line
                        )
                        next_line = content[i + 1]
                        if ''.join(set(next_line[:-1])) in ('=', '-'):
                            content[i + 1] = next_line[-len(content[i]):]

                    if f == 'modules.rst':
                        if content[i] in ['Submodules', 'Subpackages']:
                            content[i+1] = content[i+1].replace('-', '=')

                if f == 'modules.rst':
                    # replace title and strip module contents for root package
                    content[0] = 'Python\n'
                    content[1] = content[1][0]*(len(content[0]) - 1) + '\n'
                    content = content[:-8]

                fh = open(f, 'w')
                fh.write(''.join(content))
                fh.close()

                if len(f_spl) == 2:
                    # do not move/rename modules.rst
                    continue

                # 3. move the file to its correct directory
                if len(d):
                    d = os.path.join(*d)
                    try:
                        os.makedirs(d)
                    except OSError:
                        # directory exists
                        pass
                else:
                    d = '.'

                dest = os.path.join(d, '.'.join(f_spl[-2:]))
                try:
                    os.remove(dest)
                except OSError:
                    # file does not exist already
                    pass
                os.rename(f, dest)

        os.chdir(doc_dir)

        # run doxygen and breathe-apidoc
        sys_argv = copy(sys.argv)

        # read Doxyfile
        doxyfile = ''
        for l in open('Doxyfile', 'r').readlines():
            if l.strip() and not l.startswith('#'):
                doxyfile += l

        for name, path in breathe_projects.items():
            _generate_doxygen(doxyfile % {
                'project_name': name,
                'input_dir': os.path.join(src_dir, name),
                'output_dir': os.path.split(path)[0],
                'xml_output': os.path.split(path)[1],
                'strip_from_path': os.path.join(src_dir, name)
            })
            breathe_output = os.path.join(APIDOC_DIR, CPP_DIR, name)
            sys.argv[1:] = [
                '-o', breathe_output,
                '-f',
                '-p', name,
                path
            ]
            breathe_apidoc()

            file_list = os.path.join(breathe_output, 'filelist.rst')
            fh = open(file_list, 'r')
            content = fh.readlines()
            fh.close()

            content[0] = name + '\n'
            content[1] = content[1][0]*len(name) + '\n'

            fh = open(file_list, 'w')
            fh.write(''.join(content))
            fh.close()

        sys.argv = sys_argv

        # build html documentation
        build(['build', doc_dir, html_output])


doc = SphinxBuilder()


def _generate_doxygen(doxygen_input):
    '''
    Borrowed from exhale
    '''

    if not isinstance(doxygen_input, str):
        return "Error: the `doxygen_input` variable must be of type `str`."

    doxyfile = doxygen_input == "Doxyfile"
    try:
        # Setup the arguments to launch doxygen
        if doxyfile:
            args = ["doxygen"]
            kwargs = {}
        else:
            args = ["doxygen", "-"]
            kwargs = {"stdin": PIPE}

        # Note: overload of args / kwargs, Popen is expecting a list as the
        # first parameter (aka no *args, just args)!
        doxygen_proc = Popen(args, **kwargs)

        # Communicate can only be called once, arrange whether or not stdin has
        # value
        if not doxyfile:
            # In Py3, make sure we are communicating a bytes-like object which
            # is no longer interchangeable with strings (as was the case in Py2)
            if sys.version[0] == "3":
                doxygen_input = bytes(doxygen_input, "utf-8")
            comm_kwargs = {"input": doxygen_input}
        else:
            comm_kwargs = {}

        # Waits until doxygen has completed
        doxygen_proc.communicate(**comm_kwargs)

        # Make sure we had a valid execution of doxygen
        exit_code = doxygen_proc.returncode
        if exit_code != 0:
            raise RuntimeError("Non-zero return code of [{0}] from 'doxygen'...".format(exit_code))
    except Exception as e:
        return "Unable to execute 'doxygen': {0}".format(e)

    # returning None signals _success_
    return None
