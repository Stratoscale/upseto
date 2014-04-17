import subprocess
import tempfile
import shutil
import os
import random
import string

_tempDir = None


def setUp():
    global _tempDir
    assert _tempDir is None
    _tempDir = tempfile.mkdtemp()


def tearDown():
    global _tempDir
    shutil.rmtree(_tempDir, ignore_errors=True)
    assert _tempDir is not None
    _tempDir = None


def githubRootURL():
    global _tempDir
    assert _tempDir is not None
    return "file://" + _tempDir + "/github"


def localClonesDir():
    global _tempDir
    assert _tempDir is not None
    return os.path.join(_tempDir, "localclone")


def _run(command, cwd):
    try:
        return subprocess.check_output(
            command, shell=True, cwd=cwd, stderr=subprocess.STDOUT, close_fds=True)
    except subprocess.CalledProcessError as e:
        print e.output
        raise


class GitWrapper:
    def __init__(self, directory):
        self._directory = directory

    def directory(self):
        return self._directory

    def run(self, command):
        return _run(command=command, cwd=self._directory)

    def hash(self, branch='HEAD'):
        return self.run("git rev-parse " + branch).strip()

    def manifestFilename(self):
        return os.path.join(self._directory, "upseto.manifest")


class GitHub(GitWrapper):
    def __init__(self, name):
        assert _tempDir is not None
        directory = os.path.join(_tempDir, "github", name)
        os.makedirs(directory)
        GitWrapper.__init__(self, directory)
        self.run("git init")
        randomContent = ''.join(
            random.choice(string.ascii_letters) for i in xrange(10))
        self._write("firstCommitFile", randomContent)
        self.run("git add firstCommitFile")
        self.run("git commit -m 'Initial commit'")
        self.run("git checkout -b dont_hold_master")

    def _write(self, filename, content):
        with open(os.path.join(self.directory(), filename), "w") as f:
            f.write(content)


class LocalClone(GitWrapper):
    def __init__(self, gitHub):
        assert _tempDir is not None
        directory = os.path.join(
            localClonesDir(), os.path.basename(gitHub.directory()))
        if not os.path.isdir(localClonesDir()):
            os.makedirs(localClonesDir())
        _run("git clone file://%s" % gitHub.directory(), cwd=localClonesDir())
        GitWrapper.__init__(self, directory)
        self.run("git checkout master")

    def createAddCommitPush(self, filename):
        randomContent = ''.join(
            random.choice(string.ascii_letters) for i in xrange(10))
        with open(os.path.join(self.directory(), filename), "w") as f:
            f.write(randomContent)
        self.addCommitPush(filename)

    def addCommitPush(self, filename):
        self.run("git add %s" % filename)
        self.run("git commit -m 'a commit'")
        self.run("git push")

    def addCommitPushManifest(self):
        self.addCommitPush('upseto.manifest')

    def checkout(self, branch):
        self.run("git checkout " + branch)
