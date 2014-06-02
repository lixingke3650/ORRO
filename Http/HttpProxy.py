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

	def __init__( self, socklc, headstr, workermanager ):
		self._Socket_Local_Computer = socklc
		self._HeadStrFiest_Computer_Local = headstr
		self._WorkerManagerLocalComputer = workermanager

		

	def start( self ):
		# Fir Head Format
		self._HeadDict_Computer_Local = Tool.HttpHead.H_C_HTTP_HEAD( self._HeadStrFiest_Computer_Local )

		try:
			# Local - Remote Connect
			self._Local_Remote_Address = ( self._HeadDict_Computer_Local.getTags( 'Host' ), 80 )
			self._Socket_Local_Remote = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self._Socket_Local_Remote.connect( self._Local_Remote_Address )

		except:
			self._WorkerManagerLocalComputer.workdel()
			G_Log.error( 'socket connect error! [HttpProxy.py:HttpProxy:start]' )


		# first head send
		#self._Socket_Local_Remote.send( HeadStrFiest_Local_Computer )

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

			self._WorkerManagerLocalComputer.workdel()
		except Exception as e:
			G_Log.error( 'HttpProxy stop err! [HttpProxy.py:HttpProxy:stop]' )
			pass

	# Local -> Remote
	def processLocalToRemote( self ):
		# first
		self._Socket_Local_Remote.send( self._HeadStrFiest_Computer_Local )
		#>>>>>>>>>>>>>>>>>>>>>
		print( '-- 30 --: HeadStrFiest \n%s' %self._HeadStrFiest_Computer_Local )
		#<<<<<<<<<<<<<<<<<<<<<

		while( self._Keep_Alive == True ):
			try:
				# Request recv
				localtoremotedata = ''
				while( True ): # socket 保持连接
					localtoremotedata = self._Socket_Local_Computer.recv(RECV_MAXSIZE)
					if( localtoremotedata == '' ):
						# Computer断开socket
						# except中处理
						raise Exception( 'Computer socket stop!' )

					# 考虑一次socket recv不能完全读取数据的情况！
					# 

					# HTTP METHOD
					# GET
					if( localtoremotedata[0:3] == 'GET' ):
						self._HeadDict_Computer_Local = Tool.HttpHead.H_C_HTTP_HEAD( localtoremotedata )
						if( self._HeadDict_Computer_Local.getTags( 'Connection' ) == 'close' ):
							self._Keep_Alive = False
						if( self._HeadDict_Computer_Local.getTags( 'Proxy-Connection' ) == 'close' ):
							self._Keep_Alive = False

						self._Socket_Local_Remote.send( localtoremotedata )

					# POST
					elif( localtoremotedata[0:4] == 'POST' ):
						self._Socket_Local_Remote.send( localtoremotedata )

					# OTHER
					else:
						self._Socket_Local_Remote.send( localtoremotedata )
				
			except Exception as e:
				#>>>>>>>>>>>>>>>>>>>>>
				print( '-- 25 --: %s\n' %e )
				#<<<<<<<<<<<<<<<<<<<<<
				self._Keep_Alive = False

		self.stop()

	# Remote -> Local
	def processRemoteToLocal( self ):
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

					if( self._HeadDict_Computer_Local.getTags( 'Connection' ) == 'close' ):
						self._Keep_Alive = False
					if( self._HeadDict_Computer_Local.getTags( 'Proxy-Connection' ) == 'close' ):
						self._Keep_Alive = False

					self._Socket_Local_Computer.send( localtoremotedata )

					#>>>>>>>>>>>>>>>>>>>>>
					print( '-- 40 --: localtoremotedata \n%s' %localtoremotedata )
					#<<<<<<<<<<<<<<<<<<<<<

			except Exception as e:
				#>>>>>>>>>>>>>>>>>>>>>
				print( '-- 45 --: %s\n' %e )
				#<<<<<<<<<<<<<<<<<<<<<
				self._Keep_Alive = False

		self.stop()
