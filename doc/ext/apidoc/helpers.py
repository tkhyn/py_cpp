import os
import sys
from copy import copy
from contextlib import contextmanager
from subprocess import Popen, PIPE


@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


@contextmanager
def sysargs(args):
    sys_argv = copy(sys.argv)
    sys.argv[1:] = args
    try:
        yield
    finally:
        sys.argv = sys_argv


def generate_doxygen(doxygen_input):
    """
    Borrowed from exhale
    """

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
