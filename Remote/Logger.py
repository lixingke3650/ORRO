# !usr/bin/python
# -*- coding: utf-8 -*-
# Filename: logger.py

# log level:
# logging.CRITICAL # 50
# logging.ERROR    # 40
# logging.WARN     # 30
# logging.WARNING  # 30
# logging.INFO     # 20
# logging.DEBUG    # 10
# logging.NOTSET   # 0

import logging

LOG_OBJ_NAME = 'ORRO_R'
LOG_OBJ_FILENAME = 'Orro_R.log'

_G_Logger = None


class OrroLog(object):
	_Logger = None
	_LogHandler = None
	_LogFormat = None

	def __init__(self):
		# logger实例获取
		self._Logger = logging.getLogger(LOG_OBJ_NAME)
		# 指定logger控制器
		self._LogHandler = logging.FileHandler(filename=LOG_OBJ_FILENAME)
		# 设置log格式
		self._LogFormat = logging.Formatter('%(levelname)-9s %(asctime)s    %(message)s')
		# 格式信息加载到控制器上
		self._LogHandler.setFormatter(self._LogFormat)
		# 激活控制器信息
		self._Logger.addHandler(self._LogHandler)
		# 设置log级别
		self._Logger.setLevel(logging.DEBUG)

	def debug(self, msg):
		self._Logger.debug(msg)

	def info(self, msg):
		self._Logger.info(msg)

	def warn(self, msg):
		self._Logger.warn(msg)

	def error(self, msg):
		self._Logger.error(msg)

	def critical(self, msg):
		self._Logger.critical(mag)


def getLogger():
	global _G_Logger
	if( _G_Logger == None ):
		_G_Logger  = OrroLog()

	return _G_Logger

# if __name__ == "__main__":
# 	getLogger()
# 	_Logger.debug("hello")