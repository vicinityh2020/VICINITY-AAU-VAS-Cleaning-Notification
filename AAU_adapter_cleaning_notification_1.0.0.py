from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import requests
import socket   
import json
import time
import threading

#define global vars default state
stopflag = 0

#define global OID of devices
OID_DoorSensor = '5875b07f-8a80-4860-8793-c75e569418cf'

#Enquire data and state from EMS
#Publish events to subscribers through VICINITY agnet
def timerfun_publishevent():
   global stopflag   
    
   #Inquire state data from Labview for Charging price
   handel_TCPclient_interruptthread.send(b'Read_EMSstat_NNN') 
   responsestring = handel_TCPclient_interruptthread.recv(11) 

   #Rearrange received data from EMS
   CleanRequirement = responsestring[10:11]

   #Derive System time
   ISOTIMEFORMAT = '%Y-%m-%d %X'        
   systemtime = time.strftime(ISOTIMEFORMAT,time.localtime())
   systemtime = str(systemtime)
   systemtime = bytes(systemtime, encoding = "utf8")
        
   if (CleanRequirement == b'Y'):          
   
       #Publish the alarm event
       hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_CN'}
       url = 'http://localhost:9997/agent/events/ClearingRequirment'     
       payload = b'{' + b'"clean":"required",' + b'"time":"'+ systemtime +b'"}'
       r=requests.request('PUT',url,headers=hd,data = payload)
       print(r.text)

   handel_timer_publishevent = threading.Timer(5,timerfun_publishevent,())         
   
   if stopflag==1:
        handel_timer_publishevent.cancel()
   else:
        handel_timer_publishevent.start()
   

#Handle the http requests from VICINITY agent 
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
 
    def do_GET(self):
        self.send_response(200)
        self.end_headers() 
 
    def do_POST(self):
        
        global stopflag
        
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        self.send_response(200)
        self.end_headers()
                  
        string = body.decode() #encode()
        string = json.loads(string)
        
        control_ID=string['control_ID']
        control_val=string['value']
        
        if (control_ID=='shutdown' and control_val=='1'):
            response = BytesIO()
            response.write(b'HTTP/1.1 200 OK/Server is shutdown successfully')
            self.wfile.write(response.getvalue())   
            httpd.shutdown
            httpd.socket.close()            
            print('AAU adapter is shutdown successfully!')
            stopflag = 1
    
        else:
            response = BytesIO()
            response.write(b'HTTP/1.1 406 Failed')
            self.wfile.write(response.getvalue())   
 
    def do_PUT(self):
               
        global OID_DoorSensor
        
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        self.send_response(200)
        self.end_headers()
        
        if (self.path.count(OID_DoorSensor) == 1):  #Freezer
            
            string = body.decode() #encode()
            print(string)
            
            if (string.count('door_activity_b0654854-a9ff-4ad7-99ca-9d71f94c4f53') == 1 and  string.count('False') == 1):     
                doorstate = b'O'   
                              
            
            elif (string.count('door_activity_b0654854-a9ff-4ad7-99ca-9d71f94c4f53') == 1 and  string.count('True') == 1):  
                doorstate = b'C'   
                             
            Finalsenddata = b'USet_DoorSen_' + doorstate + b'N' + b'N'   
            handel_TCPclient_mainthread.send(Finalsenddata)        
            
      
if __name__ == '__main__':
     #Create handel for TCP client to connect to Labview (main)  
     address = ('17486633in.iask.in', 31127)  
     handel_TCPclient_mainthread = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
     handel_TCPclient_mainthread.connect(address) 

     #Create handel for TCP client to connect to Labview (interrupt)
     address = ('17486633in.iask.in', 36539 )  
     handel_TCPclient_interruptthread = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
     handel_TCPclient_interruptthread.connect(address)  
        
     #Open the channel for publishing the Clearing Requirment event of AAU
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_CN'}
     url = 'http://localhost:9997/agent/events/ClearingRequirment'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
      
     #Door sensor(TINYM) is subscribed staticly  
     
     #start thread for publish event
     handel_timer_publishevent = threading.Timer(5,timerfun_publishevent,())  
     handel_timer_publishevent.start()

     #start main http server
     print('AAU Server is working!')
     httpd = HTTPServer(('localhost', 9995), SimpleHTTPRequestHandler)
     httpd.serve_forever()

  

