# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: HttpProxy.py

import socket
import sys
import threading

sys.path.append('..')
import Tool.HttpHead
import Tool.Logger
from globals import G_Log

# 最大读取字节数
RECV_MAXSIZE = 65535


class HttpProxy(object):
	"""docstring for HttpProxy"""
	
	_WorkerManagerLocalComputer = None

	_Local_Remote_Address = None
	_Socket_Local_Computer = None
	_Socket_Local_Remote = None
	_HeadStrFiest_Computer_Local = None
	_HeadDict_Computer_Local = None

	_ProcessLtoR = None
	_ProcessRtoL = None

	_Keep_Alive = None
	_IsWorker = None

	def __init__( self, socklc, headstr, workermanager ):
		self._Socket_Local_Computer = socklc
		self._HeadStrFiest_Computer_Local = headstr
		self._WorkerManagerLocalComputer = workermanager
		self._IsWorker = False

	def start( self ):
		try:
			# worker add
			ret = self._WorkerManagerLocalComputer.workadd()
			# >>>>>
			# print( '--add-- worklen: %s\n' %ret )
			# <<<<<
			self._IsWorker = True
		except Exception as e:
			self._IsWorker = False
			G_Log.error( 'Worker add error! [HttpProxy.py:HttpProxy:start] --> %s' %e )
			return

		# Fir Head Format
		self._HeadDict_Computer_Local = Tool.HttpHead.H_C_HTTP_HEAD( self._HeadStrFiest_Computer_Local )

		try:
			# Local - Remote Connect
			# 考虑Host中指定port的情况
			hosttmp = self._HeadDict_Computer_Local.getTags( 'Host' )
			host = hosttmp.split(':')
			if (len(host) > 1):
				self._Local_Remote_Address = ( host[0], int(host[1]) )
			else:
				self._Local_Remote_Address = ( self._HeadDict_Computer_Local.getTags( 'Host' ), 80 )
			self._Socket_Local_Remote = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self._Socket_Local_Remote.connect( self._Local_Remote_Address )

		except Exception as e:
			ret = self._WorkerManagerLocalComputer.workdel()
			# >>>>>
			# print( '--connect del-- worklen: %s\n' %ret )
			# <<<<<
			G_Log.error( 'socket connect error! [HttpProxy.py:HttpProxy:start] --> %s' %e )
			return

		# process thread
		self._ProcessLtoR = threading.Thread( target = self.processLocalToRemote )
		self._ProcessRtoL = threading.Thread( target = self.processRemoteToLocal )

		self._Keep_Alive = True
		self._ProcessLtoR.start()
		self._ProcessRtoL.start()

	def stop( self ):
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
				# >>>>>
				# print( '--del-- worklen: %s\n' %ret )
				# <<<<<
		except Exception as e:
			G_Log.error( 'HttpProxy stop err! [HttpProxy.py:HttpProxy:stop] --> %s' %e )

	# Local -> Remote
	def processLocalToRemote( self ):
		'''本地请求信息发送到远程'''

		# first
		head = Tool.HttpHead.H_C_HTTP_HEAD(self._HeadStrFiest_Computer_Local)
		head = self.toProxyConnection( None, head )
		self._Socket_Local_Remote.send( head.getHeadStr() )
		G_Log.debug( 'Local  ->Remote : %s' %head.getHeadStr() )
		#>>>>>>>>>>>>>>>>>>>>>
		# print( '-- 30 --: HeadStrFiest \n%s' %head.getHeadStr() )
		#<<<<<<<<<<<<<<<<<<<<<

		while( self._Keep_Alive == True ):
			try:
				# Request recv
				localtoremotedata = ''
				while( True ): # socket 保持连接
					localtoremotedata = self._Socket_Local_Computer.recv(RECV_MAXSIZE)
					G_Log.debug( 'Computer->Local   : %s' %localtoremotedata )
					if( localtoremotedata == '' ):
						# Computer断开socket
						# except中处理
						raise Exception( 'Computer socket stop!' )

					#>>>>>>>>>>>>>>>>>>>>>
					# print( '-- 31 --: localtoremotedata \n%s' %localtoremotedata )
					#<<<<<<<<<<<<<<<<<<<<<

					# 考虑一次socket recv不能完全读取数据的情况！
					# 

					# Connection -> Proxy-Connection
					#localtoremotedata = Tool.HttpHead.H_C_HTTP_HEAD(self._HeadStrFiest_Computer_Local)
					#localtoremotedata = self.toProxyConnection( localtoremotedata )

					# HTTP METHOD
					# GET
					if( localtoremotedata[0:3] == 'GET' ):
						self._HeadDict_Computer_Local = Tool.HttpHead.H_C_HTTP_HEAD( localtoremotedata )
						if( self._HeadDict_Computer_Local.getTags( 'Connection' ) == 'close' or self._HeadDict_Computer_Local.getTags( 'Connection' ) == 'Close'):
							self._Keep_Alive = False
						if( self._HeadDict_Computer_Local.getTags( 'Proxy-Connection' ) == 'close' or self._HeadDict_Computer_Local.getTags( 'Connection' ) == 'Close'):
							self._Keep_Alive = False

						# Connection -> Proxy-Connection
						localtoremotedatatmp = self.toProxyConnection( None, self._HeadDict_Computer_Local ).getHeadStr()

						self._Socket_Local_Remote.send( localtoremotedatatmp )
						G_Log.debug( 'Local  ->Remote : %s' %localtoremotedatatmp )

						# 不保持连接
						# self._Keep_Alive = False

					# POST
					elif( localtoremotedata[0:4] == 'POST' ):
						self._Socket_Local_Remote.send( localtoremotedata )

					# OTHER
					else:
						self._Socket_Local_Remote.send( localtoremotedata )
				
			except Exception as e:
				#>>>>>>>>>>>>>>>>>>>>>
				# print( '-- 25 --: %s\n' %e )
				#<<<<<<<<<<<<<<<<<<<<<
				G_Log.info( 'processLocalToRemote info! [HttpProxy.py:HttpProxy:processLocalToRemote] --> %s' %e )
				self._Keep_Alive = False

		self.stop()

	# Remote -> Local
	def processRemoteToLocal( self ):
		'''读取远程回复信息并发送给本地应用'''

		while( self._Keep_Alive == True ):
			try:
				localtoremotedata = ''
				while( self._Keep_Alive ): # socket 保持连接
					localtoremotedata = self._Socket_Local_Remote.recv(RECV_MAXSIZE)
					if( localtoremotedata == '' ):
						# Computer断开socket
						# except中处理
						raise Exception( 'Remote socket stop!' )

					if( localtoremotedata[0:5] != 'HTTP/' ):
						self._Socket_Local_Computer.send( localtoremotedata )
						break

					# 考虑数据未读取完成，再次循环读取
					# headsize = localtoremotedata.find( '\r\n\r\n' )
					# if( headsize == -1 ):
					# 	continue

					self._HeadDict_Computer_Local = Tool.HttpHead.H_C_HTTP_HEAD( localtoremotedata )

					if( self._HeadDict_Computer_Local.getTags( 'Connection' ) == 'close' or self._HeadDict_Computer_Local.getTags( 'Connection' ) == 'Close' ):
						self._Keep_Alive = False
					if( self._HeadDict_Computer_Local.getTags( 'Proxy-Connection' ) == 'close' or self._HeadDict_Computer_Local.getTags( 'Connection' ) == 'Close' ):
						self._Keep_Alive = False

					self._Socket_Local_Computer.send( localtoremotedata )
					G_Log.debug( 'Remote->Local   : %s' %localtoremotedata )

					#>>>>>>>>>>>>>>>>>>>>>
					# print( '-- 40 --: localtoremotedata \n%s' %localtoremotedata )
					#<<<<<<<<<<<<<<<<<<<<<

			except Exception as e:
				#>>>>>>>>>>>>>>>>>>>>>
				# print( '-- 45 --: %s\n' %e )
				#<<<<<<<<<<<<<<<<<<<<<
				G_Log.info( 'processRemoteToLocal info! [HttpProxy.py:HttpProxy:processRemoteToLocal] --> %s' %e )
				self._Keep_Alive = False

		self.stop()

	def toProxyConnection( self, keep, head ):
		'''替换头信息Connection为Proxy-Connection
		keep: None - 设置为原来信息
			  True - 保持连接
			  False- 不保持连接'''

		try:
			connection = head.getTags( 'Connection' )
		except Exception as e:
			G_Log.warn( 'Connection Get error! [HttpProxy.py:HttpProxy:toProxyConnection] --> %s' %e )
			return head

		if( connection == None ):
			return head

		try:
			# Connection删除
			head.delHeadKey( 'Connection' )
			# Proxy-Connection添加
			if( keep == True ):
				head.addHeadKey( 'Proxy-Connection: ' + 'keep-alive')
			elif( keep == False ):
				head.addHeadKey( 'Proxy-Connection: ' + 'close')
			else:
				head.addHeadKey( 'Proxy-Connection: ' + connection)

		except Exception as e:
			G_Log.error( 'Connection -> Proxy-Connection error! [HttpProxy.py:HttpProxy:toProxyConnection] --> %s' %e )
			return head
		return head
		