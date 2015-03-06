# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: ProxyServerWorker.py

# original
import Http
import Https
import Tool
from globals import G_Log


class ProxyServerWorker():
	"""docstring for ProxyServerWorker"""

	_WorkerManagerLocalComputer = None

	_ConnectionType_Local_Remote = None 	# HTTP or HTTPS

	_Socket_Local_Computer = None
	_Socket_Remote_Local = None
	_HeadStr_Computer_Local = None
	_ProxyWorker = None 					# HttpProxy or HttpsProxy

	def __init__( self, sock, workermanager ):
		self._HeadStr_Computer_Local = ''
		self._Socket_Local_Computer = sock
		self._WorkerManagerLocalComputer = workermanager

	def gethead( self ):
		bufferbytes = b''
		headbytes = b''

		try:
			while True:
				bufferbytes = self._Socket_Local_Computer.recv(1)
				if not bufferbytes:
					G_Log.info( 'self._Socket_Local_Computer close(head)! [ProxyServerWorker.py:ProxyServerWorker:gethead]')
					break
				headbytes = headbytes + bufferbytes;
				if 	headbytes[-4:] == b'\r\n\r\n':
					break
			self._HeadStr_Computer_Local = headbytes.decode('utf8')

		except:
			self._HeadStr_Computer_Local = None
			G_Log.error( 'first head get error! [ProxyServerWorker.py:ProxyServerWorker:gethead] --> %s' %e )

	def typecheck( self ):
		if ( self._HeadStr_Computer_Local[0:7] == 'CONNECT' ):
			self._ConnectionType_Local_Remote = 'HTTPS'
		else:
			self._ConnectionType_Local_Remote = 'HTTP'

	def start( self ):
		try:
			self.gethead()
			self.typecheck()

			if( self._ConnectionType_Local_Remote == 'HTTP' ):
				self._ProxyWorker = Http.HttpProxy.HttpProxy( self._Socket_Local_Computer, self._HeadStr_Computer_Local, self )
			elif( self._ConnectionType_Local_Remote == 'HTTPS' ):
				self._ProxyWorker = Https.HttpsProxy.HttpsProxy( self._Socket_Local_Computer, self._HeadStr_Computer_Local, self )
				G_Log.warn( 'ProxyWorker create warning - HTTPS! [ProxyServerWorker.py:ProxyServerWorker:start] --> _HeadStr_Computer_Local: \r\n%s' %(self._HeadStr_Computer_Local) )
				# self._Socket_Local_Computer.close()
				# return
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
