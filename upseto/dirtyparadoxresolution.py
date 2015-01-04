class DirtyParadoxResolution:
    def __init__(self):
        self._dirt = dict()
        self._sameParentDirtyFirstAssertion_parentOriginUrl = None
        self._sameParentDirtyFirstAssertion_nonDirtyRequirementSpotted = False

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
        assert self._assertSameParentDirtyFirst(requirement, parentOriginURL), \
            "Traverse order must visit dirty requirements first"
        dirt = self._dirt[parentOriginURL]
        return dirt.get(requirement['originURL'], requirement['hash'])

    def _assertSameParentDirtyFirst(self, requirement, parentOriginURL):
        if parentOriginURL != self._sameParentDirtyFirstAssertion_parentOriginUrl:
            self._sameParentDirtyFirstAssertion_parentOriginUrl = parentOriginURL
            self._sameParentDirtyFirstAssertion_nonDirtyRequirementSpotted = False
        dirt = self._dirt[parentOriginURL]
        if requirement['originURL'] in dirt:
            return not self._sameParentDirtyFirstAssertion_nonDirtyRequirementSpotted
        else:
            self._sameParentDirtyFirstAssertion_nonDirtyRequirementSpotted = True
            return True
