from flask import Flask
from flask import request
from flask import render_template, send_file
import socket
import threading 

app = Flask(__name__)

IP = '192.168.43.100'
port = 1234

#setting up the connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, port))
server.listen()
new, address = server.accept()
print("Connect established with: ", address)

status = ""
statusR = False

array = []


@app.route("/on")
#turning on the sampling 
def turnOn():
   message = "SensorOn"
   
   new.sendall(str.encode(message))
   return "Sensor Turned On"
   
@app.route("/off")
#turning off sampling
def turnOff():
   message = "SensorOff"
   new.sendall(str.encode(message))
   return "Sensor Turned Off"
   
@app.route("/status")
#getting the status of the client
def getStatus():
   global statusR
   
   message = "Status"
   new.sendall(str.encode(message))
   
   while(not statusR):
      pass
   
   statusR = False
   
   return status
   
@app.route("/logs")
#getting the logs from the array
def logs():

   global array

   logs = "Time  | Light Reading |   Temparature Reading  |   Temparature in degrees Celcious  <br>"
   for i in array:
      split = i.split(";")
      logs = logs + "    " + split[0] + "    |    " + split[1] + "    | " + split[2] + " | " + split[3] + " | " + split[4] +"<br>"
   
   return logs
   
@app.route("/get-csv", methods=['GET','POST'])
#allowing for dowloading of the data
def download():
   return send_file("../log.csv",as_attachment=True,mimetype="text/csv")


@app.route("/exit")
#used to exit
def exit():
   message = "Exit"
   
   new.sendall(str.encode(message))
   return "Shutting Down"
   
@app.route("/")
#starts the thread
def main():   
    thread = threading.Thread(target = receive)
    thread.start()
    return render_template('Webserver.html', title='Webserver')
    
 #this function is used when a certain message is received from the client   
def receive():
   
   #opening the file that we will be writing in 
   file = open("/usr/src/app/log.csv", "w")
   file.write("Date;Time;Light Reading;Temparature Reading;Temparature in Degrees Celcius \n")
   file.close()
   
   global array, status, statusR, new
   
   with new:
   
      while(True) :
         
         data = new.recv(1024)
         data = data.decode("utf-8")
         p = "Data: " + data
         print(p)
      
         if(not data):
           pass        
      
         #checking if the message receive is a status message
         elif(data[0] == "S"):
            status = data
            statusR = True
         
         else:
           #if the message received is not a statuse then it is the data that must be written to a file
            if(len(array) == 10):
               array.pop(0)
         
            array.append(data)
         
            file = open("/usr/src/app/log.csv","a")
            file.write(data + '\n')
            file.close()
    
   quit()
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
quit()
   