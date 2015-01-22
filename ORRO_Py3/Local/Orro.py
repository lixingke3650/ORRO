#! C:\Python\Python3\python
# -*-coding: utf-8-*-
# FileName: Orro.py

# std
import sys
# original
import globals
import Tool
import ProxyServer.ProxyServer

__Version__ = '0.1'

def loadConfig():
	config = Tool.Config.ConfigIni('Config.ini')
	globals.G_ORRO_L_SERVER_IP = config.getKey('ORRO_L','SERVER_IP')
	globals.G_ORRO_L_LISTEN_PORT = config.getKeyInt('ORRO_L','LISTEN_PORT')
	globals.G_ORRO_L_CONNECT_MAXNUMBER = config.getKeyInt('ORRO_L','CONNECT_MAXNUMBER')
	globals.G_ORRO_R_HOST = config.getKey('ORRO_R','HOST')
	globals.G_ORRO_R_PORT = config.getKeyInt('ORRO_R','PORT')
	globals.G_Log.setLevel(config.getKey('ORRO_L','LOG_LEVEL'))	

def main():
	print('This is Proxy Service Of ORRO.')
	print('(https://github.com/lixingke3650/ORRO)')
	print('ORRO Local Server Version: ' + __Version__)
	print('Python Version: ' + sys.version)
	print('')

	loadConfig()

	print('=====================================================')
	print('* Local Server IPAddr: %s' % globals.G_ORRO_L_SERVER_IP)
	print('* Local Server Port: %d' % globals.G_ORRO_L_LISTEN_PORT)
	print('* Local Server C_Max: %d' % globals.G_ORRO_L_CONNECT_MAXNUMBER)
	print('* Remote Server Host: %s' % globals.G_ORRO_R_HOST)
	print('* Remote Server Port: %d' % globals.G_ORRO_R_PORT)
	print('* Local Log Level: %s' % globals.G_Log.getLevel())
	print('=====================================================')
	print('')
	
	head = Tool.HttpHead.HttpHead()
	ORRO = ProxyServer.ProxyServer.H_C_ProxyServer( globals.G_ORRO_L_SERVER_IP, globals.G_ORRO_L_LISTEN_PORT, globals.G_ORRO_L_CONNECT_MAXNUMBER )
	ORRO.start()

	print('ORRO Proxy Service Start.')
	print('')

if __name__ == '__main__':
    main()