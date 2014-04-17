import urlparse
import os
from upseto import shell


def originURLBasename(originURL):
    originUrlBasename = urlparse.urlparse(originURL).path.split("/")[-1]
    if originUrlBasename.endswith(".git"):
        originUrlBasename = originUrlBasename[: - len(".git")]
    return originUrlBasename


class GitWrapper:
    def __init__(self, directory):
        self._directory = directory
        if not os.path.isdir(os.path.join(directory, ".git")):
            raise Exception(
                ("Directory '%s' does not look like a git "
                "repository (no .git subdirectory)") % directory)
        if originURLBasename(self.originURL()) != os.path.basename(os.path.abspath(directory)):
            raise Exception(
                "Directory '%s' must be named exactly like the "
                "origin URL '%s' (with no '.git' extension)" % (
                    directory, self.originURL()))

    @classmethod
    def existing(cls, originURL, baseDirectory):
        basename = originURLBasename(originURL)
        directory = os.path.join(baseDirectory, basename)
        if not os.path.isdir(directory):
            raise Exception("Directory '%s' does not exist" % directory)
        existing = cls(directory)
        if existing.originURL() != originURL:
            raise Exception(
                "Existing directory '%s' origin URL is '%s' which is not the expected '%s'" % (
                    directory, existing.originURL(), originURL))
        return existing

    @classmethod
    def clone(cls, originURL, baseDirectory):
        basename = originURLBasename(originURL)
        shell.run("git clone '%s' '%s'" % (originURL, basename), cwd=baseDirectory)
        clone = cls(os.path.join(baseDirectory, basename))
        clone.checkout('master')
        return clone

    def directory(self):
        return self._directory

    def hash(self, branch='HEAD'):
        return self._run("git rev-parse '%s'" % branch).strip()

    def originURL(self):
        url = self._run("git config --local remote.origin.url").strip()
        parts = list(urlparse.urlparse(url))
        netloc = parts[1]
        if '@' in netloc:
            netloc = netloc.split('@')[1]
        parts[1] = netloc
        return urlparse.urlunparse(parts)

    def fetch(self):
        self._run("git fetch")

    def checkout(self, branch):
        self._run("git checkout '%s'" % branch)

    def _run(self, command):
        return shell.run(command=command, cwd=self._directory)
