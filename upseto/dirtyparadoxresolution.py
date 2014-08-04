class DirtyParadoxResolution:
    def __init__(self):
        self._dirt = dict()

    def process(self, manifest):
        if manifest.originURL() not in self._dirt:
            self._dirt[manifest.originURL()] = dict()
        dirt = dict(self._dirt[manifest.originURL()])
        for requirement in manifest.requirements():
            if requirement['originURL'] in dirt:
                continue
            if not requirement.get('dirtyParadoxResolution', False):
                continue
            dirt[requirement['originURL']] = requirement['hash']
        for requirement in manifest.requirements():
            self._dirt[requirement['originURL']] = dirt

    def hashOverride(self, requirement, parentOriginURL):
        dirt = self._dirt[parentOriginURL]
        return dirt.get(requirement['originURL'], requirement['hash'])
