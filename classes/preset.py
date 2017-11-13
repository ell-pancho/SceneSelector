import os
import json
import copy

class Preset():
    def __init__(self, app):
        self._app = app
        self._listPresets = ["default"]

        self._homeDir = os.path.join(os.path.expandvars("%home%"), "AssetSelector")
        if not os.path.exists(self._homeDir): os.mkdir(self._homeDir)
        self._homeDir = os.path.join(self._homeDir, "presets")
        if not os.path.exists(self._homeDir): os.mkdir(self._homeDir)
        self._homeDir = os.path.join(self._homeDir, self.app.context)
        if not os.path.exists(self._homeDir): os.mkdir(self._homeDir)

        for presets in os.listdir(self._homeDir):
            if not '.json' in presets: continue
            namePreset = os.path.splitext(presets)[0]
            self._listPresets.append(namePreset)
    
    def load(self, loadName):
        if loadName == "default":
            for key, values in self.app.defaultConfig.items():
                if not hasattr(self.app, key): setattr(self.app, key, None)
                setattr(self.app, key, copy.deepcopy(values))
            return
        path = self.build_path(loadName)
        if not os.path.exists(path):
            raise Exception("{0}-preset not exists".format(loadName))
        with open(path, 'r') as presetFile:
            info = dict(json.loads(presetFile.read()))
        for key, values in info.items():
            if not hasattr(self.app, key): setattr(self.app, key, None)
            setattr(self.app, key, values)

    def delete(self, deleteName):
        if deleteName == "default": return
        path = self.build_path(deleteName)
        if not os.path.exists(path):
            raise Exception("{0}-preset not exists".format(deleteName))
        self.listPresets.remove(deleteName)
        os.remove(path)
    
    def add(self, newPreset):
        version = len([i for i in self.listPresets if newPreset in i])
        name = "{0}0{1}".format(newPreset, version) if version else newPreset
        self.listPresets.append(name)
        self.save(name)
        return name

    def save(self, saveName):
        newPreset = dict()
        for key in sorted(self.app.defaultConfig.keys()):
            newPreset[key] = getattr(self.app, key)
        path = self.build_path(saveName)
        with open(path, 'w') as presetFile:
            json.dump(newPreset, presetFile, sort_keys=True, indent=2)

    def rename(self, oldName, newName):
        index = self.listPresets.index(oldName)
        self.listPresets[index] = newName

    def build_path(self, name):
        return os.path.join(self.homeDir, '{0}.json'.format(name))

    @property
    def listPresets(self):
        return self._listPresets
    
    @property
    def homeDir(self):
        return self._homeDir

    @property
    def app(self):
        return self._app