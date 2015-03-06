# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: HttpsProxy.py

# std
import socket
import threading
# original
import Tool
import globals
from globals import G_Log

# 最大读取字节数
S_RECV_MAXSIZE = 65536

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
		# worker add
		try:
			self._WorkerManagerLocalComputer.workadd()
			self._IsWorker = True
		except Exception as e:
			self._IsWorker = False
			G_Log.error( 'Worker add error! [HttpsProxy.py:HttpsProxy:start] --> %s' %e )
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
			G_Log.error( 'socket connect error! [HttpsProxy.py:HttpsProxy:start] --> %s' %e )
			return

		# process thread
		self._ProcessLtoR = threading.Thread( target = self.processLocalToRemote )
		self._ProcessRtoL = threading.Thread( target = self.processRemoteToLocal )
		self._Keep_Alive = True
		self._Keep_Alive_LC = True
		self._Keep_Alive_LR = True
		self._ProcessLtoR.start()
		self._ProcessRtoL.start()

		self._ProcessLtoR.join()
		self._ProcessRtoL.join()

		self.stop()

	# 强制停止与本地的socket连接，停止与云端的socket连接
	def stopAllForce( self ):
		G_Log.info( 'HttpProxy stopForce! [HttpProxy.py:HttpProxy:stopForce]')

		try:
			if( self._Socket_Local_Computer != None ):
				self._Socket_Local_Computer.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Computer.close()
				self._Socket_Local_Computer = None
			if( self._Socket_Local_Remote != None ):
				self._Socket_Local_Remote.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Remote.close()
				self._Socket_Local_Remote = None

			if( self._IsWorker == True ): 
				self._IsWorker = False
				self._WorkerManagerLocalComputer.workdel()
		except Exception as e:
			G_Log.error( 'HttpProxy stopForce err! [HttpProxy.py:HttpProxy:stopForce] --> %s' %e )

		self._Keep_Alive = False

	# Local -> Remote
	def processLocalToRemote( self ):
		'''本地请求信息发送到远程'''

		# 初次请求发送
		self.aHttpsProcLC( self._Socket_Local_Computer, self._Socket_Local_Remote, self._FirstHeadStr_Computer_Local )
		# 长连接时请求读取与发送
		while (self._Keep_Alive_LC == True):
			self.aHttpsProcLC( self._Socket_Local_Computer, self._Socket_Local_Remote )

		self.stopAllForce()

	# Remote -> Local
	def processRemoteToLocal( self ):
		'''读取远程回复信息并发送给本地应用'''

		# 应答读取与发送(至本地应用)
		while (self._Keep_Alive_LR == True):
			self.aHttpsProcLR( self._Socket_Local_Computer, self._Socket_Local_Remote )

		self.stopAllForce()

	def aHttpsProcLC( self, socklc, socklr, head = None ):
		'''完成一次本地的请求处理，读取head - ORRO封装 - 转发 - 读取Body - 转发
		'''

		try:
			# Head读取
			headbytes = b''
			headstr = ''
			# head == None时SSL内容无法查看，只负责转发，
			if (head == None):
				while True:
					buffer = socklc.recv(S_RECV_MAXSIZE)
					if not buffer:
						G_Log.info( 'socklc close(head)! [HttpsProxy.py:HttpsProxy:aHttpsProcLC]')
						self._Keep_Alive_LC = False
						break
					# 请求头编码
					connecthead = self._FirstHeadStr_Computer_Local.encode('utf8')
					# 转发ORRO头作成
					orroheadstr = self.createOrroHead(len(buffer)+len(connecthead), True)
					# ORRO头发送
					socklr.send( orroheadstr.encode('utf8') )
					# >>>>>>>>>>>>
					G_Log.debug( 'orroheadstr: \r\n%s' %orroheadstr )
					# <<<<<<<<<<<<
					# CONNECT头发送
					socklr.send( connecthead )
					# SSL 内容转发
					socklr.send( buffer )
					# >>>>>>>>>>>>
					G_Log.debug( 'ssl body size: %s' %str(len(buffer)) )
					# <<<<<<<<<<<<
			# 初次请求时，追加CONNECT ORRO头
			else:
				# 初次请求，回应CONNECT成功
				socklc.send('HTTP/1.0 200\r\nConnection established\r\nProxyServer: ORRO\r\n\r\n'.encode('utf8'))
				# 初次请求,转发ORRO头作成
				# orroheadstr = self.createOrroHead( len(head), True)
				if (self._FirstHeadDict_Computer_Local == None):
					self._FirstHeadDict_Computer_Local = Tool.HttpHead.HttpHead( head )
				requrl = self._FirstHeadDict_Computer_Local.getTags('Url')
				if (requrl == None):
					G_Log.error('get Request Https Url Error. [HttpsProxy.py:HttpsProxy:aHttpsProcLC]')
					self._Keep_Alive_LC = False
					return
				# requrlsplitarr = self._FirstHeadDict_Computer_Local.getTags('Url').split(':')
				# orroheadstr = self.createOrroHeadOfHttps(len(head), requrlsplitarr[0], requrlsplitarr[1])
				
				# # ORRO头发送
				# socklr.send( orroheadstr.encode('utf8') )
				# # SSL 内容转发
				# socklr.send( head.encode('utf8') )

		except Exception as e:
			self._Keep_Alive_LC = False
			G_Log.error( 'local to remote error! [HttpProxy.py:HttpProxy:aHttpProcLC] --> %s' %e )

	def aHttpsProcLR( self, socklc, socklr ):
		'''完成一次远端的应答处理，读取ORRO包 - ORRO解封 - 转发 - 读取body - 转发
		'''

		try:
			# ORRO Head读取
			orroheadbytes = b''
			orroheadstr = ''
			while True:
				buffer = socklr.recv(1)
				if not buffer:
					G_Log.info( 'socklr close(orro head)! [HttpsProxy.py:HttpsProxy:aHttpsProcLR]')
					self._Keep_Alive_LR = False
					# if (orroheadbytes == b''):
					# 	return
					break
				orroheadbytes = orroheadbytes + buffer;
				if 	orroheadbytes[-4:] == b'\r\n\r\n':
					orroheadstr = orroheadbytes.decode('utf8')
					break
			# ORRO Head处理
			orroheaddict = Tool.HttpHead.HttpHead(orroheadstr)
			# ORRO Body长度取得
			orrobodylengthstr = orroheaddict.getTags('Content-Length')
			orrobodylength = 0
			if (orrobodylengthstr != None):
				orrobodylength = int(orrobodylengthstr)

			# >>>>>>>>>>>>
			G_Log.debug( 'res orroheadstr: \r\n%s' %orroheadstr )
			# <<<<<<<<<<<<

			# SSL内容转发
			# while True:
			buffer = socklr.recv(S_RECV_MAXSIZE)
			if not buffer:
				G_Log.info( 'socklr close(orro head)! [HttpProxy.py:HttpProxy:aHttpProcLR]' )
				self._Keep_Alive_LR = False
				return
			# SSL 内容转发
			socklc.send( buffer )
			# >>>>>>>>>>
			G_Log.debug( 'SSL Response Body size: %s' %str(len(buffer)) )
			# <<<<<<<<<<
			self._Keep_Alive_LR = False

		except Exception as e:
			self._Keep_Alive_LR = False
			G_Log.error( 'remote to local error! [HttpsProxy.py:HttpsProxy:aHttpsProcLR] --> %s' %e )

	def createOrroHead( self, length, first=False ):
		'''生成ORRO头，包含CONNECT对象信息
		'''

		headstr = ''
		try:
			orrohead = '\r\n'
			if ( first == True ):
				orrohead = 'ProxyOrro-HttpsConnect: yes\r\n'

			porttmp = ''
			if (globals.G_ORRO_R_PORT != 80):
				porttmp = ':' + str(globals.G_ORRO_R_PORT)
			headstr = 'POST http://' + globals.G_ORRO_R_HOST + porttmp + '/ORRO_HTTPS HTTP/1.1\r\n'	\
					+ 'Host: ' + globals.G_ORRO_R_HOST + '\r\n'								\
					+ 'Content-Length: ' + str(length) + '\r\n'								\
					+ 'Content-Type: application/octet-stream\r\n'							\
					+ 'Connection: keep-alive\r\n'											\
					+ orrohead 																\
					+ '\r\n'
		except Exception as e:
			headstr = ''
			G_Log.error( 'create orro head error! [HttpsProxy.py:HttpsProxy:createOrroHead] --> %s' %e )
		return headstr

	def createOrroHeadOfHttps( self, reqheadsize, bodysize, httpsurl=None, httpsport='443' ):
		'''生成ORRO头，包含CONNECT对象信息
		'''

		headstr = ''
		try:
			orrohttpsheadurl = ''
			orrohttpsheadport = ''
			if ( httpsurl != None ):
				orrohttpsheadurl = 'ProxyOrro-HttpsConnectUrl: ' + httpsurl + '\r\n'
				orrohttpsheadport = 'ProxyOrro-HttpsConnectPort: ' + httpsport + '\r\n'
			porttmp = ''
			if (globals.G_ORRO_R_PORT != 80):
				porttmp = ':' + str(globals.G_ORRO_R_PORT)
			headstr = 'POST http://' + globals.G_ORRO_R_HOST + porttmp + '/ORRO_HTTPS HTTP/1.1\r\n'	\
					+ 'Host: ' + globals.G_ORRO_R_HOST + porttmp + '\r\n'							\
					+ 'Content-Length: ' + str(bodysize) + '\r\n'									\
					+ 'Content-Type: application/octet-stream\r\n'							\
					+ 'Connection: keep-alive\r\n'											\
					+ 'ProxyOrro-HttpsConnectHeadSize: ' + str(reqheadsize) + '\r\n'		\
					+ orrohttpsheadurl 														\
					+ orrohttpsheadport 													\
					+ '\r\n\r\n'
		except Exception as e:
			headstr = ''
			G_Log.error( 'create orro head error! [HttpsProxy.py:HttpsProxy:createOrroHeadOfHttps] --> %s' %e )
		return headstr
