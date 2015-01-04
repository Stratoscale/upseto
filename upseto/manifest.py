import yaml
import os
from upseto import gitwrapper


class Manifest:
    _FILENAME = "upseto.manifest"

    def __init__(self, data, originURL):
        assert isinstance(data, dict)
        assert 'requirements' in data
        self._data = data
        self._originURL = originURL
        self._assertValid()

    def originURL(self):
        return self._originURL

    def originURLBasename(self):
        return gitwrapper.originURLBasename(self._originURL)

    def requirements(self):
        return self._data['requirements']

    def save(self):
        with open(self._FILENAME, "w") as f:
            f.write(yaml.dump(self._data, default_flow_style=False))

    def addRequirement(self, originURL, hash):
        for requirement in self._data['requirements']:
            if originURL == requirement['originURL']:
                requirement['hash'] = hash
                return
        self._data['requirements'].append(
            dict(originURL=originURL, hash=hash))

    def dirtyFirstRequirements(self):
        sortedRequirements = list(self.requirements())
        sortedRequirements.sort(key=lambda x: 0 if x.get('dirtyParadoxResolution', False) else 1)
        return sortedRequirements

    def _requirementByBasename(self, basename):
        for requirement in self._data['requirements']:
            if gitwrapper.originURLBasename(requirement['originURL']) == basename:
                return requirement
        raise Exception("Origin URL with the basename '%s' was not found in requirement list", basename)

    def delRequirementByBasename(self, basename):
        requirement = self._requirementByBasename(basename)
        self._data['requirements'].remove(requirement)

    def clearAllDirtyParadoxResolution(self):
        for requirement in self._data['requirements']:
            if 'dirtyParadoxResolution' in requirement:
                del requirement['dirtyParadoxResolution']

    def setDirtyParadoxResolution(self, basename):
        requirement = self._requirementByBasename(basename)
        requirement['dirtyParadoxResolution'] = True

    @classmethod
    def fromDir(cls, directory):
        filename = os.path.join(directory, cls._FILENAME)
        with open(filename) as f:
            data = yaml.load(f.read())
        return cls(data, cls._originURL(directory))

    @classmethod
    def fromDirOrNew(cls, directory):
        if cls.exists(directory):
            return cls.fromDir(directory)
        else:
            return cls(dict(requirements=[]), cls._originURL(directory))

    @classmethod
    def fromLocalDir(cls):
        return cls.fromDir('.')

    @classmethod
    def fromLocalDirOrNew(cls):
        return cls.fromDirOrNew('.')

    @classmethod
    def exists(cls, directory):
        return os.path.exists(os.path.join(directory, cls._FILENAME))

    def _assertValid(self):
        requirements = set()
        for requirement in self._data['requirements']:
            if requirement['originURL'] in requirements:
                raise Exception("'%s' located twice in requirement list" % requirement['originURL'])
            requirements.add(requirement['originURL'])

    @classmethod
    def _originURL(self, directory):
        return gitwrapper.GitWrapper(directory).originURL()
