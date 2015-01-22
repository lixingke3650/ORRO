# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: HttpsProxy.py

class HttpsProxy(object):
	"""docstring for HttpsProxy"""
	
	_WorkerManagerLocalComputer = None

	_Local_Remote_Address = None
	_Socket_Local_Computer = None
	_Socket_Local_Remote = None
	_FirstHeadStr_Computer_Local = None
	_FirstHeadDict_Computer_Local = None

	_ProcessLtoR = None
	_ProcessRtoL = None

	_Keep_Alive = None
	_Keep_Alive_LC = None
	_Keep_Alive_LR = None
	_IsWorker = None

	def __init__( self, socklc, headstr, workermanager ):
		self._Socket_Local_Computer = socklc
		self._FirstHeadStr_Computer_Local = headstr
		self._WorkerManagerLocalComputer = workermanager
		self._IsWorker = False

	def start( self ):
		print( self._FirstHeadStr_Computer_Local )
		return
		# worker add
		try:
			self._WorkerManagerLocalComputer.workadd()
			self._IsWorker = True
		except Exception as e:
			self._IsWorker = False
			G_Log.error( 'Worker add error! [HttpProxy.py:HttpProxy:start] --> %s' %e )
			return
		try:
			# Fir Head Format
			self._FirstHeadDict_Computer_Local = Tool.HttpHead.HttpHead( self._FirstHeadStr_Computer_Local )
			# ORRO Server Connect
			self._Socket_Local_Remote = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self._Local_Remote_Address = ( globals.G_ORRO_R_HOST, globals.G_ORRO_R_PORT )
			self._Socket_Local_Remote.connect_ex( self._Local_Remote_Address )

		except Exception as e:
			self._WorkerManagerLocalComputer.workdel()
			G_Log.error( 'socket connect error! [HttpProxy.py:HttpProxy:start] --> %s' %e )
			return