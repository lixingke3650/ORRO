# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: HttpProxy.py

# std
import msvcrt
import os
import socket
import sys
import threading
sys.path.append('..')
# original
import Tool.HttpHead
import Tool.Logger
import globals
from globals import G_Log

# 最大读取字节数
S_RECV_MAXSIZE = 65535

class HttpProxy(object):
	"""docstring for HttpProxy"""
	
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
			G_Log.error( 'Worker add error! [HttpProxy.py:HttpProxy:start] --> %s' %e )
			return
		try:
			# Fir Head Format
			self._FirstHeadDict_Computer_Local = Tool.HttpHead.HttpHead( self._FirstHeadStr_Computer_Local )
			# ORRO Server Connect
			self._Socket_Local_Remote = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self._Local_Remote_Address = ( globals.G_ORRO_R_HOST, globals.G_ORRO_R_PORT )
			self._Socket_Local_Remote.connect( self._Local_Remote_Address )

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

	def stopAll( self ):
		G_Log.info( 'HttpProxy stopAll! [HttpProxy.py:HttpProxy:stopAll]')
		self._Keep_Alive = False
		try:
			if( self._Socket_Local_Computer != None ):
				self._Socket_Local_Computer.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Computer.close()
				self._Socket_Local_Computer = None
			if( self._Socket_Local_Remote != None ):
				self._Socket_Local_Remote.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Remote.close()
				self._Socket_Local_Remote = None

			# self._ProcessLtoR.join()
			# self._ProcessRtoL.join()
			if( self._IsWorker == True ): 
				self._IsWorker = False
				self._WorkerManagerLocalComputer.workdel()
		except Exception as e:
			G_Log.error( 'HttpProxy stopAll err! [HttpProxy.py:HttpProxy:stopAll] --> %s' %e )

	def stop( self ):
		self.stopLR()
		self.stopLC()

	def stopLR( self ):
		try:
			if( self._Socket_Local_Remote != None ):
				self._Socket_Local_Remote.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Remote.close()
				self._Socket_Local_Remote = None

			# self._ProcessLtoR.join()
			# self._ProcessRtoL.join()

			if ( self._Socket_Local_Computer == None and self._Socket_Local_Remote == None ):
				# G_Log.info( 'HttpProxy stop! [HttpProxy.py:HttpProxy:stop]')
				if( self._IsWorker == True ): 
					self._IsWorker = False
					self._WorkerManagerLocalComputer.workdel()
		except Exception as e:
			G_Log.error( 'HttpProxy stop err! [HttpProxy.py:HttpProxy:stop] --> %s' %e )

	def stopLC( self ):
		try:
			if( self._Socket_Local_Computer != None ):
				self._Socket_Local_Computer.shutdown( socket.SHUT_RDWR )
				self._Socket_Local_Computer.close()
				self._Socket_Local_Computer = None

			# self._ProcessLtoR.join()
			# self._ProcessRtoL.join()

			if ( self._Socket_Local_Computer == None and self._Socket_Local_Remote == None ):
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

	# Remote -> Local
	def processRemoteToLocal( self ):
		'''读取远程回复信息并发送给本地应用'''

		# 应答读取与发送(至本地应用)
		while (self._Keep_Alive_LR == True):
			self.aHttpProcLR( self._Socket_Local_Computer, self._Socket_Local_Remote )

		# self.stopLR()
		self.stopAll()

	def aHttpProcLC( self, socklc, socklr, head = None ):
		'''完成一次本地的请求处理，读取head - ORRO封装 - 转发 - 读取Body - 转发
		'''

		# Transfer-Encoding: chunked对应
		isChunk = False

		try:
			# Head读取
			headstr = ''
			headlength = 0
			if (head == None):
				while True:
					buffer = socklc.recv(1)
					if (len(buffer) <= 0):
						G_Log.info( 'socklc close(head)! [HttpProxy.py:HttpProxy:aHttpProcLC]')
						self._Keep_Alive_LC = False
						return
					headstr = headstr + buffer;
					headlength = len(headstr)
					if (headlength >= 4):
						if 	headstr[headlength - 4] == '\r' and \
							headstr[headlength - 3] == '\n' and \
							headstr[headlength - 2] == '\r' and \
							headstr[headlength - 1] == '\n' :
							break
			else:
				headstr = head
				headlength = len(headstr)
			# Head处理
			headdict = Tool.HttpHead.HttpHead(headstr)
			# Transfer-Encoding取得
			if ('chunked' == headdict.getTags('Transfer-Encoding')):
				isChunk = True
			# 根据Transfer-Encoding是否存在，分别处理
			if (isChunk == True):
				# Connection状态取得
				connection = headdict.getTags('Connection')
				# ORRO请求头作成
				orrohead = ''
				if (connection == 'keep-alive' or connection == 'Keep-Alive'):
					orrohead = self.createOrroHeadOfTEC(True)
				else:
					G_Log.info( 'Request Head Connection is not keep-alive: %s. [HttpProxy.py:HttpProxy:aHttpProcLC]' %headstr)
					orrohead = self.createOrroHeadOfTEC(False)
				# ORRO Head发送
				socklr.send( orrohead )
				# 请求Head发送
				socklr.send( headstr )
				# chunked 读取
				chunkedstr = ''
				while True:
					buffer = socklc.recv(1)
					if (len(buffer) <= 0):
						G_Log.info( 'socklc close(chunked length)! [HttpProxy.py:HttpProxy:aHttpProcLC]')
						self._Keep_Alive_LC = False
						return
					chunkedstr = chunkedstr + buffer;
					bufferlength = len(chunkedstr)
					if (bufferlength >= 4):
						if 	chunkedstr[bufferlength - 4] == '\r' and \
							chunkedstr[bufferlength - 3] == '\n' and \
							chunkedstr[bufferlength - 2] == '\r' and \
							chunkedstr[bufferlength - 1] == '\n' :
							break
				# chunked 发送
				socklr.send( chunkedstr )
			else:
				# 请求Body长度取得
				bodylengthstr = headdict.getTags('Content-Length')
				bodylength = 0
				if (bodylengthstr != None):
					bodylength = int(bodylengthstr)
				# Connection状态取得
				connection = headdict.getTags('Connection')
				# ORRO请求头作成
				orrohead = ''
				if (connection == 'keep-alive' or connection == 'Keep-Alive'):
					orrohead = self.createOrroHeadOfCL(headlength+bodylength, True)
				else:
					G_Log.info( 'Request Head Connection is not keep-alive: %s. [HttpProxy.py:HttpProxy:aHttpProcLC]' %headstr)
					orrohead = self.createOrroHeadOfCL(headlength+bodylength, False)
				# 持久性连接取消
				# headdict.delHeadKey('Connection')
				# headdict.updateKey('Connection', 'close')
				# headstr = headdict.getHeadStr()
				# ORRO Head发送
				socklr.send( orrohead )
				# 请求Head发送
				socklr.send( headstr )
				# Body读取与发送
				lengthtmp = 0
				while (lengthtmp < bodylength):
					buffer = socklc.recv(S_RECV_MAXSIZE)
					if (len(buffer) <= 0):
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

		# Transfer-Encoding: chunked对应
		isChunk = False

		try:
			# ORRO Head读取
			orroheadstr = ''
			orroheadlength = 0
			while True:
				buffer = socklr.recv(1)
				if (len(buffer) <= 0):
					G_Log.info( 'socklr close(orro head)! [HttpProxy.py:HttpProxy:aHttpProcLR]')
					self._Keep_Alive_LR = False
					return
				orroheadstr = orroheadstr + buffer;
				orroheadlength = len(orroheadstr)
				if (orroheadlength >= 4):
					if 	orroheadstr[orroheadlength - 4] == '\r' and \
						orroheadstr[orroheadlength - 3] == '\n' and \
						orroheadstr[orroheadlength - 2] == '\r' and \
						orroheadstr[orroheadlength - 1] == '\n' :
						break
			# ORRO Head处理
			orroheaddict = Tool.HttpHead.HttpHead(orroheadstr)
			# ORRO Body长度取得
			orrobodylengthstr = orroheaddict.getTags('Content-Length')
			orrobodylength = 0
			if (orrobodylengthstr != None):
				orrobodylength = int(orrobodylengthstr)
			# Response Head读取与发送
			headstr = ''
			lengthtmp = 0
			while True:
				buffer = socklr.recv(1)
				if (len(buffer) <= 0):
					G_Log.info( 'socklr close(head)! [HttpProxy.py:HttpProxy:aHttpProcLR]')
					self._Keep_Alive_LR = False
					return
				headstr = headstr + buffer;
				lengthtmp = len(headstr)
				if (lengthtmp >= 4):
					if 	headstr[lengthtmp - 4] == '\r' and \
						headstr[lengthtmp - 3] == '\n' and \
						headstr[lengthtmp - 2] == '\r' and \
						headstr[lengthtmp - 1] == '\n' :
						break
			# Response处理
			headdict = Tool.HttpHead.HttpHead(headstr)
			# Transfer-Encoding取得
			if ('chunked' == headdict.getTags('Transfer-Encoding')):
				isChunk = True
			headdict.updateKey('Connection', 'close')
			headstr = headdict.getHeadStr()
			socklc.send( headstr )
			# 根据Transfer-Encoding是否存在，分别处理
			if (isChunk == True):
				# chunked 读取
				chunkedstr = ''
				while True:
					buffer = socklr.recv(1)
					if (len(buffer) <= 0):
						G_Log.info( 'socklc close(chunked length)! [HttpProxy.py:HttpProxy:aHttpProcLC]')
						self._Keep_Alive_LC = False
						return
					chunkedstr = chunkedstr + buffer;
					bufferlength = len(chunkedstr)
					if (bufferlength >= 4):
						if 	chunkedstr[bufferlength - 4] == '\r' and \
							chunkedstr[bufferlength - 3] == '\n' and \
							chunkedstr[bufferlength - 2] == '\r' and \
							chunkedstr[bufferlength - 1] == '\n' :
							break
				# chunked 发送
				socklc.send( chunkedstr )
			else:
				# Response Body读取与发送
				while (lengthtmp < orrobodylength):
					buffer = socklr.recv(S_RECV_MAXSIZE)
					if (len(buffer) <= 0):
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
				if( connection == None ):
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
				if( connection == None ):
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
				+ 'Host: ' + globals.G_ORRO_R_HOST + porttmp + '\r\n'								\
				+ 'Content-Length: ' + str(length) + '\r\n'								\
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
				+ 'Connection: keep-alive\r\n'											\
				+ proxyorro 															\
				+ '\r\n'
		G_Log.debug('createOrroHeadOfTEC headstr:%s' % headstr)
		return headstr
