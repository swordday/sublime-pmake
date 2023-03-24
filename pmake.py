import sublime
import sublime_plugin
import subprocess
import os
import re
import time

# References
#
# - http://feliving.github.io/Sublime-Text-3-Documentation/api_reference.html
# 

# the xmake plugin
class PmakePlugin(object):

	# initializer
	def __init__(self):

		# init xmake
		self.pmake = None

		# init panels
		self.panels = {}

		# init default target
		self.target = "default"

		# init current project directory
		self.projectdir = None

		# init build output level
		self.build_output_level = "warning"

	def update_status(self):
		if not self.is_enabled():
			sublime.error_message("Sorry!\nThe Premake plugin needs a project and a premake file to be used.\n")
			self._print_help()
			return

	def is_enable(self):
		return self._get_project_folder() is not None and os.path.exists(self._get_premake_filepath())

	def _get_project_folder(self):
		folders = self.window.folders()
		if len(folders) == 0:
			return None
		return folder[0]	

	def _get_project_file(self):
		"""Get the name of the project file in the current project."""
		filesList = os.listdir(self._get_project_folder())
		projFileFound = False
		for projFile in filesList:
			if projFile[-16:] == ".sublime-project":
				projFileFound = True
				break

		if projFileFound:
			return projFile
		return None

	def _get_project_setting(self, name):
		"""Get a value from the project configuration file."""
		projFile = self._get_project_file()
		if not projFile:
			return None

		projFilePath = os.path.join(self._get_project_folder(), projFile)
		projFileDesc = open(projFilePath, 'r')
		projJson = json.load(projFileDesc)
		projFileDesc.close()

		if 'settings' not in projJson:
			return None
		if name not in projJson['settings']:
			return None
		return projJson['settings'][name]

	def _get_project_file(self):
		"""Get the name of the project file in the current project."""
		filesList = os.listdir(self._get_project_folder())
		projFileFound = False
		for projFile in filesList:
			if projFile[-16:] == ".sublime-project":
				projFileFound = True
				break

		if projFileFound:
			return projFile
		return None

	def _get_premake_filepath(self):
		"""Find the absolute path to the premake build file (not guaranteed to exist)."""
		premakeFile = None

		# Attempt to load it from the project file.
		premakeFile = self._get_project_setting("premake_file")

		# If we don't have it yet, we load it from the default file.
		if not premakeFile:
			premakeSettings = sublime.load_settings("pmake.sublime-settings")
			premakeFile = premakeSettings.get("premake_file")

		# The name should be defined here, otherwise the default config is screwed.
		if not premakeFile:
			raise RuntimeError("Unable to get 'premake_file' from the settings.")

		# Convert the path to an absolute path, if necessary.
		if not os.path.isabs(premakeFile):
			premakeFile = os.path.abspath(os.path.join(self._get_project_folder(), premakeFile))

		return premakeFile

	# get pmake program
	def get_pmake(self):

		# for windows? return xmake directly
		if sublime.platform() == "windows":
			self.pmake = "pmake"

		# attempt to get xmake program
		if not self.xmake:
			programs = ["pmake", os.path.join(os.getenv("HOME"), ".local/bin/pmake"), "/usr/local/bin/pmake", "/usr/bin/pmake"]
			for program in programs:
				if program == "pmake" or os.path.isfile(program):
					result = subprocess.Popen(program + " --version", stdout = subprocess.PIPE, shell = True).communicate()
					if result and len(result[0]) > 0:
						self.xmake = program
						break
		
		# ok?
		return self.xmake
		
# define plugin
global plugin
plugin = PmakePlugin()

# plugin loaded
def plugin_loaded():
	plugin.update_status()
