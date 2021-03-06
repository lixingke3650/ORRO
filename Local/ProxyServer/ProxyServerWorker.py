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
			self.gethead()
			self.typecheck()

			if( cmp( self._ConnectionType_Local_Remote, 'HTTP' ) == 0 ):
				self._ProxyWorker = Http.HttpProxy.HttpProxy( self._Socket_Local_Computer, self._HeadStr_Computer_Local, self )
			elif( cmp( self._ConnectionType_Local_Remote, 'HTTPS' ) == 0 ):
				# self._ProxyWorker = Https.HttpsProxy.HttpsProxy( self._Socket_Local_Computer, self._HeadStr_Computer_Local, self )
				G_Log.warn( 'ProxyWorker create warning - HTTPS! [ProxyServerWorker.py:ProxyServerWorker:start] --> _ConnectionType_Local_Remote: %s' %(self._ConnectionType_Local_Remote) )
				self._Socket_Local_Computer.close()
				return
			else:
				G_Log.error( 'ProxyWorker create error! [ProxyServerWorker.py:ProxyServerWorker:start] --> _ConnectionType_Local_Remote: %s' %(self._ConnectionType_Local_Remote) )
				self._Socket_Local_Computer.close()
				return
		except Exception as e:
			G_Log.error( 'HttpProxy or HttpsProxy create error! [ProxyServerWorker.py:ProxyServerWorker:start] --> %s' %e )
			self._Socket_Local_Computer.close()
			return

		try:
			# worker start
			self._ProxyWorker.start()
		except Exception as e:
			G_Log.error( 'ProxyWorker start error! [ProxyServerWorker.py:ProxyServerWorker:start] --> %s' %e )
			# worker del
			self.workdel()

	def stop( self ):
		if( self._ProxyWorker != None ):
			self._ProxyWorker.stop()
			# worker del
			self.workdel()

	def workadd( self ):
		ret = self._WorkerManagerLocalComputer( 'add', self )
		#>>>>
		print('WorkAdd : %d' %ret)
		#<<<<
		return ret

	def workdel( self ):
		ret = self._WorkerManagerLocalComputer( 'del', self )
		#>>>>
		print('WorkDel : %d' %ret)
		#<<<<
		return ret
