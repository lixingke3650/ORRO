# !usr/bin/python
# -*-coding: utf-8-*-
# Filename: Config.py

import json
# import ConfigParser
import configparser

class ConfigJson():
	'''json配置文件处理'''

	_JsonHandle = None

	def __init__(self, filepath):
		fp = open(filepath)
		self._JsonHandle = json.load(fp)
		fp.close()

	def getKey(self, *keys):
		'''返回键值，可变参数，可指定多层'''

		if (keys == None):
			return self._JsonHandle

		try:
			json = self._JsonHandle
			for key in keys:
				json = self.jsonelemiter(json, key)
			return json
		except:
			return None

	def jsonelemiter(self, json, key):
		return json[key]

class ConfigIni():
	'''INI配置文件处理'''

	_IniHandle = None

	def __init__(self, filepath):
		fp = open(filepath)
		# self._IniHandle = ConfigParser.ConfigParser()
		self._IniHandle = configparser.ConfigParser()
		# self._IniHandle.read(filepath)
		self._IniHandle.readfp(fp)
		fp.close()

	def getKey(self, section, option):
		try:
			return (self._IniHandle.get(section, option))
		except:
			return None

	def getKeyInt(self, section, option):
		try:
			return (self._IniHandle.getint(section, option))
		except:
			return None

	def getKeyFloat(self, section, option):
		try:
			return (self._IniHandle.getfloat(section, option))
		except:
			return None

	def getKeyBool(self, section, option):
		try:
			return (self._IniHandle.getboolean(section, option))
		except:
			return None
