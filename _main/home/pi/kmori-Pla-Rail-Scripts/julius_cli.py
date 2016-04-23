#!/usr/bin/env python
# coding=utf-8
# Jurius Client for Pla-Rail
#
# kumapapa2012, Kenichi Mori
# 
#

import socket
import time
import commands

host = '127.0.0.1'
port = 10500

#
#       コマンド処理
#
def process_command (rcvmsg):
        #       最低限の処理
        #       fail なら終了
        if ( rcvmsg.find("RECOGFAIL") >=0 ):
                print 'Failed to recognize.'
                return

        # "GO_" あれば前進
        if ( rcvmsg.find("GO_") >=0 ):
                print commands.getoutput("python start.py")
        # "STOP_" あれば停止
        if ( rcvmsg.find("STOP_") >=0 ):
                print commands.getoutput("python stop.py")

#
#	接続
#
sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

retry=0
while retry < 5:
	try:
		sock_cli.connect((host,port))
	except:
		time.sleep(3)
		retry=retry+1
	else:
		break

if(retry >= 5):
	exit

#
#	メインループ
#
while True:
	print '==== ==== ==== Waiting for command ==== ==== ===='
	rcvmsg = sock_cli.recv(4096) # 4kB 固定。。。
	print 'Received %d bytes', len(rcvmsg)
	print '==== ==== ====        DATA         ==== ==== ===='
	# print rcvmsg
	process_command(rcvmsg)
	
sock_cli.close()

