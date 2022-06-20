import subprocess32


class RunError(Exception):
    def __init__(self, calledProcessError, cwd):
        self._calledProcessError = calledProcessError
        self._cwd = cwd

    def __str__(self):
        return str(self._calledProcessError) + " in '%s'. Output was:\n%s" % (
            self._cwd, self._calledProcessError.output)


def run(command, cwd=None):
    try:
        return subprocess32.check_output(
            command, cwd=cwd, stderr=subprocess32.STDOUT,
            stdin=open("/dev/null"), close_fds=True)
    except subprocess32.CalledProcessError as e:
        raise RunError(e, cwd)
