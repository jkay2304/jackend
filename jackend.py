import asyncio
import json
import logging
import websockets

logging.basicConfig()

USERS = set()

FUNCTIONS = dict()

#wsconfig = websocketIO.WebsocketIO("birthday")

# Example:
# Jack = JackendServer(5011)
# Jack.registerAction("test", testfunctionname)
# Jack.start()
class JackendServer:
    def __init__(self, port):
        self.port = port

    def registerAction(self, function):
        FUNCTIONS[function.__name__] = function

    def start(self):
        start_server = websockets.serve(_start_websocket, "0.0.0.0", self.port)
        print("Server started on Port {}!".format(self.port))

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

# Example:
# async def testfunctionname(data, websocket):
#     Req = JackendRequest("testfunctionname", websocket)
#     Req.setMessage("Moin")
#     await Req.send()
class JackendRequest:
    def __init__(self, action, websocket):
        self.action = action
        self.status = True
        self.message = ""
        self.result = ""
        self.websocket = websocket

    def setError(self, message):
        self.status = False
        self.message = message

    def setMessage(self, message):
        self.message = message

    def setResult(self, result):
        self.result = result

    def getStatus(self):
        return self.status

    def getWsData(self):
        wsdata = {"action" : self.action, \
        "status" : self.status, \
        "message" : self.message, \
        "result" : self.result}
        return wsdata

    async def sendWithMessage(self, message):
        self.start = True
        self.setMessage(message)
        await self.send()

    async def sendWithError(self, message) :
        self.start = False
        self.setMessage(message)
        self.send()

    async def send(self) :
        wsdata = self.getWsData()
        print("SEND: {}".format(wsdata))
        await self.websocket.send(json.dumps(wsdata))



#==========================================================
# USE PYTHON3.6                
#==========================================================
async def _registerUser(websocket):
    USERS.add(websocket)
    Req = JackendRequest("register", websocket)
    await Req.sendWithMessage("Registred")

#==========================================================
async def _unregisterUser(websocket):
    USERS.remove(websocket)

#==========================================================
# get request from server
async def _start_websocket(websocket, path):
    # register(websocket) sends user_event() to websocket
    await _registerUser(websocket)
    try:
        async for message in websocket:
            if _isJasonValid(message):
                await _doAction(message, websocket)
            else :
                await _sendBadJson(message, websocket)
    finally:
        await _unregisterUser(websocket)

#==========================================================
def _isJasonValid(json_string) :
    try:
        json.loads(json_string)
    except ValueError:
        return False
    return True

#==========================================================
async def _sendBadJson(json_string, websocket) :

    Req = JackendRequest("badJson", websocket)
    Req.sendWithMessage("No valid json format.")
    
#==========================================================
async def _doAction(json_string, websocket) :
    print("GET:  {}".format(json_string))
    data = json.loads(json_string)

    action = data["action"]
    if action in FUNCTIONS:
        await FUNCTIONS[action](data, websocket)
    else:
        print("Function not registred:{}".format(action))
