import subprocess


def run(where, arguments):
    try:
        output = subprocess.check_output(
            "python -m upseto.main " + arguments, cwd=where.directory(),
            shell=True, stderr=subprocess.STDOUT, close_fds=True)
    except subprocess.CalledProcessError as e:
        print e.output
        raise
    return output


def runShouldFail(where, arguments, partOfErrorMessage):
    try:
        output = subprocess.check_output(
            "python -m upseto.main " + arguments, cwd=where.directory(),
            shell=True, stderr=subprocess.STDOUT, close_fds=True)
    except subprocess.CalledProcessError as e:
        if partOfErrorMessage in e.output.lower():
            return
        else:
            print e.output
            raise Exception((
                "Expected upseto command '%s' to fail with the error '%s', "
                "but it failed with '%s'") % (arguments, partOfErrorMessage, e.output))
    print output
    raise Exception("Expected upseto command '%s' to fail, but it didn't" % arguments)
