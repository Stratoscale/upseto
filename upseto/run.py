import subprocess


class RunError(Exception):
    def __init__(self, calledProcessError, cwd):
        self._calledProcessError = calledProcessError
        self._cwd = cwd

    def __str__(self):
        return str(self._calledProcessError) + " in '%s'. Output was:\n%s" % (
            self._cwd, self._calledProcessError.output)


def run(command, cwd=None):
    try:
        return subprocess.check_output(
            command, cwd=cwd, stderr=subprocess.STDOUT,
            stdin=open("/dev/null"), close_fds=True)
    except subprocess.CalledProcessError as e:
        raise RunError(e, cwd)
