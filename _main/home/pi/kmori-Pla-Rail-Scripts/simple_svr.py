#!/usr/bin/env python
# coding=utf-8
# Jurius Client for Pla-Rail
#
# kumapapa2012, Kenichi Mori
# 
#

from __future__ import print_function
import time
import commands
from contextlib import closing
import socket

host = '127.0.0.1'
backlog = 10
port = 10501

#
#       コマンド処理
#
def process_command (rcvmsg):
        #       最低限の処理
        # "GO_" あれば前進
        if ( rcvmsg.find("GO_") >=0 ):
                print(commands.getoutput("python start.py"))
        # "STOP_" あれば停止
        if ( rcvmsg.find("STOP_") >=0 ):
                print(commands.getoutput("python stop.py"))

#
#	接続
#

sock_svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

with closing(sock_svr):
	sock_svr.bind((host,port))
	sock_svr.listen(backlog)
	#
	#	メインループ
	#
	while True:
		print('==== ==== ==== Waiting for command ==== ==== ====')
		conn, addr = sock_svr.accept()
		print('==== ==== ==== Connection established ==== ==== ====')
		with closing(conn):
			rcvmsg = conn.recv(4096) # 4kB 固定。。。
			print ('Received %d bytes', len(rcvmsg))
			print ('==== ==== ====        DATA         ==== ==== ====')
			print (rcvmsg)
			process_command(rcvmsg)
