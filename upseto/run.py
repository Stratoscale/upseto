import subprocess


def run(command, cwd=None):
    try:
        return subprocess.check_output(
            command, cwd=cwd, stderr=subprocess.STDOUT,
            stdin=open("/dev/null"), close_fds=True)
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError("Failed command '%s': %s in '%s' output:\n%s" % (
            command, e, cwd, e.output))
