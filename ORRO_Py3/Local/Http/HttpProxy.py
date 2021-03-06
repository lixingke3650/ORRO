# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: HttpProxy.py

# std
import socket
import threading

# original
import Tool
import globals
from globals import G_Log

# 最大读取字节数
S_RECV_MAXSIZE = 65536

class HttpProxy(object):
	"""docstring for HttpProxy"""
	
	_WorkerManagerLocalComputer = None

	_Local_Remote_Address = None
	_Socket_Local_Computer = None
	_Socket_Local_Remote = None
	_FirstHeadStr_Computer_Local = None

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
			G_Log.error( 'Worker add error! [HttpProxy.py:HttpProxy:start] --> %s' %e )
			return
		try:
			# ORRO Server Connect
			self._Socket_Local_Remote = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self._Local_Remote_Address = ( globals.G_ORRO_R_HOST, globals.G_ORRO_R_PORT )
			self._Socket_Local_Remote.connect_ex( self._Local_Remote_Address )

		except Exception as e:
			self._WorkerManagerLocalComputer.workdel()
			G_Log.error( 'socket connect error! [HttpProxy.py:HttpProxy:start] --> %s' %e )
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

	def stopAllForce( self ):
		G_Log.warn( 'HttpProxy stopForce! [HttpProxy.py:HttpProxy:stopForce]')

		try:
			if( self._Socket_Local_Computer is not None ):
				self._Socket_Local_Computer.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Computer.close()
				self._Socket_Local_Computer = None
			if( self._Socket_Local_Remote is not None ):
				self._Socket_Local_Remote.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Remote.close()
				self._Socket_Local_Remote = None

			if( self._IsWorker == True ): 
				self._IsWorker = False
				self._WorkerManagerLocalComputer.workdel()
		except Exception as e:
			G_Log.error( 'HttpProxy stopForce err! [HttpProxy.py:HttpProxy:stopForce] --> %s' %e )

		self._Keep_Alive = False

	def stopAuto( self ):
		G_Log.info( 'HttpProxy stopAuto [HttpProxy.py:HttpProxy:stopAuto]')

		try:
			if ( self._Keep_Alive_LC == False ):
				if( self._Socket_Local_Computer is not None ):
					self._Socket_Local_Computer.shutdown( socket.SHUT_RDWR )
					self._Socket_Local_Computer.close()
					self._Socket_Local_Computer = None

			if ( self._Keep_Alive_LR == False ):
				if( self._Socket_Local_Remote is not None ):
					self._Socket_Local_Remote.shutdown( socket.SHUT_RDWR )
					self._Socket_Local_Remote.close()
					self._Socket_Local_Remote = None

			if ( self._IsWorker == True and self._Socket_Local_Computer is None and self._Socket_Local_Remote is None ):
				self._IsWorker = False
				self._WorkerManagerLocalComputer.workdel()

		except Exception as e:
			G_Log.error( 'HttpProxy stopAuto err! [HttpProxy.py:HttpProxy:stopAuto] --> %s' %e )

	def stopAll( self ):
		G_Log.info( 'HttpProxy stopAll! [HttpProxy.py:HttpProxy:stopAll]')
		self._Keep_Alive = False

		try:
			if( self._Socket_Local_Computer is not None ):
				self._Socket_Local_Computer.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Computer.close()
				self._Socket_Local_Computer = None
			if( self._Socket_Local_Remote is not None ):
				self._Socket_Local_Remote.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Remote.close()
				self._Socket_Local_Remote = None

			if( self._IsWorker == True ): 
				self._IsWorker = False
				self._WorkerManagerLocalComputer.workdel()
		except Exception as e:
			G_Log.error( 'HttpProxy stopAll err! [HttpProxy.py:HttpProxy:stopAll] --> %s' %e )

	def stop( self ):
		self.stopLR()
		self.stopLC()

	def stopLR( self ):
		G_Log.info( 'HttpProxy stopLR! [HttpProxy.py:HttpProxy:stopLR]')

		try:
			if( self._Socket_Local_Remote is not None ):
				self._Socket_Local_Remote.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Remote.close()
				self._Socket_Local_Remote = None

			if ( self._Socket_Local_Computer is None and self._Socket_Local_Remote is None ):
				if( self._IsWorker == True ): 
					self._IsWorker = False
					self._WorkerManagerLocalComputer.workdel()
		except Exception as e:
			G_Log.error( 'HttpProxy stop err! [HttpProxy.py:HttpProxy:stop] --> %s' %e )

	def stopLC( self ):
		G_Log.info( 'HttpProxy stopLC! [HttpProxy.py:HttpProxy:stopLC]')

		try:
			if( self._Socket_Local_Computer is not None ):
				self._Socket_Local_Computer.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Computer.close()
				self._Socket_Local_Computer = None

			if ( self._Socket_Local_Computer is None and self._Socket_Local_Remote is None ):
				# G_Log.info( 'HttpProxy stop! [HttpProxy.py:HttpProxy:stop]')
				if( self._IsWorker == True ): 
					self._IsWorker = False
					self._WorkerManagerLocalComputer.workdel()
		except Exception as e:
			G_Log.error( 'HttpProxy stop err! [HttpProxy.py:HttpProxy:stop] --> %s' %e )

	# Local -> Remote
	def processLocalToRemote( self ):
		'''本地请求信息发送到远程'''

		# 初次请求发送
		self.aHttpProcLC( self._Socket_Local_Computer, self._Socket_Local_Remote, self._FirstHeadStr_Computer_Local )
		# 长连接时请求读取与发送
		while (self._Keep_Alive_LC == True):
			self.aHttpProcLC( self._Socket_Local_Computer, self._Socket_Local_Remote )

		# self.stopLC()
		self.stopAll()
		# self.stopAuto()

	# Remote -> Local
	def processRemoteToLocal( self ):
		'''读取远程回复信息并发送给本地应用'''

		# 应答读取与发送(至本地应用)
		while (self._Keep_Alive_LR == True):
			self.aHttpProcLR( self._Socket_Local_Computer, self._Socket_Local_Remote )

		# self.stopLR()
		self.stopAll()
		# self.stopAuto()

	def aHttpProcLC( self, socklc, socklr, head = None ):
		'''完成一次本地的请求处理，读取head - ORRO封装 - 转发 - 读取Body - 转发
		'''

		# Transfer-Encoding: chunked 标记
		isChunk = False

		try:
			# Head读取
			headbytes = b''
			headstr = ''
			if (head == None):
				while True:
					buffer = socklc.recv(1)
					if not buffer:
						G_Log.info( 'socklc close(head)! [HttpProxy.py:HttpProxy:aHttpProcLC]')
						self._Keep_Alive_LC = False
						if (headbytes == b''):
							return;
						break
					headbytes = headbytes + buffer;
					if 	headbytes[-4:] == b'\r\n\r\n':
						headstr = headbytes.decode('utf8')
						break
			else:
				headstr = head
			# Head处理
			headdict = Tool.HttpHead.HttpHead(headstr)
			# 去除代理添加的URL信息(百度，优酷等不识别)
			hosttmp = 'http://' + headdict.getTags('Host')
			headstr = headstr.replace(hosttmp, '', 1)
			headdict = Tool.HttpHead.HttpHead(headstr)
			# Connection状态取得
			connection = headdict.getTags('Connection')
			# 持久性连接取消
			headdict.updateKey2('Connection', 'close')
			headstr = headdict.getHeadStr()
			# ###############
			# CnBeta中若指定 accept-encoding为gzip, deflate时
			# response中不含有Transfer-Encoding或Content-Length
			# 目前暂不支持不含有Transfer-Encoding或Content-Length头的解析
			# accept-encoding 删除
			# headdict.delHeadKey('accept-encoding')
			# ###############
			#Transfer-Encoding取得
			if ('chunked' == headdict.getTags('Transfer-Encoding')):
				isChunk = True
			# 根据Transfer-Encoding是否存在，分别处理
			if (isChunk == True):
				# ORRO请求头作成
				orrohead = ''
				if (headdict.getTags('HttpVersion') == 'HTTP/1.0'):
					orrohead = self.createOrroHeadOfTEC(False)
				elif (connection is not None and connection.lower() == 'close'):
					orrohead = self.createOrroHeadOfTEC(False)
				else:
					orrohead = self.createOrroHeadOfTEC(True)
				# ORRO Head发送
				socklr.send( orrohead.encode('utf8') )
				# 请求Head发送
				socklr.send( headstr.encode('utf8') )

				# >>>>>>>>>>>>>>>>
				G_Log.debug( 'SEND REMOTE HEAD: \r\n%s' % headstr );
				# <<<<<<<<<<<<<<<<

				while True:
					buffer = socklc.recv(S_RECV_MAXSIZE)
					if not buffer:
						G_Log.info( 'socklc close(chunked length)! [HttpProxy.py:HttpProxy:aHttpProcLC]')
						self._Keep_Alive_LC = False
						break
					socklr.send( buffer )
					if 	buffer[-5:] == b'0\r\n\r\n':
						break
			else:
				# 请求Body长度取得
				bodylength = 0
				bodylengthstr = headdict.getTags('Content-Length')
				if (bodylengthstr is not None):
					bodylength = int(bodylengthstr)
				# ORRO请求头作成
				headlength = len(headstr)
				orrohead = ''
				if (headdict.getTags('HttpVersion') == 'HTTP/1.0'):
					orrohead = self.createOrroHeadOfCL(headlength+bodylength, False)
				elif (connection is not None and connection.lower() == 'close'):
					orrohead = self.createOrroHeadOfCL(headlength+bodylength, False)
				else:
					orrohead = self.createOrroHeadOfCL(headlength+bodylength, True)
				# ORRO Head发送
				socklr.send( orrohead.encode('utf8') )
				# 请求Head发送
				socklr.send( headstr.encode('utf8') )

				# >>>>>>>>>>>>>>>>
				G_Log.debug( 'SEND REMOTE HEAD: \r\n%s' % headstr );
				# <<<<<<<<<<<<<<<<

				# Body读取与发送
				lengthtmp = 0
				buffer = b''
				while (lengthtmp < bodylength):
					buffer = socklc.recv(S_RECV_MAXSIZE)
					if not buffer:
						G_Log.info( 'socklc close(body)! [HttpProxy.py:HttpProxy:aHttpProcLC]')
						self._Keep_Alive_LC = False
						break
					socklr.send( buffer )
					lengthtmp += len(buffer)
		except Exception as e:
			self._Keep_Alive_LC = False
			G_Log.error( 'local to remote error! [HttpProxy.py:HttpProxy:aHttpProcLC] --> %s' %e )

	def aHttpProcLR( self, socklc, socklr ):
		'''完成一次远端的应答处理，读取ORRO包 - ORRO解封 - 转发 - 读取body - 转发
		'''

		# Transfer-Encoding: chunked标记
		isChunk = False

		try:
			# ORRO Head读取
			orroheadbytes = b''
			orroheadstr = ''
			while True:
				buffer = socklr.recv(1)
				if not buffer:
					G_Log.info( 'socklr close(orro head)! [HttpProxy.py:HttpProxy:aHttpProcLR]')
					self._Keep_Alive_LR = False
					if (orroheadbytes == b''):
						return
					break
				orroheadbytes = orroheadbytes + buffer;
				if 	orroheadbytes[-4:] == b'\r\n\r\n':
					orroheadstr = orroheadbytes.decode('utf8')
					break

			# ORRO头此处暂不做其他处理
			# # ORRO Head处理
			# orroheaddict = Tool.HttpHead.HttpHead(orroheadstr)
			# # ORRO Body长度取得
			# orrobodylengthstr = orroheaddict.getTags('Content-Length')
			# orrobodylength = 0
			# if (orrobodylengthstr != None):
			# 	orrobodylength = int(orrobodylengthstr)
			#
			#

			# Response Head读取与发送
			headbytes = b''
			headstr = ''
			while True:
				buffer = socklr.recv(1)
				if not buffer:
					G_Log.info( 'socklr close(head)! [HttpProxy.py:HttpProxy:aHttpProcLR]')
					self._Keep_Alive_LR = False
					if (headbytes == b''):
						return
					break
				headbytes = headbytes + buffer;
				if 	headbytes[-4:] == b'\r\n\r\n':
					headstr = headbytes.decode('utf8')
					break
			# Response处理
			headdict = Tool.HttpHead.HttpHead(headstr)
			# Connection状态判断
			connection = headdict.getTags('Connection')
			if (headdict.getTags('HttpVersion') == 'HTTP/1.0'):
				self._Keep_Alive_LR = False
				self._Keep_Alive_LC = False
			elif (connection is not None and connection.lower() == 'close'):
				self._Keep_Alive_LR = False
				self._Keep_Alive_LC = False
			# Transfer-Encoding取得
			if ('chunked' == headdict.getTags('Transfer-Encoding')):
				isChunk = True
			# Response Body长度取得
			resbodylength = 0
			if (isChunk != True):
				resbodylengthstr = headdict.getTags('Content-Length')
				if (resbodylengthstr != None):
					resbodylength = int(resbodylengthstr)
			# 持久性连接取消
			headdict.updateKey2('Connection', 'close')
			headstr = headdict.getHeadStr()
			socklc.send( headstr.encode('utf8') )

			# >>>>>>>>>>>>>>>>
			G_Log.debug( 'SEND LOCAL HEAD: \r\n%s' % headstr );
			# <<<<<<<<<<<<<<<<

			# 根据Transfer-Encoding是否存在，分别处理
			if (isChunk == True):
				# chunked 读取
				# 此处对chunked暂做简易处理
				while True:
					buffer = socklr.recv(S_RECV_MAXSIZE)
					if not buffer:
						G_Log.info( 'socklr close(chunked length)! [HttpProxy.py:HttpProxy:aHttpProcLR]')
						self._Keep_Alive_LR = False
						break
					socklc.send( buffer )
					if 	buffer[-5:] == b'0\r\n\r\n':
						break
			else:
				# Response Body读取与发送
				lengthtmp = 0
				while (lengthtmp < resbodylength):
					buffer = socklr.recv(S_RECV_MAXSIZE)
					if not buffer:
						G_Log.info( 'socklr close(body)! [HttpProxy.py:HttpProxy:aHttpProcLR]')
						self._Keep_Alive_LR = False
						break
					socklc.send( buffer )
					lengthtmp += len(buffer)
		except Exception as e:
			self._Keep_Alive_LR = False
			G_Log.error( 'remote to local error! [HttpProxy.py:HttpProxy:aHttpProcLR] --> %s' %e )

	def addProxyConnection( self, keep, head ):
		'''添加Proxy-Connection头信息
		keep: None - 设置为原来信息(与Connection相同，Connection不存在则不保持连接close)
			  True - 保持连接(keep-alive)
			  False- 不保持连接(close)'''

		try:
			# Proxy-Connection添加
			if( keep == True ):
				head.addHeadKey( 'Proxy-Connection: ' + 'keep-alive')
			elif( keep == False ):
				head.addHeadKey( 'Proxy-Connection: ' + 'close')
			else:
				# Connection取得
				connection = head.getTags( 'Connection' )
				if( connection is None ):
					head.addHeadKey( 'Proxy-Connection: ' + 'close')
				else:
					head.addHeadKey( 'Proxy-Connection: ' + connection)
		except Exception as e:
			G_Log.error( 'add Proxy-Connection error! [HttpProxy.py:HttpProxy:addProxyConnection] --> %s' %e )
		return head

	def delProxyConnection( self, head ):
		'''删除Proxy-Connection头信息

		'''

		try:
			# Proxy-Connection删除
			head.delHeadKey( "Proxy-Connection" )
		except Exception as e:
			G_Log.error( 'del Proxy-Connection error! [HttpProxy.py:HttpProxy:delProxyConnection] --> %s' %e )
		return head

	def addProxyOrroConnection( self, keep, head ):
		'''添加ProxyOrro-Connection头信息
		keep: None - 设置为原来信息(与Connection相同，Connection不存在则不保持连接close)
			  True - 保持连接(keep-alive)
			  False- 不保持连接(close)'''

		try:
			# Proxy-Connection添加
			if( keep == True ):
				head.addHeadKey( 'ProxyOrro-Connection: ' + 'keep-alive')
			elif( keep == False ):
				head.addHeadKey( 'ProxyOrro-Connection: ' + 'close')
			else:
				# Connection取得
				connection = head.getTags( 'Connection' )
				if( connection is None ):
					head.addHeadKey( 'ProxyOrro-Connection: ' + 'close')
				else:
					head.addHeadKey( 'ProxyOrro-Connection: ' + connection)
		except Exception as e:
			G_Log.error( 'add ProxyOrro-Connection error! [HttpProxy.py:HttpProxy:addProxyOrroConnection] --> %s' %e )
		return head

	def delProxyOrroConnection( self, head ):
		'''删除ProxyOrro-Connection头信息

		'''

		try:
			# Proxy-Connection删除
			head.delHeadKey( "ProxyOrro-Connection" )
		except Exception as e:
			G_Log.error( 'del ProxyOrro-Connection error! [HttpProxy.py:HttpProxy:delProxyOrroConnection] --> %s' %e )
		return head

	def createOrroHeadOfCL( self, length, proxyconnection ):
		'''生成ORRO头
		length         : bodysize
		proxyconnection: None - 不添加ProxyOrro-Connection
						 True - 添加ProxyOrro-Connection为keep-alive
						 False- 添加ProxyOrro-Connection为close
		'''

		proxyorro = '\r\n'
		if (proxyconnection == True):
			proxyorro = 'ProxyOrro-Connection: keep-alive\r\n'
		elif (proxyconnection == False):
			proxyorro = 'ProxyOrro-Connection: close\r\n'
		porttmp = ''
		if (globals.G_ORRO_R_PORT != 80):
			porttmp = ':' + str(globals.G_ORRO_R_PORT)
		headstr = 'POST http://' + globals.G_ORRO_R_HOST + porttmp + '/ORRO_HTTP HTTP/1.1\r\n'	\
				+ 'Host: ' + globals.G_ORRO_R_HOST + porttmp + '\r\n'					\
				+ 'Content-Length: ' + str(length) + '\r\n'								\
				+ 'Content-Type: application/octet-stream\r\n'							\
				+ 'Connection: keep-alive\r\n'											\
				+ proxyorro 															\
				+ '\r\n'
		return headstr

	def createOrroHeadOfTEC( self, proxyconnection ):
		'''生成ORRO头,用于处理Transfer-Encoding: chunked
		proxyconnection: None - 不添加ProxyOrro-Connection
						 True - 添加ProxyOrro-Connection为keep-alive
						 False- 添加ProxyOrro-Connection为close
		'''

		proxyorro = '\r\n'
		if (proxyconnection == True):
			proxyorro = 'ProxyOrro-Connection: keep-alive\r\n'
		elif (proxyconnection == False):
			proxyorro = 'ProxyOrro-Connection: close\r\n'
		porttmp = ''
		if (globals.G_ORRO_R_PORT != 80):
			porttmp = ':' + str(globals.G_ORRO_R_PORT)
		headstr = 'POST http://' + globals.G_ORRO_R_HOST + porttmp + '/ORRO_HTTP HTTP/1.1\r\n'	\
				+ 'Host: ' + globals.G_ORRO_R_HOST + porttmp + '\r\n'								\
				+ 'Transfer-Encoding: chunked\r\n'										\
				+ 'Content-Type: application/octet-stream\r\n'							\
				+ 'Connection: keep-alive\r\n'											\
				+ proxyorro 															\
				+ '\r\n'
		return headstr
