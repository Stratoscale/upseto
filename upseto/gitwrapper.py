import urlparse
import os
from upseto import run


def originURLBasename(originURL):
    originURLBasename = urlparse.urlparse(originURL).path.split("/")[-1]
    if originURLBasename.endswith(".git"):
        originURLBasename = originURLBasename[: - len(".git")]
    return originURLBasename


class GitWrapper:
    def __init__(self, directory):
        self._cachedOriginURL = None
        self._directory = directory
        if not os.path.isdir(os.path.join(directory, ".git")):
            raise Exception(
                "Directory '%s' does not look like a git repository (no .git subdirectory)" %
                directory)
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
        run.run(["git", "clone", originURL, basename], cwd=baseDirectory)
        clone = cls(os.path.join(baseDirectory, basename))
        clone.checkout('master')
        return clone

    def directory(self):
        return self._directory

    def hash(self, branch='HEAD'):
        return self._run(["git", "rev-parse", branch]).strip()

    def originURL(self):
        if self._cachedOriginURL is None:
            url = self._run(["git", "config", "--local", "remote.origin.url"]).strip()
            parts = list(urlparse.urlparse(url))
            netloc = parts[1]
            if '@' in netloc:
                netloc = netloc.split('@')[1]
            parts[1] = netloc
            self._cachedOriginURL = urlparse.urlunparse(parts)
        return self._cachedOriginURL

    def fetch(self):
        self._run(["git", "fetch"])

    def checkout(self, branch):
        self._run(["git", "checkout", branch])

    def shortStatus(self):
        return self._run(["git", "status", "-s"])

    def run(self, args):
        return self._run(["git"] + args)

    def _run(self, command):
        return run.run(command=command, cwd=self._directory)
