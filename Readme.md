## Synopsis

Cobalt Strike contains a new / experimental feature called external_c2. This bypasses the mallable profiles and allows the developper to craft it's own channels. 
This code is a POC, that in the end appeared to be the solution to a real life problem.

## Code Example

c2file.c: a C implementation of the client (the process in talking to beacon)
c2file_dll.c, c2file_dll.h, c2file.py: A python implementation of the client (using a dll, the process in talking to beacon) allowing for quick development of complex channels
python_c2ex.py: The server talking to the external_c2 plugin of teamserver.
externalc2_start.cna: the script needed to start the external_c2 on teamserver.

## Blog

Read our blog for more info: https://www.outflank.nl/publications/

## Installation

i686-w64-mingw32-gcc -shared c2file_dll.c -o c2file.dll


## Contributors

Thanks to @armitagehacker for providing info on external_c2 functionality including C sample code that was essentially to make this work.
Thanks to Marc Smeets (@mramsmeets), author of the blog and the one to implement this POC in a real assignment.
Code written by Mark Bergman (@xychix) but heavily relying on @armitagehacker initial C example.

## License

BSD license