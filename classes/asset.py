import copy

class Asset():
    def __init__(self, project, name, type, root, area, process):
        self._name = copy.deepcopy(name)
        self._type = copy.deepcopy(type)
        self._root = copy.deepcopy(root)
        self._area = copy.deepcopy(area)
        self._process = copy.deepcopy(process)
        self._project = copy.deepcopy(project)
        self._info = self.init()

    def init(self):
        import re
        import os
        pattern = ''.join([
            '{name}',
            '(_[a-zA-Z0-9]*|\B)',
            '(_r_[a-zA-Z0-9]*|\B)',
            '_{process}',
            '(_v[0-9]*|)',
            '.ma',
            '$'
        ])
        info = dict()
        for folder in self.area:
            listProcess = dict()
            for process in self.process:
                if folder == "root": localPath = '{0.root}'.format(self)
                else: localPath = '{0.root}\\{1}'.format(self, folder)
                if not os.path.isdir(localPath):
                    listProcess[process] = []
                else:
                    listVersion = list()
                    for item in os.listdir(localPath):
                        if re.match(pattern.format(name=self.name, process=process), item):
                            listVersion.append('{0}\\{1}'.format(localPath, item))
                    listProcess[process] = sorted(listVersion)
            info[folder] = listProcess

        return info

    @property
    def project(self):
        return self._project
    
    @property
    def name(self):
        return self._name

    @property
    def root(self):
        return self._root

    @property
    def type(self):
        return self._type

    @property
    def area(self):
        return self._area
    
    @property
    def process(self):
        return self._process

    @property
    def info(self):
        return self._info