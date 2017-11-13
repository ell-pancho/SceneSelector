import os
import re
import cPickle as pickle
import time
from functools import wraps
import ui
import ui.window
import classes.preset as preset
import db
import threading
reload(preset)
reload(ui.window)
reload(db)

class SceneSelectorApp():

    defaultConfigAsset = {
        "path": "\\\\ALPHA\\prj\\${project}\\assets\\${type}\\${name}\\maya",
        "types":   ["chars", "locs", "objs", "props", "sets"],
        "area":    ["root", "versions", "publish"],
        "process": ["proxy", "rig", "model", "uv", "shade"],
        "selectedArea":    "root",
        "selectedProcess": "model",
        "selectedTypes":   "all",
        "showLocked":      True,
                    }

    defaultConfigShot = {
        "path": "\\\\ALPHA\\prj\\${project}\\prod\\${type}\\${sq}\\${name}",
        "types": [],
        "area": ["root", "polish", "postanim"],
        "process": ["---", "polish", "postanim", "camx"],
        "selectedArea": "root",
        "selectedProcess": "---",
        "selectedTypes": "all",
        "showLocked": True,
                    }

    def updateUI(func):
        @wraps(func)
        def decorateUI(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.window.update()
        return decorateUI

    @updateUI
    def __init__(self, callBack, project, context):
        self.name = "{0}Selector".format(context.title())
        self.callBack = callBack
        self.condition = True
        self._project = project
        self._context = context
        self._pathToScript = os.path.split(os.path.realpath(__file__))[0]
        self._selectedFilter = ""
        self._selectedPreset = "default"
        self._showSelected = False

        if context == "asset": self.defaultConfig = self.defaultConfigAsset
        elif context == "shot":
            self.generic_shot_types()
            self.defaultConfig = self.defaultConfigShot
        else:
            raise Exception("{0}-context not exists".format(self.context))

        self._homeDir = os.path.join(os.path.expandvars("%home%"), "AssetSelector")
        if not os.path.exists(self._homeDir): os.mkdir(self._homeDir)
        self._homeDir = os.path.join(self._homeDir, "database")
        if not os.path.exists(self._homeDir): os.mkdir(self._homeDir)
        self._homeDir = os.path.join(self._homeDir, self.context)
        if not os.path.exists(self._homeDir): os.mkdir(self._homeDir)
        
        self._preset = preset.Preset(self)
        self.preset.load(self.selectedPreset)

        self._db = db.DataBase()
        if not self.load_db(self.project):
            self.db.init(self.project, self.context, self.defaultConfig)
            self.dump_db()

        self.create_window()

        self._threadCheck = threading.Thread(target=self.check_db)
        self.start_thread()

    def create_window(self):
        self._window = ui.window.Window(self)
        self.window.create()

    def create_help_window(self):
        pathToImage = os.path.join(self.pathToScript, "images", "help.png")
        try: self.app.exitHelp()
        except: pass
        self.window.create_help(pathToImage)

    def return_selected(self):
        """ Return selected in window """
        windowReturned = self.window.return_selected()
        selected = dict((instance.name, instance.info[self.selectedArea][self.selectedProcess]) for instance in windowReturned)
        return selected

    def start_thread(self):
        self.threadCheck.start()

    def stop_thread(self):
        self.condition = False

    @updateUI
    def set_selected(self, param, newPick):
        try:
            setattr(self, 'selected' + param, newPick)
        except:
            raise Exception("Not found selected{0}".format(param))

    @updateUI
    def set_showLocked(self, *args):
        """ This method change display locked asset in tree view. """
        self.showLocked = False if self.showLocked else True

    @updateUI
    def set_showSelected(self, *args):
        """ This method change display selected asset in tree view. """
        self.showSelected = False if self.showSelected else True

    def change(self, postfix):
        if not "*" in self.selectedPreset:
            changeName = "{0}{1}".format(self.selectedPreset, postfix)
            self.preset.rename(self.selectedPreset, changeName)
            self.selectedPreset = changeName

    def save_preset(self, newPreset):
        if "*" in newPreset:
            self.preset.rename(newPreset, newPreset[:-1])
            newPreset = newPreset[:-1]
        self.preset.save(newPreset)
        self.set_selected('Preset', newPreset)

    def add_preset(self, addPreset):
        self.preset.rename(self.selectedPreset, self.selectedPreset[:-1])
        newName = self.preset.add(addPreset)
        self.set_selected('Preset', newName)

    def load_preset(self, loadPreset):
        self.preset.load(loadPreset)
        self.set_selected('Preset', loadPreset)

    def delete_preset(self, deletePreset):
        if "*" in deletePreset:
            self.preset.rename(self.selectedPreset, self.selectedPreset[:-1])
            deletePreset = deletePreset[:-1]
        self.preset.delete(deletePreset)
        self.preset.load("default")
        self.set_selected('Preset', "default")

    def process_append(self, newProcess):
        if newProcess in self.process:
            raise Exception("{0} already exists in process-list".format(newProcess))
        self.process.append(newProcess)
        self.set_selected("Process", newProcess)

    def process_remove(self, removeProcess):
        if len(self.process) == 1:
            raise Exception("It must be at least one process.")
        self.process.remove(removeProcess)
        self.set_selected("Process", sorted(self.process)[0])

    def generic_shot_types(self):
        pattern = "^ep[0-9]{2,}$"
        defaultPath = self.defaultConfigShot["path"]
        defaultPath = defaultPath[:defaultPath.find("${type}")-1]
        pathToEp = "\\\\ALPHA\\prj\\{0.project}\\prod\\".format(self)
        listEp = sorted([ep for ep in os.listdir(pathToEp) if "ep" in ep if re.match(pattern, ep)])
        self.defaultConfigShot["types"] = listEp

    def types_append(self, newTypes):
        if newTypes in self.types: return
        self.types.append(newTypes)
        self.types = sorted(self.types)
        self.set_selected("Types", newTypes)

    def types_remove(self, removeTypes):
        if removeTypes == "all":
            raise Exception("Can not delete all-types.")
        if type(removeTypes) != type(str()):
            raise Exception("Remove types is not a string.")
        self.types.remove(removeTypes)
        if removeTypes == self.selectedTypes:
            self.set_selected('types', 'all')

    def dump_db(self):
        with open('{0.homeDir}\\{0.project}.pkl'.format(self), 'wb') as output:
            pickle.dump(self.db, output, 2)

    def check_db(self):
        path = '{0.homeDir}\\{1}.pkl'.format(self, self.project)
        while self.condition:
            createTime = os.path.getmtime(path)
            currentTime = time.time()
            passedTime = round((currentTime - createTime)/60/60, 1)
            if passedTime >= 2: self.update()
            time.sleep(60)

    def load_db(self, nameDB):
        path = '{0.homeDir}\\{1}.pkl'.format(self, nameDB)
        if not os.path.exists(path):
            return False
        with open(path, 'rb') as output:
            self.db = pickle.load(output)
            if self.context == "shot":
                self.generic_shot_types()
                self.defaultConfig = self.defaultConfigShot
            self.preset.load("default")
            return True

    def get(self, name="", type=""):
        return self.db.get(name, type)

    def update(self):
        self.db.update()
        self.dump_db()

    @updateUI
    def set_project(self, newProject):
        """ Set new project, update database. Example: app.set_project(name_newProject) --> app.projet = name_newProject."""
        if newProject == self.project:
            raise Exception("Already in {0}-project".format(newProject))
        self.project = newProject
        if not self.load_db(self.project):
            if self.context == "shot":
                self.generic_shot_types()
                self.defaultConfig = self.defaultConfigShot
            self.preset.load("default")
            self.db.init(self.project, self.context, self.defaultConfig)
            self.dump_db()
        
    @property
    def selectedFilter(self):
        return self._selectedFilter
    
    @property
    def selectedTypes(self):
        return self._selectedTypes

    @property
    def selectedProcess(self):
        return self._selectedProcess

    @property
    def selectedArea(self):
        return self._selectedArea

    @property
    def showLocked(self):
        return self._showLocked

    @property
    def showSelected(self):
        return self._showSelected

    @property
    def selectedPreset(self):
        return self._selectedPreset

    @property
    def path(self):
        return self._path

    @property
    def project(self):
        return self._project

    @property
    def context(self):
        return self._context

    @property
    def types(self):
        return self._types

    @property
    def process(self):
        return self._process

    @property
    def area(self):
        return self._area

    @property
    def pathToScript(self):
        return self._pathToScript

    @property
    def preset(self):
        return self._preset
    
    @property
    def db(self):
        return self._db

    @property
    def homeDir(self):
        return self._homeDir

    @property
    def window(self):
        return self._window

    @property
    def threadCheck(self):
        return self._threadCheck
    
    def exitHelp(self):
        try: self.window.destroyHelp()
        except: pass

    def exit(self):
        try: self.window.destroy()
        except: pass
        self.stop_thread()