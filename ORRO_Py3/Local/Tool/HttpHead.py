# !usr/bin/python
# -*-coding: utf-8-*-
# Filename: HttpHead.py

# std
import string

class HttpHead():
	'''http head info
	头名称规范化
	内部处理采用小写，输出时将头名称单词首字母大写，如：Content-Length

	getTags()
	getHeadStr()
	addHeadKey()
	delHeadKey()
	updateKey()
	updateKey2()'''

	# complete
	_Headcomplete = {}
	# headstring
	_HeadStr = None
	# headstr修改flag
	_HeadModify = False
	# Request?Response
	# True: Request ; Flase: Response
	_IsRequest = None

	def __init__( self, headstr = None ):
		if headstr == None:
			return

		self._Headcomplete = {}

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
			self._Headcomplete['status'] = Value1[0][9:]
		else :
			# Request
			self._IsRequest = True
			# 分析
			Value11 = Value1[0].split( ' ' )

			# Request 方法
			self._Headcomplete['method'] = Value11[0]
			
			# URL
			if( 3 > len( Value11 ) ):
				self._Headcomplete['url'] = None
			else:
				self._Headcomplete['url'] = Value11[1]

		# HTTP协议版本
		if( -1 != Value1[0].find( 'HTTP/1.0' ) ):
			self._Headcomplete['httpversion'] = 'HTTP/1.0'
		elif( -1 != Value1[0].find( 'HTTP/1.1' ) ):
			self._Headcomplete['httpversion'] = 'HTTP/1.1'

		# 其他头信息获取
		for i in range( 1, len(Value1) ):
			Value2 = Value1[i].split( ': ' )
			if( len(Value2) == 2 ):
				self._Headcomplete[Value2[0].lower()] = Value2[1]

	def getTags( self, tagname = None ):
		'''return Tag info 
		tagname为None时，以字典形式返回所有头信息'''

		try:
			if( tagname == None ):
				return( self._Headcomplete )
			else:
				return (self._Headcomplete.get(tagname.lower(), None))
		except:
			return( None )

	def getHeadStr( self ):
		'''return head string
		返回处理后的头信息，包含结尾的\r\n\r\n
		头名称单词首字母大写'''

		# Request Head String
		if self._HeadModify == True:
			self._HeadStr = self.headComposing( self._Headcomplete )
			self._HeadModify = False

		return( self._HeadStr )

	def addHeadKey( self, keypair = None ):
		'''在头信息末尾插入新条目'''

		if( keypair == None ):
			return

		count = keypair.find(': ')
		if( count == -1 ):
			return

		try:
			# 头字典追加
			self._Headcomplete[keypair[0:count].lower()] = keypair[count+2:]
			self._HeadModify = True
		except:
			pass

	def addHeadKey( self, key = None, value = None ):
		'''在头信息末尾插入新条目'''

		if( key == None ):
			return
		if( value == None ):
			return

		# 统一大小写
		key = key.lower()

		try:
			# 头字典追加
			self._Headcomplete[key] = value
			self._HeadModify = True
		except:
			pass

	def delHeadKey( self, key ):
		'''从头信息中删除条目'''

		if( key == None ):
			return

		# 统一大小写
		key = key.lower()

		# 从头信息词典中删除
		try:
			if key in self._Headcomplete:
				del self._Headcomplete[key]
				self._HeadModify = True
			else:
				return
		except:
			pass

	def updateKey( self, key, value):
		'''头信息变更,不存在则返回'''

		if (value == None):
			return

		# 统一大小写
		key = key.lower()

		# 头信息词典替换
		try:
			if key in self._Headcomplete:
				self._Headcomplete[key] = value
				self._HeadModify = True
		except:
			pass

	def updateKey2( self, key, value):
		'''头信息变更,不存在则追加'''

		if (value == None):
			return

		# 统一大小写
		key = key.lower()

		# 头信息词典替换
		try:
			if key in self._Headcomplete:
				self._Headcomplete[key] = value
			else:
				self.addHeadKey(key + ': ' + value)
				
			self._HeadModify = True
		except:
			pass


	def headComposing( self, headdic ):
		'''由头信息字典生成头信息字符串
		头名称单词首字母大写。'''

		headstr = ''

		if (self._IsRequest == True):
			# Method
			headstr = headdic['method']
			# Url
			headstr += ' ' + headdic['url']
			# Http Version
			headstr += ' ' + headdic['httpversion']
		else:
			# Http Version
			headstr += headdic['httpversion']
			# Status
			headstr += ' ' + headdic['status']
		# other
		headstr += '\r\n'
		for key in self._Headcomplete:
			if key == 'method' or key == 'url' or key == 'httpversion' or key == 'status':
				continue
			headstr += string.capwords(key, '-') + ': ' + headdic[key] + '\r\n'
		# end
		headstr += '\r\n'

		return headstr

class HttpHead2():
	'''http head info
	保持原有头名称的大小写

	getTags()
	getHeadStr()
	addHeadKey()
	delHeadKey()
	updateKey()
	updateKey2()'''

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

		self._Headcomplete = {}

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
			self._Headcomplete['httpversion'] = 'HTTP/1.0'
		elif( -1 != Value1[0].find( 'HTTP/1.1' ) ):
			self._Headcomplete['httpversion'] = 'HTTP/1.1'

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
				return (self._Headcomplete.get(tagname, None))
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

	def addHeadKey( self, keypair = None ):
		'''在头信息末尾插入新条目'''

		if( keypair == None ):
			return

		count = keypair.find(': ')
		if( count == -1 ):
			return

		# 头信息追加
		self._HeadStr = self._HeadStr[0:-2] + keypair + '\r\n\r\n'
		# 头字典追加
		self._Headcomplete[keypair[0:count]] = keypair[count+2:]

	def delHeadKey( self, key ):
		'''从头信息中删除条目'''

		if( key == None ):
			return

		# 不含有该条目则返回
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

	def updateKey( self, key, value):
		'''头信息变更,不存在则返回'''

		if (value == None):
			return

		# 不含有该条目则返回
		count = self._HeadStr.find( key )
		if( count == -1 ):
			return
		count1 = self._HeadStr[count:].find( '\r\n' )
		if( count1 == -1 ):
			return
		count1 = count + count1
		count2 = self._HeadStr[count:count1].find( ': ' )
		self._HeadStr = self._HeadStr[0:count+count2+2] + value + self._HeadStr[count1:]

		# 头信息词典替换
		try:
			self._Headcomplete[key] = value
		except:
			pass

	def updateKey2( self, key, value):
		'''头信息变更,不存在则追加'''

		if (value == None):
			return

		flg = True
		# 不含有该条目则增加
		count = self._HeadStr.find( key )
		if( count == -1 ):
			flg = False
		count1 = self._HeadStr[count:].find( '\r\n' )
		if( count1 == -1 ):
			flg = False

		if (flg == True):
			count1 = count + count1
			count2 = self._HeadStr[count:count1].find( ': ' )
			self._HeadStr = self._HeadStr[0:count+count2+2] + value + self._HeadStr[count1:]

			# 头信息词典替换
			try:
				self._Headcomplete[key] = value
			except:
				pass
		else:
			self.addHeadKey(key + ': ' + value)

