#!/usr/bin/python
#-*- coding: utf-8 -*-
#Filename: Orro_R.py

# sys
import socket
import webob
# import msvcrt
# import os
# original
import Logger
import HttpHead

# 二进制文件处理
# msvcrt.setmode( 0, os.O_BINARY )

Log = Logger.getLogger()

class ApplicationHTTP():
	_BUFFER_SIZE = 4096
	_Environ = None
	_ResLength = 0
	_Socket_R = None
	_Response = ['']

	def __call__(self, environ, start_response):
		self._Environ = environ
		self._ResLength = 0
		self._Response = ['']
		self._Socket_R = None

		Log.debug('ApplicationHTTP  __call__ START ')

		try :
			# # ORRO 头信息获取
			# http_orro_head_str = self.getOrroHead()
			# http_orro_head_dict = HttpHead.HttpHead(http_orro_head_str)
			# http_request_length = http_orro_head_dict.getTags('Content-Length')
			# # >>>>
			# Log.debug('http_orro_head_str: ' + http_orro_head_str);
			# # <<<<
			# 请求的head信息获取
			http_request_head_str = self.getReqHead()
			http_request_head_dict = HttpHead.HttpHead(http_request_head_str)
			http_requestbody_length = 0
			if (http_request_head_dict.getTags('Content-Length') != None):
				http_requestbody_length = int(http_request_head_dict.getTags('Content-Length'))
			# >>>>
			Log.debug('http_request_head_str: \r\n' + http_request_head_str);
			# <<<<
			# 请求Address作成
			hosttmp = http_request_head_dict.getTags('Host').split(':')
			port = 80
			if (len(hosttmp) > 1):
				port = int(hosttmp[1])
			address = (hosttmp[0], port)
			# 与请求方建立连接
			self._Socket_R = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self._Socket_R.connect(address)
			# 请求head信息发送
			self._Socket_R.send(http_request_head_str)
			# 请求body信息发送
			if (http_requestbody_length > 0):
				lengthtmp = 0
				while True:
					buffer = environ['wsgi.input'].read(self._BUFFER_SIZE)
					if (buffer == None):
						break
					if (len(buffer) <= 0):
						break
					# >>>>
					Log.debug("environ['wsgi.input']: " + buffer);
					# <<<<
					self._Socket_R.send(buffer)
					lengthtmp += len(buffer)
					if (lengthtmp >= http_requestbody_length):
						break
			# response读取
			# response head 读取
			http_response_head = self.getResHead()
			# >>>>
			Log.debug('http_response_head: \r\n' + http_response_head);
			# <<<<
			self._Response.append(http_response_head)
			http_response_head_dict = HttpHead.HttpHead(http_response_head)
			http_responsebody_length = 0
			if (http_response_head_dict.getTags('Content-Length') != None):
				http_responsebody_length = int(http_response_head_dict.getTags('Content-Length'))
			# response body 读取
			if (http_responsebody_length > 0):
				lengthtmp = 0
				while True:
					buffer = self._Socket_R.recv(self._BUFFER_SIZE)
					if (len(buffer) <= 0):
						break
					lengthtmp += len(buffer)
					self._Response.append(buffer)
					if (lengthtmp >= http_responsebody_length):
						break
				self._ResLength += lengthtmp
			# 断开请求连接
			self._Socket_R.close()
			self._Socket_R = None
			# 数据返回
			# >>>>
			Log.debug('self._ResLength: ' + str(self._ResLength));
			# <<<<
			status = '200 OK'
			response_headers = [('Content­type','text/plain'),("Content-Length", str(self._ResLength)),('ProxyOrro-Connection','keep-alive')]
			start_response(status, response_headers)
			# >>>>
			Log.debug('self._Response: \r\n' + b'-+-'.join(self._Response));
			# <<<<
			return iter(self._Response)

		except Exception as e :
			Log.error('[Orro_R:ApplicationHTTP:__call__] --> e:%s' %e)
			# for key in environ:
			# 	Log.debug( key )
			# 	Log.debug( environ[key] )
			data = 'ORRO_HTTP: ERROR'
			start_response("200 OK", 
				[
					("Content-Type", "text/html"),
					("Content-Length", str(len(data)))
				]
			)
			return iter([data])

	def getReqHead(self):
		reqhead = ''
		try:
			while True:
				buffer = self._Environ['wsgi.input'].read(1)
				if (len(buffer) <= 0):
					break
				reqhead = reqhead + buffer;
				length = len(reqhead)
				if (length >= 4):
					if 	reqhead[length - 4] == '\r' and \
						reqhead[length - 3] == '\n' and \
						reqhead[length - 2] == '\r' and \
						reqhead[length - 1] == '\n' :
						break
			return reqhead
		except Exception as e:
			Log.error('[Orro_R:ApplicationHTTP:getReqHead] --> e:%s' %e)
			return None

	def getResHead(self):
		reshead = ''
		try:
			while True:
				buffer = self._Socket_R.recv(1)
				if (len(buffer) <= 0):
					break
				reshead = reshead + buffer;
				length = len(reshead)
				if (length >= 4):
					if 	reshead[length - 4] == '\r' and \
						reshead[length - 3] == '\n' and \
						reshead[length - 2] == '\r' and \
						reshead[length - 1] == '\n' :
						break
			self._ResLength = length
			return reshead
		except Exception as e:
			Log.error('[Orro_R:ApplicationHTTP:getResHead] --> e:%s' %e)
			return None

class ApplicationHTTPS():
	def __call__(self, environ, start_response):
		data = 'HTTPS'

		start_response("200 OK", 
			[
				("Content-Type", "text/html"),
				("Content-Length", str(len(data)))
			]
		)
		return iter([data])

class ApplicationERR():
	def __call__(self, environ, start_response):
		data = '<html><body><h1>ORRO REMOTE ERROR!</h1></body></html>'

		start_response("200 OK", 
			[
				("Content-Type", "text/html"),
				("Content-Length", str(len(data)))
			]
		)
		return iter([data])

class ApplicationREF():
	def __call__(self, environ, start_response):
		data = '<script language="javascript" type="text/javascript">window.location.href="https://www.google.com";</script>'

		start_response("200 OK", 
			[
				("Content-Type", "text/html"),
				("Content-Length", str(len(data)))
			]
		)
		return iter([data])

def app(environ, start_response):
	# POST 以外的请求不处理
	if (environ['REQUEST_METHOD'] != 'POST'):
		application = ApplicationREF()
	elif (environ['wsgi.url_scheme'] == 'http'):
		if (environ['PATH_INFO'] == '/ORRO_HTTP'):
			# HTTP
			application = ApplicationHTTP()
		elif (environ['PATH_INFO'] == '/ORRO_HTTPS'):
			# HTTPS
			application = ApplicationHTTPS()
		else :
			application = ApplicationERR()
	else :
		application = ApplicationERR()

	return (application(environ, start_response))
