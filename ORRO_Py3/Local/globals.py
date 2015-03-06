# !usr/bin/python
# -*- coding: utf-8 -*-
# Filename: globals.py

# original
import Tool

# logger
G_Log = Tool.Logger.getLogger()
# 远端服务器地址
G_ORRO_R_HOST = '0.0.0.0'
# 远端服务器端口
G_ORRO_R_PORT = 0
# 本地监视IP
G_ORRO_L_SERVER_IP = '0.0.0.0'
# 本地监视端口
G_ORRO_L_LISTEN_PORT = 0
# 最大连接数
G_ORRO_L_CONNECT_MAXNUMBER = 0
# 积攒的数据队列
G_DEPOT_DATA = None