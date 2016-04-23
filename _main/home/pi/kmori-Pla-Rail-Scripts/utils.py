#!/usr/bin/env python
import smbus
import time

i2c = smbus.SMBus(1)
adr = 0x64

def Get8830Status():
	# Read Ctrl Register Value and returns motor status
	r = i2c.read_byte_data(adr,0)
	v = (r>>2) * 0.08
	s = ["Standby","Forward","Reverse","Brake"]
	d = s[r&3]
	return (v,d)

def Get8830Status_Fault():
	# Read Fault Register Value and returns motor status
	r = i2c.read_byte_data(adr,1)
        s = ["FAULT","OCP","UVLO","OTS","ILIMIT","UNUSE5","UNUSE6","CLEAR"]
	ret = ""
        for i in range(0,7):
		if ((r>>i)&1):
			ret = ret + s[i] + "|"
        return (r,ret)

def Set8830Status(v,d):
	# Write Ctrl register value and returns motor status
	# Check fault status
	vr = int(v*100) / 8

	s = ["Standby","Forward","Reverse","Brake"]
	si = s.index(d)
	print si
	r = (vr<<2)|si

	print r

	i2c.write_byte_data(adr,0,r)
	return Get8830Status()

def Clear8830Status_Fault():
	# Write Fault Register CLEAR bit and returns fault status
	r = i2c.write_byte_data(adr,1,0x80)
	time.sleep(1)
	return Get8830Status_Fault()

