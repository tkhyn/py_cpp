import os
import shutil
import re

from fabric.tasks import Task
from fabric.api import env

from sphinx import build_main as build
from sphinx.ext.apidoc import main as build_apidoc

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

        # build html documentation
        build(['build', doc_dir, html_output])


doc = SphinxBuilder()
