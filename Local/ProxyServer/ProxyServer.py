# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: ProxyServer.py

import sys
import socket
import threading

sys.path.append('..')
# from globals import G_Log
import ProxyServerWorker
import Tool.Logger
from globals import G_Log

# 超时
CONNECT_TIMEOUT = 10

class H_C_ProxyServer():
	"""docstring for ProxyServer"""

	_isRun = False
	_ProxyServerThread = None
	_ProxyServerWorks = []
	_WorkerThreadRLock = None

	# obj _ self _ other
	_Address_Local_Server = None
	_Ip_Loacl_Server = None
	_Port_Local_Server = None
	_Connect_Maximum = None
	_Socket_Local_Server = None

	_Address_Local_Computer = None
	_Socket_Local_Computer = None

	def __init__( self, ip='127.0.0.1', port=0, maximum=1024 ):
		self._Ip_Loacl_Server = ip
		self._Port_Local_Server = port
		self._Connect_Maximum = maximum
		self._Address_Local_Server = ( self._Ip_Loacl_Server, self._Port_Local_Server )
		self._WorkerThreadRLock = threading.RLock()
		
	def start( self ):
		'''ProxyServer Start.

		   socket create/bind/listen.'''

		try:
			self._Socket_Local_Server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self._Socket_Local_Server.bind( self._Address_Local_Server )
			self._Socket_Local_Server.listen( self._Connect_Maximum )

		except:
			G_Log.error( 'socket start error! [ProxyServer.py:H_C_ProxyServer:start]' )
			self._isRun = False
			return False

		self._isRun = True
		self._ProxyServerThread = threading.Thread( target = self.generator )
		self._ProxyServerThread.start()
		return True

	def stop( self ):
		if( self._ProxyServerThread == None ):
			return True
		else:
			self._isRun = False
			try:
				self._ProxyServerThread.jion(CONNECT_TIMEOUT)
				return True
				
			except:
				return False

	def generator( self ):
		'''proxyworker generator(socket.accept).'''

		while( self._isRun == True ):
			try:
				self._Socket_Local_Computer, self._Address_Local_Computer = self._Socket_Local_Server.accept()
				proxyserverworker = ProxyServerWorker.ProxyServerWorker( self._Socket_Local_Computer, self.proxyserverworksmanager )
				workerthread = threading.Thread( target = proxyserverworker.start )
				workerthread.start()

			except:
				G_Log.error( 'workerthread generator error! [ProxyServer.py:H_C_ProxyServer:generator]' )
				# pass

	def proxyserverworksmanager( self, oper, worker ):
		'''proxyworks add and del.'''

		# 返回值，当前work总数
		ret = 0

		# thread lock
		self._WorkerThreadRLock.acquire()

		try:
			if( cmp( oper, 'add') == 0 ):
				self._ProxyServerWorks.append( worker )
			elif( cmp( oper, 'del' ) == 0 ):
				self._ProxyServerWorks.remove( worker )

			ret = len( self._ProxyServerWorks )
		except:
			G_Log.error( 'ProxyServerWorks add or del error! [ProxyServer.py:H_C_ProxyServer:proxyserverworksmanager]' )

		# thread unlock
		self._WorkerThreadRLock.release()

		# 返回当前work总数
		return ret;
