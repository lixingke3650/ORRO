# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: ProxyServerWorker.py

import sys

sys.path.append('..')
import Http.HttpProxy
import Https.HttpsProxy
import Tool.HttpHead
import Tool.Logger
import ProxyServerWorker
from globals import G_Log


# 端口
REMOTE_PORT = 80
# 最大连接数
CONNECT_MAXNUMBER = 1024
# 超时
CONNECT_TIMEOUT = 10
# 最大读取字节数
RECV_MAXSIZE = 65535


class ProxyServerWorker():
	"""docstring for ProxyServerWorker"""

	_WorkerManagerLocalComputer = None

	# KeepAlive_Local_Remote = None
	# Address_Local_Remote = None
	# Url_Local_Remote = None
	_ConnectionType_Local_Remote = None 	# HTTP or HTTPS

	_Socket_Local_Computer = None
	_Socket_Remote_Local = None
	_HeadStr_Computer_Local = None
	_ProxyWorker = None 					# HttpProxy or HttpsProxy

	def __init__( self, sock, workermanager ):
		self._HeadStr_Computer_Local = ''
		self._Socket_Local_Computer = sock
		self._WorkerManagerLocalComputer = workermanager
		#self.Socket_Local_Remote = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

	def gethead( self ):
		isend = False
		isnewline = 0

		try:
			while( isend == False ): 
				tmp = self._Socket_Local_Computer.recv(1)
				self._HeadStr_Computer_Local += tmp

				if( tmp == '\r' ):
					isnewline += 1
				elif( tmp == '\n' ):
					isnewline += 1
					if( isnewline >= 4 ):
						isend = True
				else:
					isnewline = 0

		except:
			isnewline = 0
			self._HeadStr_Computer_Local = None

	def typecheck( self ):
		if ( cmp( self._HeadStr_Computer_Local[0:7], 'CONNECT' ) == 0 ):
			self._ConnectionType_Local_Remote = 'HTTPS'
		else:
			self._ConnectionType_Local_Remote = 'HTTP'

	def start( self ):
		try:
			# worker add
			self.workadd()

			self.gethead()
			self.typecheck()

			if( cmp( self._ConnectionType_Local_Remote, 'HTTP' ) == 0 ):
				self._ProxyWorker = Http.HttpProxy.HttpProxy( self._Socket_Local_Computer, self._HeadStr_Computer_Local, self )
			elif( cmp( self._ConnectionType_Local_Remote, 'HTTPS' ) == 0 ):
				self._ProxyWorker = Https.HttpsProxy.HttpsProxy( self._Socket_Local_Computer, self._HeadStr_Computer_Local, self )

			# worker start
			self._ProxyWorker.start()

		except Exception as e:
			G_Log.error( 'HttpsProxy or ProxyWorker start error! [ProxyServerWorker.py:ProxyServerWorker:start]' )
			# worker del
			self.workdel()
			pass

	def stop( self ):
		if( self._ProxyWorker != None ):
			self._ProxyWorker.stop()
			# worker del
			self.workdel()

	def workadd( self ):
		self._WorkerManagerLocalComputer( 'add', self )

	def workdel( self ):
		self._WorkerManagerLocalComputer( 'del', self )