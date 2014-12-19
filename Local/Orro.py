# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: Orro.py

import globals
import Tool.Logger
import Tool.HttpHead
import ProxyServer.ProxyServer

# 本地监视IP
SERVER_IP = '127.0.0.1'
# 本地监视端口
LISTENPORT = 5010
# 最大连接数
CONNECT_MAXNUMBER = 1024
# 超时
CONNECT_TIMEOUT = 10
# 最大读取字节数
RECV_MAXSIZE = 65535

def main():
	head = Tool.HttpHead.HttpHead()
	ORRO = ProxyServer.ProxyServer.H_C_ProxyServer( SERVER_IP, LISTENPORT, CONNECT_MAXNUMBER )
	ORRO.start()

if __name__ == '__main__':
    main()