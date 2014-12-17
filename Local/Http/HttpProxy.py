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
from globals import G_Log

# 最大读取字节数
S_RECV_MAXSIZE = 65535
S_ORRO_HOST = '192.168.1.125'
S_ORRO_PORT = 5085
S_ORRO_URL = 'http://192.168.1.125:5085/ORRO_HTTP'

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
	_IsWorker = None

	def __init__( self, socklc, headstr, workermanager ):
		self._Socket_Local_Computer = socklc
		self._FirstHeadStr_Computer_Local = headstr
		self._WorkerManagerLocalComputer = workermanager
		self._IsWorker = False

	def start( self ):
		# worker add
		try:
			ret = self._WorkerManagerLocalComputer.workadd()
			#>>>>
			print('WorkAdd : %d' %ret)
			#<<<<
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
			self._Local_Remote_Address = ( S_ORRO_HOST, S_ORRO_PORT )
			self._Socket_Local_Remote.connect( self._Local_Remote_Address )

		except Exception as e:
			ret = self._WorkerManagerLocalComputer.workdel()
			G_Log.error( 'socket connect error! [HttpProxy.py:HttpProxy:start] --> %s' %e )
			return
		# process thread
		self._ProcessLtoR = threading.Thread( target = self.processLocalToRemote )
		self._ProcessRtoL = threading.Thread( target = self.processRemoteToLocal )
		self._Keep_Alive = True
		self._ProcessLtoR.start()
		self._ProcessRtoL.start()

	def stop( self ):
		G_Log.info( 'HttpProxy stop! [HttpProxy.py:HttpProxy:stop]')
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
				ret = self._WorkerManagerLocalComputer.workdel()
				#>>>>
				print('WorkDel : %d' %ret)
				#<<<<
		except Exception as e:
			G_Log.error( 'HttpProxy stop err! [HttpProxy.py:HttpProxy:stop] --> %s' %e )

	# Local -> Remote
	def processLocalToRemote( self ):
		'''本地请求信息发送到远程'''

		try:
			# 请求头length取得
			length = len(self._FirstHeadStr_Computer_Local)
			# Connection状态取得
			connection = self._FirstHeadDict_Computer_Local.getTags('Connection')
			# ORRO请求头作成
			orrohead = ''
			if (connection == 'keep-alive' or connection == 'Keep-Alive'):
				orrohead = self.createOrroHead(length, True)
			else:
				G_Log.info( 'Request Head Connection is not keep-alive: %s. [HttpProxy.py:HttpProxy:processLocalToRemote]' %self._FirstHeadStr_Computer_Local)
				orrohead = self.createOrroHead(length, False)
			# ORRO head发送
			self._Socket_Local_Remote.send( orrohead )
			# >>>>>>>>>
			G_Log.debug( 'ORRO HEAD: \r\n%s' %orrohead )
			# <<<<<<<<<
			# 请求头发送
			self._Socket_Local_Remote.send( self._FirstHeadStr_Computer_Local )
			# >>>>>>>>>
			G_Log.debug( 'Request HEAD: \r\n%s' %self._FirstHeadStr_Computer_Local )
			# <<<<<<<<<
			# # 请求body发送
			# bodysizestr = self._FirstHeadDict_Computer_Local.getTags('Content-Length')
			# if (bodysizestr != None):
			# 持续连接数据发送
			while (self._Keep_Alive == True):
				buffer = self._Socket_Local_Computer.recv(S_RECV_MAXSIZE)
				if (len(buffer) <= 0):
					self._Keep_Alive = False
					break
				# buflength = len(buffer)
				# orrohead = self.createOrroHead(buflength, True)
				# self._Socket_Local_Remote.send( orrohead )
				self._Socket_Local_Remote.send( buffer )
		except Exception as e:
			G_Log.error( 'processLocalToRemote error! [HttpProxy.py:HttpProxy:processLocalToRemote] --> %s' %e )

		self._Keep_Alive = False
		self.stop()

	# Remote -> Local
	def processRemoteToLocal( self ):
		'''读取远程回复信息并发送给本地应用'''

		try:
			while( self._Keep_Alive == True ):
				# ORRO head读取
				orroresheadstr = ''
				while True:
					buffer = self._Socket_Local_Remote.recv(1)
					if (len(buffer) <= 0):
						G_Log.info( '_Socket_Local_Remote close of orro head! [HttpProxy.py:HttpProxy:processRemoteToLocal]')
						self._Keep_Alive = False
						break
					orroresheadstr = orroresheadstr + buffer;
					length = len(orroresheadstr)
					if (length >= 4):
						if 	orroresheadstr[length - 4] == '\r' and \
							orroresheadstr[length - 3] == '\n' and \
							orroresheadstr[length - 2] == '\r' and \
							orroresheadstr[length - 1] == '\n' :
							break
				# ORRO head分析
				orroresheaddict = Tool.HttpHead.HttpHead(orroresheadstr)
				# ORRO body读取
				orroresbodylength = int(orroresheaddict.getTags('Content-Length'))
				lengthtmp = 0
				orroresbodystr = ''
				while True:
					buffer = self._Socket_Local_Remote.recv(S_RECV_MAXSIZE)
					if (len(buffer) <= 0):
						G_Log.info( '_Socket_Local_Remote close of orro body! [HttpProxy.py:HttpProxy:processRemoteToLocal]')
						self._Keep_Alive = False
						break
					lengthtmp += len(buffer)
					orroresbodystr += buffer
					if (lengthtmp >= orroresbodylength):
						break
				# 数据返回给本地应用
				self._Socket_Local_Computer.send( orroresbodystr )

				# ORRO ProxyOrro-Connection 判断
				if (orroresheaddict.getTags('ProxyOrro-Connection') != 'keep-alive'):
					self._Keep_Alive = False
		except Exception as e:
			self._Keep_Alive = False
			G_Log.error( 'processRemoteToLocal error! [HttpProxy.py:HttpProxy:processRemoteToLocal] --> %s' %e )
			
		self.stop()


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

	def createOrroHead( self, length, proxyconnection ):
		'''生成ORRO头
		length         : bodysize
		proxyconnection: None - 不添加ProxyOrro-Connection
						 True - 添加ProxyOrro-Connection为keep-alive
						 False- 添加ProxyOrro-Connection为close

		注意：此处添加 Connection: close 头，每次重连ORRO服务。
		'''

		proxyorro = '\r\n'
		if (proxyconnection == True):
			proxyorro = 'ProxyOrro-Connection: keep-alive\r\n'
		elif (proxyconnection == False):
			proxyorro = 'ProxyOrro-Connection: close\r\n'
		headstr = 'POST http://192.168.1.125:5085/ORRO_HTTP HTTP/1.1\r\n'	\
				+ 'Host: ' + S_ORRO_HOST + ':' + str(S_ORRO_PORT) + '\r\n'	\
				+ 'Content-Length: ' + str(length) + '\r\n'					\
				+ 'Connection: close\r\n'									\
				+ proxyorro 												\
				+ '\r\n'
		return headstr
