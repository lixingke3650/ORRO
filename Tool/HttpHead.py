# !usr/bin/python
# -*-coding: utf-8-*-
# Filename: HttpHead.py

class H_C_HTTP_HEAD():
	'''http head info

	getTags(): return Tag info'''

	# Method Url HttpVersion Status Host
	# headprimary = {}
	# Other
	# headaffix = {}

	# complete
	headcomplete = 	{}

	def __init__( self, headstr=None ):
		if headstr == None:
			return

		count = headstr.find( '\r\n\r\n' )
		if(  count == -1 ):
			return

		Value1 = headstr[0:count].split( '\r\n' )

		# Head头信息提取 Request?Response
		count = Value1[0].find( 'HTTP/' )
		if( count == -1 ):
			return
		elif( count == 0 ):
			# Response 状态
			self.headcomplete['Status'] = Value1[0][9:]
		else :
			Value11 = Value1[0].split( ' ' )

			# Request 方法
			self.headcomplete['Method'] = Value11[0]
			
			# URL
			if( 3 > len( Value11 ) ):
				self.headcomplete['Url'] = None
			else:
				self.headcomplete['Url'] = Value11[1]

		# HTTP协议版本
		if( -1 != Value1[0].find( 'HTTP/1.0' ) ):
			self.headcomplete['HttpVersion'] = 'HTTP/1.0'
		elif( -1 != Value1[0].find( 'HTTP/1.1' ) ):
			self.headcomplete['HttpVersion'] = 'HTTP/1.1'

		# 其他头信息获取
		for i in range( 1, len(Value1) ):
			Value2 = Value1[i].split( ': ' )
			if( len(Value2) == 2 ):
				self.headcomplete[Value2[0]] = Value2[1]

	def getTags( self, tagname=None ):
		'''return Tag info 
		tagname为None时，以字典形式返回所有头信息'''

		try:
			if( tagname == None ):
				return( self.headcomplete )
			else:
				return( self.headcomplete[ tagname ] )
		except:
			return( None )