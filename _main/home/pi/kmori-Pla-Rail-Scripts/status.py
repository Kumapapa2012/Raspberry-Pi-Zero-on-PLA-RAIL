#!/usr/bin/env python
import utils

print "Main Register:"
print utils.Get8830Status()
print "Fault Register:"
print utils.Get8830Status_Fault()
