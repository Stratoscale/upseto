import urlparse
import os
import re
from upseto import run
from upseto import gitconfigparser


def originURLBasename(originURL):
    originURLBasename = urlparse.urlparse(originURL).path.split("/")[-1]
    if originURLBasename.endswith(".git"):
        originURLBasename = originURLBasename[: - len(".git")]  # pragma: no cover
    return originURLBasename


def normalizeOriginURL(originURL):
    originURL = re.sub(r'^git@(\S+?):(.*)$', r'https://\1/\2', originURL)
    if originURL.endswith(".git"):
        originURL = originURL[: - len(".git")]  # pragma: no cover
    return originURL


class GitWrapper:
    def __init__(self, directory):
        self._cachedOriginURL = None
        self._directory = directory
        if not os.path.isdir(os.path.join(directory, ".git")):
            raise Exception(
                "Directory '%s' does not look like a git repository (no .git subdirectory)" %
                directory)


    @classmethod
    def existing(cls, originURL, baseDirectory):
        basename = originURLBasename(originURL)
        directory = os.path.join(baseDirectory, basename)
        if not os.path.isdir(directory):
            raise Exception("Directory '%s' does not exist" % directory)
        existing = cls(directory)
        if normalizeOriginURL(existing.originURL()) != normalizeOriginURL(originURL):
            raise Exception(
                "Existing directory '%s' origin URL is '%s' which is not the expected '%s' "
                "(normalized '%s' and '%s')" % (
                    directory, existing.originURL(), originURL,
                    normalizeOriginURL(existing.originURL()),
                    normalizeOriginURL(originURL)))
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
            url = gitconfigparser.GitConfigParser(self._directory).originURL()
            parts = list(urlparse.urlparse(url))
            netloc = parts[1]
            if '@' in netloc:
                netloc = netloc.split('@')[1]
            parts[1] = netloc
            self._cachedOriginURL = urlparse.urlunparse(parts)
        return self._cachedOriginURL

    def originURLBasename(self):
        return originURLBasename(self.originURL())

    def fetch(self):
        self._run(["git", "fetch", "--prune"])

    def checkout(self, branch):
        self._run(["git", "checkout", branch])

    def shortStatus(self):
        return self._run(["git", "status", "-s"])

    def run(self, args):
        return self._run(["git"] + args)

    def _run(self, command):
        return run.run(command=command, cwd=self._directory)
