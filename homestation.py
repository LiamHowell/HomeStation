'''
HomeStation MicroPython Library
Written by Liam Howell
Project Write-up: https://core-electronics.com.au/projects/homestation/
Full Repo: https://github.com/LiamHowell/HomeStation

Should host a web-page with Sensor readouts, and a colour picker for the RGB Module

Adapted from the adaptation:
https://core-electronics.com.au/projects/wifi-garage-door-controller-with-raspberry-pi-pico-w-smart-home-project/
Adapted from examples in: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
'''




'''
TODO
# Break code into classes - seperate ones for async tasks, loading the webserver, and generating the content
# Finish standardisation of the input functions (raw string/dict/ named tuple?/both?)
# Add some easy input options - button, RGB, text input
# Create a template sensor and input part of the webpage, java gets locked in regardless
# Make the page look cleaner
# Make the blink status indicate what is happening more clearly, document this
# Add 2 levels of optional debugging - print statements and optional OLED code for each, pass out with a getter function? ref PiicoDev

Functions
# General creation of webserver - input WLAN?
Sensor data - input dict
'''

from machine import Pin
import utime
import network
import uasyncio as asyncio

from utime import sleep


class homestation_base():
    def __init__(self,ssid,password,sensorDict):
        self.ssid = ssid
        self.password = password
        self.sensorDict = sensorDict
        
    # Build a set of sensors
    def sensDict2Vals(self,sensorDict):
        sensOut = {}
        for i,j in sensorDict.items():
            if callable(j):
                sensOut[i]=j()
            elif type(j) == type([]):
                sensOut[i] = sensorDict.get('.'+j[0])()[j[1]]
        return sensOut

    def sensVals2PrntLst(self,sensOut):
        valLst = []
        for i,j in sensOut.items():
            if (i[0] != '.'):
                valLst.append([i,j])
        return valLst

    def getSensorsHTML(self,sensDict):
        # Convert sensor dict to list without parent functions
        sensValLst = self.sensVals2PrntLst(self.sensDict2Vals(sensDict))
        
        ret_str = ''
        for i in sensValLst:
            ret_str += '<p>'
            ret_str += i[0]+str(i[1])
            ret_str += '</p>'
        return ret_str

    def requestBreakdown(self,request):
        return request.split()

    async def _connect_to_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.config(pm = 0xa11140)  # Diable powersave mode
        wlan.connect(self.ssid, self.password)
        
        # Wait for connect or fail
        max_wait = 10
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print('Waiting for connection...')
            sleep(1)
        # Handle connection error
        if wlan.status() != 3:
            raise RuntimeError('WiFi connection failed')
        else:
            print('Connected')
            status = wlan.ifconfig()
            print('IP = ' + status[0])
            # self.showIP(status[0])

    async def _serve_client(self,reader, writer, sensors=None):
        print("Client connected")
        request_line = await reader.readline()
        print("Request:", request_line)
        # We are not interested in HTTP request headers, skip them
        while await reader.readline() != b"\r\n":
            pass
        request = str(request_line)
        cmd_rq = self.requestBreakdown(request)
        
        if cmd_rq[1] == '/': #Make 2 standard ones and the option to add more easily
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            response = html.format(sensors=sensors,script=script)
            #pushLight(leds,[[0,0,0]]*3)
            writer.write(response)
            
        elif cmd_rq[1] == '/sensors':
            htmlify_sensVal = self.getSensorsHTML(sensors)
            sensorUpdateStr = '<p>{}</p>'.format(htmlify_sensVal)
            writer.write(sensorUpdateStr)

        elif cmd_rq[1][:15] == '/led_set?state=':
            lightOut = strToLight(cmd_rq[1][15:])
            #pushLight(leds,[lightOut]*3)

        await writer.drain()
        await writer.wait_closed()
        print("Client disconnected")
        
    def showIP(ipStr):
        try:
            display.text(ipStr, 0,0, 1)
            display.show()
        except:
            print('OLED not plugged in')
    
    
    async def homestationInit(self):
        print('Connecting to WiFi...')
        print(self.ssid,self.password)
        asyncio.create_task(self._connect_to_wifi())

        print('Setting up webserver...')
        asyncio.create_task(asyncio.start_server(lambda r,w: self._serve_client(r,w,sensors=self.sensorDict), "0.0.0.0", 80))

        while True:
            await asyncio.sleep(0.5)






# Run the server
def homestation_Run(ssid,password,sensorData):
    hs = homestation_base(ssid,password,sensorData)
    try:
        asyncio.run(hs.homestationInit())
    finally:
        asyncio.new_event_loop()



html = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>PicoW | HomeStation</title></head>
<body> <h2>HomeStation</h2>
<p id="sensors">Getting sensor state...</p>
{script}
</body>
</html>
"""

colour = '''
<label for="colorWell">LED Colour:</label>
<input type="color" value="#ff0000" id="colorWell">
'''

script = '''<script>
let colorWell;
const defaultColor = "#000000";
window.addEventListener("load", startup, false);
function startup() {
    colorWell = document.querySelector("#colorWell");
    colorWell.value = defaultColor;
    colorWell.addEventListener("input", updateFirst, false);
    colorWell.select();
}
function updateFirst(event) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        document.getElementById("state").innerHTML = this.responseText;
        }
    };
    xhttp.open("GET", "led_set?state=" + String(event.target.value).substr(1), true);
    xhttp.send();
}
setInterval(function() {
  getSensors();
}, 3000);
function getSensors() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("sensors").innerHTML = this.responseText;
    }
  };
  xhttp.open("GET", "sensors", true);
  xhttp.send();
}
</script>
'''

