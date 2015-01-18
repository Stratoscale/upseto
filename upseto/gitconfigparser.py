import re
import os


class GitConfigParser:
    def __init__(self, repoDirectory):
        self._repoDirectory = repoDirectory

    def originURL(self):
        with open(os.path.join(self._repoDirectory, ".git", "config")) as f:
            contents = f.read()
        return self._parseOriginURL(contents)

    def _parseOriginURL(self, contents):
        irrelevant, remoteOriginAndAfter = contents.split('[remote "origin"]')
        remoteOrigin = remoteOriginAndAfter.split("\n[")[0]
        return re.search(r"url\s*=\s*(\S+)", remoteOrigin).group(1)
