import os
import shutil
import re

from sphinx.ext.apidoc import main as sphinx_apidoc

from breathe.apidoc import main as breathe_apidoc

from doc.conf import breathe_projects

from .helpers import cd, sysargs, generate_doxygen


ROOT_PKG = 'py_cpp'
APIDOC_DIR = 'code'

PY_EXCLUDE = ['version.py']
PY_DIR = 'py'

CPP_DIR = 'cpp'


class ApidocBuilder(object):

    def __init__(self, app):
        self.doc_dir = app.srcdir
        root_dir = os.path.dirname(self.doc_dir)
        self.src_dir = os.path.join(root_dir, ROOT_PKG)
        self.apidoc_dir = os.path.join(self.doc_dir, APIDOC_DIR)
        self.html_output = os.path.join(self.doc_dir, 'build', 'html')

    def generate_py_apidoc(self):
        """
        Generates API documentation from code for all python modules and
        packages
        """

        apidoc_output = os.path.join(self.apidoc_dir, PY_DIR)

        # cleanup
        try:
            shutil.rmtree(apidoc_output)
        except OSError:
            # dir already removed
            pass
        os.makedirs(apidoc_output)

        with cd(apidoc_output):
            self._generate_py_apidoc(apidoc_output)

    def _generate_py_apidoc(self, output_dir):
        # In this function we are in the code documentation output directory

        root_pkg_name = os.path.basename(self.src_dir)

        # python modules apidoc
        sphinx_apidoc([
            '--implicit-namespaces', '--separate', '--force',
            '-o', output_dir, self.src_dir] + [
            os.path.join(self.src_dir, os.path.normpath(p))
            for p in PY_EXCLUDE
        ])

        os.remove('modules.rst')
        os.rename(root_pkg_name + '.rst', 'modules.rst')

        for f in os.listdir(output_dir):

            f_path = os.path.join(output_dir, f)

            # 1. calculate new file path
            f_spl = f.split('.')

            d = f_spl[1:-2]

            # 2. search and replace root package name in file + change paths
            fh = open(f_path, 'r')
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
                # replace title and strip module contents for root package
                content[0] = 'Python\n'
                content[1] = content[1][0] * (len(content[0]) - 1) + '\n'
                content = content[:-8]

            fh = open(f_path, 'w')
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

    def generate_cpp_apidoc(self):
        """
        Generates API documentation from code for all C/C++ modules, via
        doxygen and breathe
        """

        apidoc_output = os.path.join(self.apidoc_dir, CPP_DIR)

        # cleanup
        try:
            for name, path in breathe_projects.items():
                shutil.rmtree(path)
                shutil.rmtree(os.path.join(apidoc_output, name))
        except OSError:
            # dir already removed
            pass

        with cd(self.doc_dir):
            self._generate_cpp_apidoc(apidoc_output)

    def _generate_cpp_apidoc(self, output_dir):
        # run doxygen and breathe-apidoc

        # read Doxyfile
        doxyfile = ''
        for l in open('Doxyfile', 'r').readlines():
            if l.strip() and not l.startswith('#'):
                doxyfile += l

        for name, path in breathe_projects.items():
            generate_doxygen(doxyfile % {
                'project_name': name,
                'input_dir': os.path.join(self.src_dir, name),
                'output_dir': os.path.split(path)[0],
                'xml_output': os.path.split(path)[1],
                'strip_from_path': os.path.join(self.src_dir, name)
            })
            breathe_output = os.path.join(output_dir, name)
            with sysargs(['-o', breathe_output, '-f', '-p', name, path]):
                breathe_apidoc()

            file_list = os.path.join(breathe_output, 'filelist.rst')
            fh = open(file_list, 'r')
            content = fh.readlines()
            fh.close()

            content[0] = name + '\n'
            content[1] = content[1][0] * len(name) + '\n'

            fh = open(file_list, 'w')
            fh.write(''.join(content))
            fh.close()

    def run(self, *args, **kwargs):
        # generate auto documentation
        self.generate_py_apidoc()
        self.generate_cpp_apidoc()


def build_apidoc(app):
    builder = ApidocBuilder(app)
    builder.run()
