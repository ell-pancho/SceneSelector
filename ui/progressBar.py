import maya.cmds as cmds
import maya.mel as mel
from maya.utils import executeInMainThreadWithResult as exIMT

class ProgressBar():
	def __init__(self):
		self._progress_bar = mel.eval('$tmp = $gMainProgressBar')

	def start(self):
		exIMT(cmds.progressBar, self.progress_bar, edit=1, beginProgress=1)

	def stop(self):
		exIMT(cmds.progressBar, self.progress_bar, edit=1, endProgress=1)

	def run(self, maxValue, status=""):
		exIMT(cmds.progressBar, self.progress_bar, maxValue=maxValue, st=status, edit=1, step=1)

	@property
	def progress_bar(self):
	    return self._progress_bar