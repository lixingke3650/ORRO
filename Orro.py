# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: Orro.py

import globals
import Tool.Logger
import Tool.HttpHead
import ProxyServer.ProxyServer


def main():
	head = Tool.HttpHead.H_C_HTTP_HEAD()
	ORRO = ProxyServer.ProxyServer.H_C_ProxyServer()
	ORRO.start()

if __name__ == '__main__':
    main()