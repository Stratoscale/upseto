import subprocess
import logging


def run(command, cwd=None):
    try:
        return subprocess.check_output(
            command, cwd=cwd, stderr=subprocess.STDOUT,
            stdin=open("/dev/null"), close_fds=True)
    except subprocess.CalledProcessError as e:
        logging.error("Failed command '%s' output:\n%s" % (command, e.output))
        raise
