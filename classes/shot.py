import copy

class Shot():
    def __init__(self, project, type, sq, sh, root, area, process):
        self._type = copy.deepcopy(type)
        self._sq = copy.deepcopy(sq)
        self._sh = copy.deepcopy(sh)
        self._root = copy.deepcopy(root)
        self._area = copy.deepcopy(area)
        self._process = copy.deepcopy(process)
        self._project = copy.deepcopy(project)
        self._name = "{0.type}_{0.sq}_{0.sh}".format(self)
        self._info = self.init()

    def init(self):
        import re
        import os

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
                        if not process == "---":
                            pattern = ''.join([
                                                '{type}',
                                                '_{sq}',
                                                '_{sh}',
                                                '(_{process}|\B)',
                                                '(_v[0-9]*|)',
                                                '.ma',
                                                '$'
                                            ])
                        else:
                            pattern = ''.join([
                                                '{type}',
                                                '_{sq}',
                                                '_{sh}',
                                                '(_v[0-9]*|)',
                                                '.ma',
                                                '$'
                                            ])
                        if re.match(pattern.format(type=self.type, sq=self.sq, sh=self.sh, process=process), item):
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
    def sq(self):
        return self._sq

    @property
    def sh(self):
        return self._sh

    @property
    def area(self):
        return self._area
    
    @property
    def process(self):
        return self._process

    @property
    def info(self):
        return self._info