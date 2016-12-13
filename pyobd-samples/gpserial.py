import serial
def latDD(x):
  D = int(x[1:3])
  M = int(x[3:5])
  S = float(x[5:])
  DD = D + float(M)/60 + float(S)/3600
  return DD
def longDD(x):
  D = int(x[1:4])
  M = int(x[4:6])
  S = float(x[6:])
  DD = D + float(M)/60 + float(S)/3600
  return DD

# Expression
ser = serial.Serial('/dev/ttyUSB0', 4800, timeout = 5)
line = ser.readline()
splitline = line.split(',')
while 1:
       if splitline[0] == '$GPGGA':
         latsub=""
         longsub=""
         latitude = splitline[3]+ splitline[2]
         latDirec = splitline[3]
         if latDirec == "S":
            latsub = "-"
         # print "latitude="+str(latitude)
         latdec = latsub+str(latDD(latitude))
         print latdec
         # print "latitude direction="+latDirec
         longitude = splitline[5]+ splitline[4]
         longdec = longDD(longitude)
         #print longdec
         #print "longitude="+longitude
         longDirect = splitline[5]
         if longDirect == "W":
            longsub = "-"
         #print "longitude direction="+longDirect
         longdec = longsub+str(longDD(longitude))
         print longdec
         # print line
         #break
 
