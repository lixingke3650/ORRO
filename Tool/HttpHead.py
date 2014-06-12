# !usr/bin/python
# -*-coding: utf-8-*-
# Filename: HttpHead.py

class H_C_HTTP_HEAD():
	'''http head info

	getTags(): return Tag info'''

	# complete
	_Headcomplete = {}
	# headstart
	_HeadStr = None
	# Request?Response
	# True: Request ; Flase: Response
	_IsRequest = None

	def __init__( self, headstr = None ):
		if headstr == None:
			return

		count = headstr.find( '\r\n\r\n' )
		if(  count == -1 ):
			return

		self._HeadStr = headstr[0:count+4]

		Value1 = self._HeadStr[0:count].split( '\r\n' )

		# Head头信息提取 Request?Response
		count = Value1[0].find( 'HTTP/' )
		if( count == -1 ):
			return
		elif( count == 0 ):
			# Response
			self._IsRequest = False
			# Response 状态
			self._Headcomplete['Status'] = Value1[0][9:]
		else :
			# Request
			self._IsRequest = True
			# 分析
			Value11 = Value1[0].split( ' ' )

			# Request 方法
			self._Headcomplete['Method'] = Value11[0]
			
			# URL
			if( 3 > len( Value11 ) ):
				self._Headcomplete['Url'] = None
			else:
				self._Headcomplete['Url'] = Value11[1]

		# HTTP协议版本
		if( -1 != Value1[0].find( 'HTTP/1.0' ) ):
			self._Headcomplete['HttpVersion'] = 'HTTP/1.0'
		elif( -1 != Value1[0].find( 'HTTP/1.1' ) ):
			self._Headcomplete['HttpVersion'] = 'HTTP/1.1'

		# 其他头信息获取
		for i in range( 1, len(Value1) ):
			Value2 = Value1[i].split( ': ' )
			if( len(Value2) == 2 ):
				self._Headcomplete[Value2[0]] = Value2[1]

	def getTags( self, tagname = None ):
		'''return Tag info 
		tagname为None时，以字典形式返回所有头信息'''

		try:
			if( tagname == None ):
				return( self._Headcomplete )
			else:
				return( self._Headcomplete[ tagname ] )
		except:
			return( None )

	def getHeadStr( self ):
		'''return head string
		返回处理后的头信息，包含结尾的\r\n\r\n.'''

		if( self._IsRequest == False ):
			# Response 情况暂不处理
			# return( None )
			return( self._HeadStr )
		else:
			# Request Head String
			return( self._HeadStr )

	def addHeadKey( self, key = None ):
		'''在头信息末尾插入新条目'''

		if( key == None ):
			return

		count = key.find(': ')
		if( count == -1 ):
			return

		# 头信息追加
		self._HeadStr = self._HeadStr[0:-2] + key + '\r\n\r\n'
		# 头字典追加
		self._Headcomplete[key[0:count]] = key[count+2:]

	def delHeadKey( self, key ):
		'''从头信息中删除条目'''

		if( key == None ):
			return

		# 不含有该条目则删除
		count = self._HeadStr.find( key )
		if( count == -1 ):
			return
		count1 = self._HeadStr[count:].find( '\r\n' )
		if( count1 == -1 ):
			return

		count1 = count + count1
		# 该条目位于最后
		if( len(self._HeadStr) - count1 < len('\r\n\r\n') + 1 ): 
			self._HeadStr = self._HeadStr[0:count] + '\r\n\r\n'
		# 该条目位于中间
		else:
			self._HeadStr = self._HeadStr[0:count] + self._HeadStr[count1+2:]

		# 从头信息词典中删除
		try:
			del self._Headcomplete[key]
		except:
			pass
