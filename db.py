import os
import copy
import classes.asset as asset
import classes.shot as shot
import ui.progressBar
reload(ui.progressBar)
reload(asset)
reload(shot)

class DataBase():
    def __init__(self):
        self._db = dict()
        self.progressBar = ui.progressBar.ProgressBar()

    def init(self, project, context, config):
        self.project = copy.deepcopy(project)
        self.context = copy.deepcopy(context)
        self.path = copy.deepcopy(config['path'])
        self.types = copy.deepcopy(config['types'])
        self.area = copy.deepcopy(config['area'])
        self.process = copy.deepcopy(config['process'])
        self.update()

    def error(self, name):
        self.progressBar.run(maxValue, "Error")
        self.progressBar.stop()
        raise Exception("{0}-not exists".format(name))

    def update(self):
        from string import Template
        import time

        beginTime = time.time()
        pattern = Template(self.path)

        if self.context == "asset":

            projectPath = pattern.safe_substitute(project=self.project).split("\\assets")[0]
            if not os.path.exists(projectPath):
                raise Exception("{0} folder not exists".format(projectPath))

            self.clear()
            self.progressBar.start()
            maxValue = len(self.types)+1

            for type in self.types:
                self.progressBar.run(maxValue, 'Load {0}-folder'.format(type))
                typeRoot = pattern.safe_substitute(project=self.project, type=type).split('${name}')[0]
                if not os.path.isdir(typeRoot): self.error(type)
                for name in os.listdir(typeRoot):
                    assetRoot = pattern.safe_substitute(project=self.project, type=type, name=name)
                    if os.path.isdir(assetRoot):
                        self.db[name] = asset.Asset(self.project, name, type, assetRoot, self.area, self.process)          
            
            self.progressBar.run(maxValue, "Complete")
            self.progressBar.stop()

        elif self.context == "shot":

            projectPath = pattern.safe_substitute(project=self.project).split("\\prod")[0]
            if not os.path.exists(projectPath):
                raise Exception("{0} folder not exists".format(projectPath))

            self.clear()
            self.progressBar.start()
            maxValue = len(self.types)+1

            for type in self.types:
                self.progressBar.run(maxValue, 'Load {0}-folder'.format(type))
                sqPath = pattern.safe_substitute(project=self.project, type=type).split('${sq}')[0]
                for sq in os.listdir(sqPath):
                    if not "sq" in sq: continue
                    typeRoot = pattern.safe_substitute(project=self.project, type=type, sq=sq).split('${name}')[0]
                    if not os.path.isdir(typeRoot): self.error(sq)
                    for sh in os.listdir(typeRoot):
                        if not "sh" in sh: continue
                        assetRoot = pattern.safe_substitute(project=self.project, type=type, sq=sq, name=sh)
                        if not os.path.isdir(assetRoot): self.error(sh)
                        if os.path.isdir(assetRoot):
                            newName = "{0}_{1}_{2}".format(type, sq, sh)
                            self.db[newName] = shot.Shot(self.project, type, sq, sh, assetRoot, self.area, self.process)          
            
            self.progressBar.run(maxValue, "Complete")
            self.progressBar.stop()

        else: self.error(self.context)

        endTime = time.time()
        updateTime = endTime - beginTime
        print "Database updated in {0} sec.".format(round(updateTime, 2))

    def get(self, filterByName="", filterByType=""):
        result = dict()

        def smart_filter(name, string):
            splitName = name
            trustCoeff = 1
            for i in xrange(0, len(string), 1):
                char = string[i]
                position = splitName.find(char)
                if position != -1: splitName = splitName[position+1:]
                else: return 0
                if position != 0: trustCoeff += position+1
                else: trustCoeff += 1
            trustCoeff = float((len(string)+1))/float(trustCoeff)
            return trustCoeff

        def sorted_by_propability(sort):
            final = list()
            for i in sorted(sort.keys(), reverse=True):
                for j in sorted(sort[i].keys()):
                    final.append(sort[i][j])
            return final

        for names, instance in self.db.items():
            if not smart_filter(instance.type, filterByType): continue
            trust = smart_filter(names, filterByName)
            if not trust: continue
            listInstance = dict()
            if result.get(trust):
                result[trust][names] = instance
            else:
                listInstance[names] = instance
                result[trust] = listInstance

        return sorted_by_propability(result)

    def clear(self):
        self.db = dict()

    @property
    def db(self):
        return self._db