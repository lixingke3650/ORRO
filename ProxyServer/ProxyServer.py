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

# IP
SERVER_IP = '127.0.0.1'
# 端口
LISTENPORT = 5010
# 最大连接数
CONNECT_MAXNUMBER = 1024
# 超时
CONNECT_TIMEOUT = 10
# 最大读取字节数
RECV_MAXSIZE = 65535


class H_C_ProxyServer():
	"""docstring for ProxyServer"""

	_isRun = False
	_ProxyServerThread = None
	_ProxyServerWorks = []
	_WorkerThreadRLock = None

	# obj _ self _ other
	_Address_Local_Compurte = None
	_Ip_Loacl_Compurte = None
	_Port_Local_Compurte = None
	_Socket_Local_Compurte = None

	_Address_Compurte_Local = None
	_Socket_Compurte_Local = None

	def __init__( self, ip='127.0.0.1', port=5010 ):
		self._Ip_Loacl_Compurte = ip
		self._Port_Local_Compurte = port
		self._Address_Local_Compurte = ( self._Ip_Loacl_Compurte, self._Port_Local_Compurte )
		self._WorkerThreadRLock = threading.RLock()
		
	def start( self ):
		try:
			self._Socket_Local_Compurte = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self._Socket_Local_Compurte.bind( self._Address_Local_Compurte )
			self._Socket_Local_Compurte.listen( CONNECT_MAXNUMBER )

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
				self._ProxyServerThread.jion(10)
				return True
				
			except:
				return False

	def generator( self ):
		'''proxyworker generator(socket.accept)'''

		while( self._isRun == True ):
			try:
				self._Socket_Compurte_Local, self._Address_Compurte_Local = self._Socket_Local_Compurte.accept()
				proxyserverworker = ProxyServerWorker.ProxyServerWorker( self._Socket_Compurte_Local, self.proxyserverworksmanager )
				workerthread = threading.Thread( target = proxyserverworker.start )
				workerthread.start()

			except:
				pass

	def proxyserverworksmanager( self, oper, worker ):
		'''proxyworks add and del'''
		# thread lock
		self._WorkerThreadRLock.acquire()

		try:
			if( cmp( oper, 'add') == 0 ):
				self._ProxyServerWorks.append( worker )
			elif( cmp( oper, 'del' ) == 0 ):
				self._ProxyServerWorks.remove( worker )
		except:
			G_Log.error( 'ProxyServerWorks add or del error! [ProxyServer.py:H_C_ProxyServer:proxyserverworksmanager]' )
			pass

		# thread unlock
		self._WorkerThreadRLock.release()