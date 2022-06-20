import subprocess32
import os


def run(where, arguments):
    try:
        output = subprocess32.check_output(
            "python -m coverage run --parallel-mode -m upseto.main " + arguments, cwd=where.directory(),
            shell=True, stderr=subprocess32.STDOUT, close_fds=True)
    except subprocess32.CalledProcessError as e:
        print e.output
        raise
    return output


def runShouldFail(where, arguments, partOfErrorMessage):
    try:
        output = subprocess32.check_output(
            "python -m coverage run --parallel-mode -m upseto.main " + arguments, cwd=where.directory(),
            shell=True, stderr=subprocess32.STDOUT, close_fds=True)
    except subprocess32.CalledProcessError as e:
        if partOfErrorMessage in e.output.lower():
            return
        else:
            print e.output
            raise Exception((
                "Expected upseto command '%s' to fail with the error '%s', "
                "but it failed with '%s'") % (arguments, partOfErrorMessage, e.output))
    print output
    raise Exception("Expected upseto command '%s' to fail, but it didn't" % arguments)


def packEgg(where, arguments, pythonPath):
    try:
        output = subprocess32.check_output(
            "python -m coverage run --parallel-mode -m upseto.packegg " + arguments,
            cwd=where.directory(), shell=True, stderr=subprocess32.STDOUT, close_fds=True,
            env=dict(os.environ, PYTHONPATH=pythonPath + ":" + os.environ['PYTHONPATH']))
    except subprocess32.CalledProcessError as e:
        print e.output
        raise
    return output


def runWhatever(where, commandLine):
    try:
        output = subprocess32.check_output(
            commandLine,
            cwd=where, shell=True, stderr=subprocess32.STDOUT, close_fds=True)
    except subprocess32.CalledProcessError as e:
        print e.output
        raise
    return output
