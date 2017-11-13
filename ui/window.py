import maya.cmds as cmds

class Window():
    def __init__(self, app):
        self._app = app
        self.name = self.app.name
        self._selectedScene = dict((instance, False) for instance in self.app.get())
        self.popupItem = ('Add...', 'Remove')

    def create(self):
        self.windowUI = cmds.window(t=self.name)
        treeLayout = cmds.columnLayout(adjustableColumn=True)
        self._dockDC = cmds.dockControl(l=self.name, con=self.windowUI, a='right', aa=['left', 'right'], r=1, vis=1)
        blockHeight = cmds.dockControl(self._dockDC, q=1, h=1) - 195

        width = 280
        heigth = blockHeight

        menuBarLayout = cmds.menuBarLayout(p=treeLayout)
        cmds.menu(l="File", p=menuBarLayout)
        cmds.menuItem(l="Change project", c=lambda x: self.change_project())
        #cmds.menuItem(l="Cache", c=lambda x: self.app.cache())
        #cmds.menuItem(l="Update", c=lambda x: self.app.update())
        cmds.menuItem(l="Exit", c=lambda x: self.app.exit())
        cmds.menu(l="Help", hm=1, p=menuBarLayout)
        cmds.menuItem(l="About", c=lambda x: self.app.create_help_window())
        cmds.menu(l="Display", p=menuBarLayout)
        self.menuShowLocked = cmds.menuItem(l="Show non-existent files for this process and area", c=lambda x: self.change_selected("showLocked", x), cb=self.app.showLocked)
        self.menuShowSelected = cmds.menuItem(l="Show selected", c=lambda x: self.show_selected())

        filterLayout = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, width/6), (2, width/2.9), (3, width/2.05)], p=treeLayout, w=width, cs=(2,1), bgc=(.25,.25,.25))
        cmds.textField(text="Search:", en=0, p=filterLayout, fn="boldLabelFont")
        self.textFilter = cmds.textFieldGrp(cat=(1, 'left', 0), p=filterLayout, tcc=lambda x: self.app.set_selected('Filter', x))
        self.typeMenu = cmds.optionMenu(p=filterLayout, cc=lambda x: self.change_selected('Types', x))
        popupTypes = cmds.popupMenu(p=self.typeMenu)
        cmds.menuItem(popupTypes, l=self.popupItem[0], c=lambda x: self.add_menu_types(x))
        cmds.menuItem(popupTypes, l=self.popupItem[1], c=lambda x: self.remove_menu_types(x))
        
        form = cmds.formLayout(p=treeLayout, w=width, h=heigth)
        self.treeView = cmds.treeView(nb=1, abr=True, arp=False, adr=False, enk=True)
        cmds.treeView(self.treeView, e=1, pc=(1, self.select), rpc=(1, self.select), sc=lambda x, y: "")
        cmds.treeView(self.treeView, e=1, elc=lambda old, new: "")
        cmds.formLayout(form, e=True, attachForm=(self.treeView, 'top', 2))
        cmds.formLayout(form, e=True, attachForm=(self.treeView, 'left', 2))
        cmds.formLayout(form, e=True, attachForm=(self.treeView, 'bottom', 2))
        cmds.formLayout(form, e=True, attachForm=(self.treeView, 'right', 2))
        #treeViewPopup = cmds.popupMenu(p=self.treeView)
        #cmds.menuItem(treeViewPopup, l='Show non-existent files for this process and area', c=lambda x: self.change_selected("showLocked", x), cb=self.app.showLocked)
        #cmds.menuItem(treeViewPopup, l='Show selected', c=lambda x: self.change_selected("showSelected", x), cb=self.app.showSelected)

        processLayout = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, width/4), (2, width/1.35)], p=treeLayout, w=width, cs=(2, 2), bgc=(.25,.25,.25))
        cmds.textField(text="Process:", en=0, p=processLayout, fn="boldLabelFont")
        self.processMenu = cmds.optionMenu(p=processLayout, cc=lambda x: self.change_selected('Process', x))
        popupProcess = cmds.popupMenu(p=self.processMenu)
        cmds.menuItem(popupProcess, l=self.popupItem[0], c=lambda x: self.add_menu_process(x))
        cmds.menuItem(popupProcess, l=self.popupItem[1], c=lambda x: self.remove_menu_process(x))

        areaLayout = cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, width/4), (2, width/4), (3, width/4), (4, width/4)], p=treeLayout, w=width, cs=(2, 2), bgc=(.25,.25,.25))
        cmds.textField(text="Load from:", en=0, p=areaLayout, fn="boldLabelFont")
        self.radioCol = cmds.radioCollection(p=areaLayout)
        for area in self.app.area: cmds.radioButton(l=area, onc=self.change_area_folder)

        pressetLayout = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, width/2), (2, width/4), (3, width/4.1)], p=treeLayout, w=width, cs=(2, 2))
        self.presetMenu = cmds.optionMenu(p=pressetLayout, cc=lambda x: self.load_preset(x))
        cmds.button(l="Save", bgc=(0, .25, 0), c=lambda x: self.save_preset())
        cmds.button(l="Delete", bgc=(0.25, 0.25, 0), c=lambda x: self.delete_preset())

        cmds.columnLayout(p=treeLayout)
        cmds.button(l="Done", w=width, bgc=(0,0.25,0.25), c=lambda x: self.app.callBack())
        self.cancelSelected = cmds.button(l="Cancel selected", w=width, c=lambda x: self.clear(), en=0)

    def create_help(self, pathToImage):
        self.windowHelp = cmds.window(t="Help", h=300)
        main = cmds.rowColumnLayout(numberOfColumns=1, bgc=(.25,.25,.25))
        img = cmds.columnLayout(p=main)
        cmds.image(image=pathToImage)
        text = cmds.columnLayout(p=main, co=("right",300))
        cmds.textField(tx="Developed by FSBand", en=0, p=text, w=300)
        cmds.showWindow()

    def select(self, item, state=1):
        if item in self.app.types:
            if cmds.treeView(self.treeView, i=(item, 1, ''), q=1, bst=1) == 'checkboxOff.png':
                cmds.treeView(self.treeView, e=1, i=(item, 1, 'checkboxOn.png'))
                for instance in self.app.get(self.app.selectedFilter,item):
                    if not instance.info[self.app.selectedArea][self.app.selectedProcess]: continue
                    if not cmds.treeView(self.treeView, q=1, i=(instance.name, 1, '')): continue
                    cmds.treeView(self.treeView, e=1, i=(instance.name, 1, 'checkboxOn.png'))
                    self.selectedScene[instance] = True
            else:
                cmds.treeView(self.treeView, e=1, i=(item, 1, 'checkboxOff.png'))
                for instance in self.app.get(self.app.selectedFilter,item):
                    if not instance.info[self.app.selectedArea][self.app.selectedProcess]: continue
                    if not cmds.treeView(self.treeView, q=1, i=(instance.name, 1, '')): continue
                    cmds.treeView(self.treeView, e=1, i=(instance.name, 1, 'checkboxOff.png'))
                    self.selectedScene[instance] = False
        else:
            for instance in self.selectedScene.keys():
                if instance.name == item: break
            parent = cmds.treeView(self.treeView, q=1, ip=instance.name, dl=1)
            if not self.selectedScene[instance]:
                cmds.treeView(self.treeView, e=1, i=(instance.name, 1, 'checkboxOn.png'))
                self.selectedScene[instance] = True
                cmds.treeView(self.treeView, e=1, i=(parent, 1, 'checkboxOn.png'))
            else:
                cmds.treeView(self.treeView, e=1, i=(instance.name, 1, 'checkboxOff.png'))
                self.selectedScene[instance] = False
                selected = [i for i in self.selectedScene.values() if i]
                if len(selected) < 1:
                    cmds.treeView(self.treeView, e=1, i=(parent, 1, 'checkboxOff.png'))

        self.check_selected()
           
    def update(self):
        if cmds.textFieldGrp(self.textFilter, q=1, tx=1) != self.app.selectedFilter:
            cmds.textFieldGrp(self.textFilter, e=1, tx=self.app.selectedFilter)

        def return_menu_items(optionMenu):
            elements = list()
            optionMenu = cmds.optionMenu(optionMenu, q=1, ill=True)
            if not optionMenu: return []
            for items in optionMenu:
                elements.append(cmds.menuItem(items, q=1, l=1))
            return elements

        def clear_menu_items(menu):
            optionMenu = cmds.optionMenu(menu, q=1, ill=True)
            if optionMenu: cmds.deleteUI(optionMenu)

        if cmds.menuItem(self.menuShowLocked, q=1, cb=1) != self.app.showLocked:
            cmds.menuItem(self.menuShowLocked, e=1, cb=self.app.showLocked)

        if cmds.menuItem(self.menuShowSelected, q=1, cb=1) != self.app.showSelected:
            cmds.menuItem(self.menuShowSelected, e=1, cb=self.app.showSelected)

        if return_menu_items(self.typeMenu) != self.app.types:
            clear_menu_items(self.typeMenu)
            for type in sorted((self.app.types+['all'])):
                cmds.menuItem(p=self.typeMenu, l=type)

        if return_menu_items(self.processMenu) != self.app.process:
            clear_menu_items(self.processMenu)
            for process in sorted(self.app.process): cmds.menuItem(p=self.processMenu, l=process)

        if return_menu_items(self.presetMenu) != self.app.preset.listPresets:
            clear_menu_items(self.presetMenu)
            for preset in sorted(self.app.preset.listPresets): cmds.menuItem(p=self.presetMenu, l=preset)

        if not self.app.selectedTypes in self.app.types: self.app.selectedTypes = "all"
        if not self.app.selectedProcess in self.app.process: self.app.selectedProcess = sorted(self.app.process)[0]
        if not self.app.selectedArea in self.app.area: self.app.selectedArea = sorted(self.app.area)[0]

        if cmds.optionMenu(self.typeMenu, q=1, v=1) != self.app.selectedTypes:
            cmds.optionMenu(self.typeMenu, e=1, v=self.app.selectedTypes)
        if self.app.process and cmds.optionMenu(self.processMenu, q=1, v=1) != self.app.selectedProcess:
            cmds.optionMenu(self.processMenu, e=1, v=self.app.selectedProcess)
        if cmds.optionMenu(self.presetMenu, q=1, v=1) != self.app.selectedPreset:
            cmds.optionMenu(self.presetMenu, e=1, v=self.app.selectedPreset)
        for child in cmds.radioCollection(self.radioCol, q=1, cia=1):
            if cmds.radioButton(child, q=1, l=1) == self.app.selectedArea:
                cmds.radioButton(child, e=1, sl=1)

        def updateTreeView(parent):
            listUnlocked = list()
            listSelected = list()
            intensity = .75

            cmds.treeView(self.treeView, e=1, addItem=[parent, ''])
            for instance in self.app.get(self.app.selectedFilter, parent):

                if not self.app.selectedProcess in instance.info[self.app.selectedArea].keys():
                    return [], []

                if self.selectedScene.get(instance):
                    if self.selectedScene[instance] and instance.info[self.app.selectedArea][self.app.selectedProcess]:
                        cmds.treeView(self.treeView, e=1, addItem=[instance.name, parent])
                        cmds.treeView(self.treeView, e=1, i=(instance.name, 1, 'checkboxOn.png'), tc=(instance.name, 0, intensity, 0))
                        listSelected.append(instance.name)
                        listUnlocked.append(instance.name)
                    else:
                        if self.app.showLocked:
                            cmds.treeView(self.treeView, e=1, addItem=[instance.name, parent])
                            cmds.treeView(self.treeView, e=1, i=(instance.name, 1, ''), tc=(instance.name, intensity, 0, 0))
                            self.selectedScene[instance] = False
                else:
                    if not self.app.showSelected and instance.info[self.app.selectedArea][self.app.selectedProcess]:
                        cmds.treeView(self.treeView, e=1, addItem=[instance.name, parent])
                        cmds.treeView(self.treeView, e=1, i=(instance.name, 1, 'checkboxOff.png'), tc=(instance.name, 0, intensity, 0))
                        listUnlocked.append(instance.name)
                    else:
                        if self.app.showLocked and not self.app.showSelected:
                            cmds.treeView(self.treeView, e=1, addItem=[instance.name, parent])
                            cmds.treeView(self.treeView, e=1, eb=(instance.name, 1, 0), tc=(instance.name, intensity, 0, 0))

            return listUnlocked, listSelected

        cmds.treeView(self.treeView, e=1, ra=1)
        if self.app.selectedTypes == 'all':
            for type in self.app.types:
                unlocked, selected = updateTreeView(type)
                if not len(unlocked): 
                    cmds.treeView(self.treeView, e=1, eb=(type, 1, 0), i=(type, 1, ''))
                    continue
                if len(selected)>0:
                    cmds.treeView(self.treeView, e=1, i=(type, 1, 'checkboxOn.png'))
                else:
                    cmds.treeView(self.treeView, e=1, i=(type, 1, 'checkboxOff.png'))
        else:
            unlocked, selected = updateTreeView(self.app.selectedTypes)
            if not len(unlocked): 
                cmds.treeView(self.treeView, e=1, eb=(self.app.selectedTypes, 1, 0), i=(self.app.selectedTypes, 1, ''))
                return
            if len(selected)>0:
                cmds.treeView(self.treeView, e=1, i=(self.app.selectedTypes, 1, 'checkboxOn.png'))
            else:
                cmds.treeView(self.treeView, e=1, i=(self.app.selectedTypes, 1, 'checkboxOff.png'))

        self.check_selected()

    def clear(self):
        self._selectedScene = dict((i, False) for i in self.app.get())
        cmds.menuItem(self.menuShowSelected, e=1, l="Show selected")
        self.app.showSelected = False
        if cmds.button(self.cancelSelected, q=1, en=1):
            cmds.button(self.cancelSelected, e=1, en=0)
        self.update()

    def check_selected(self):
        for value in self.selectedScene.values():
            if value:
                cmds.button(self.cancelSelected, e=1, en=1)
                return
        cmds.button(self.cancelSelected, e=1, en=0)

    def return_selected(self):
        result = list()
        for elements,values in self.selectedScene.items():
            if values: result.append(elements)
        return result

    def show_selected(self):
        if not self.app.showSelected:
            cmds.menuItem(self.menuShowSelected, e=1, l="Show all")
        else:
            cmds.menuItem(self.menuShowSelected, e=1, l="Show selected")
        self.app.set_showSelected()

    def change_selected(self, parameter, value):
        self.app.change("*")
        if parameter == "showLocked":
            self.app.set_showLocked(value)
            return
        self.app.set_selected(parameter, value)

    def change_area_folder(self, state):
        self.app.change("*")
        for radio in cmds.radioCollection(self.radioCol, q=1, cia=1):
            if cmds.radioButton(radio, q=1, sl=1):
                self.app.set_selected('Area', cmds.radioButton(radio, q=1, l=1))
                return

    def change_project(self):
        choice = cmds.confirmDialog(t="Change project", b=["princess", "beaver", "Cancel"], ds="Cancel", m="Select the object to which the switch:")
        if not choice == "Cancel":
            self.app.set_project(choice)
        self.clear()

    def add_menu_types(self, *args):
        from string import Template
        pattern = Template(self.app.path)
        rootDir = pattern.safe_substitute(project=self.app.project).split('${type}')[0]
        self.app.change("*")
        choice = cmds.fileDialog2(ds=1, fm=3, dir=rootDir)
        if not choice: return
        if choice[0] == rootDir: return
        if len(choice[0].split('\\')) != 7:
            raise Exception("Wrong directory, select folder of type asset. Example chars, props, objs.")
        item = choice[0].split('\\')[-1]
        if choice: self.app.types_append(item)
        self.clear()

    def remove_menu_types(self, *args):
        self.app.change("*")
        self.app.types_remove(str(self.app.selectedTypes))
        self.clear()

    def add_menu_process(self, *args):
        self.app.change("*")
        choice = cmds.promptDialog(t="Process", b=["Add", "Cancel"], db="Add", ds="Cancel", st="text", m="Type new process:")
        if choice == "Add":
            newProcess = cmds.promptDialog(q=1, tx=1)
            self.app.process_append(newProcess)
            self.clear()

    def remove_menu_process(self, *args):
        self.app.change("*")
        self.app.process_remove(str(self.app.selectedProcess))
        self.clear()

    def load_preset(self, item):
        for preset in self.app.preset.listPresets:
            if "*" in preset: self.app.preset.rename(preset, preset[:-1])
        if "*" in item: item = item[:-1]
        self.app.load_preset(item)
        
    def save_preset(self, *args):
        
        def dialog_for_create_preset():
            choice = cmds.promptDialog(t="Preset", b=["Save", "Cancel"], db="Save", ds="Cancel", st="text", m="Type new preset:", tx="new_preset")
            if choice == "Save":
                newPreset = cmds.promptDialog(q=1, tx=1)
                self.app.add_preset(newPreset)
            else: return

        if not "*" in self.app.selectedPreset: return
        if not "default" in self.app.selectedPreset:
            overwrite = cmds.confirmDialog(t="Overwrite", b=["Yes", "Create New"], db="Yes", ds="Create New", m="Overwrite {0}?".format(self.app.selectedPreset[:-1]))
            if not overwrite == "Yes":
                dialog_for_create_preset()
            else:
                self.app.save_preset(self.app.selectedPreset)
        else:
            dialog_for_create_preset()

    def delete_preset(self, *args):
        if self.app.selectedPreset == "default": return
        self.app.delete_preset(str(self.app.selectedPreset))
        self.clear()

    @property
    def app(self):
        return self._app
        
    @property
    def selectedScene(self):
        return self._selectedScene

    def destroy(self):
        cmds.deleteUI(self.windowUI)
        cmds.deleteUI(self._dockDC)

    def destroyHelp(self):
        cmds.deleteUI(self.windowHelp)