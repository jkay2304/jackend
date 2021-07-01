import asyncio
import json
import logging
import websockets

# Libary for Websocket IO

logging.basicConfig()

USERS = set()

FUNCTIONS = dict()

#wsconfig = websocketIO.WebsocketIO("birthday")

# Example:
# Jack = JackendServer(5011)
# Jack.registerAction("test", testfunctionname)
# Jack.start()
class Jackend:
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
# async def testfunctionname(Request):
#     Request.setMessage("Moin")
#     await Request.send()
class JackendRequest:
    # Init (private)
    def __init__(self, action, attributes, websocket):
        self.websocket = websocket
        self.action = action
        self.attributes = attributes
        self.status = True
        self.message = ""
        self.result = ""
    # check if request has the attribute <attribute>, if not then send answer
    async def needAttributeOrSendError(self, attribute, attributeType, NotNull):
        error, errorMessage = self.needAttribute(attribute, attributeType, NotNull)
        if error:
            await self.sendWithError(errorMessage)
    # check if request has the attribute <attribute>
    def needAttribute(self, attribute, attributeType, NotNull):
        err = False
        errMsg = ""
        if NotNull and attribute not in self.attributes:
            err = True
            errMsg = "Attribut missing: {}".format(attribute)
        elif not self.attributes[attribute]:
            err = True
            errMsg = "Attribut is null: {}".format(attribute)
        else:
            if attributeType == "INT":
                if not _isNumber(self.attributes[attribute]): # not name of attribut but attribut itself?
                    err = True
                    errMsg = "Datatype is not INT: {}={}".format(attribute, self.attributes[attribute])
            elif attributeType == "DATE":
                if not _isDateValid(self.attributes[attribute]):
                    err = True
                    errMsg = "Datatype is not DATE: {}={}".format(attribute, self.attributes[attribute])
            elif attributeType != "STRING":
                err = True
                errMsg = "JACKEND ERROR: Can't check for Datatype {}. INT|STRING|DATE".format(attributeType)
        return err, errMsg # Error
    # get the value of the given key
    def getAttribute(self, attribute):
        if attribute in self.attributes:
            return self.attributes[attribute]
        else:
            print("JACKEND ERROR: No attribute {} in Request.".format(attribute))
            return ""
    # set message to <message> and status to false
    def setErrorMessage(self, message):
        self.status = False
        self.message = message
    # set message to <message>
    def setMessage(self, message):
        self.message = message
    # set result to <result>
    def setResult(self, result):
        self.result = result
    # get status
    def getStatus(self):
        return self.status
    # instantly send with <message> and status true
    async def sendWithMessage(self, message):
        self.status = True
        self.setMessage(message)
        await self.send()
    # instantly send with <message> and status false
    async def sendWithError(self, message) :
        self.status = False
        self.setMessage(message)
        await self.send()
    # send to websocket
    async def send(self) :
        wsdata = self._getWsData()
        print("SEND: {}".format(wsdata))
        await self.websocket.send(json.dumps(wsdata))
    # build the request
    def _getWsData(self):
        wsdata = {"action" : self.action, \
        "status" : self.status, \
        "message" : self.message, \
        "result" : self.result}
        return wsdata

#==========================================================
# USE PYTHON3.6                
#==========================================================
async def _registerUser(websocket):
    USERS.add(websocket)
    Request = JackendRequest("register", "", websocket)
    await Request.sendWithMessage("Registered")

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
async def prepareNewRequest(action, websocket)  :   
        return JackendRequest(action, "", websocket)

#==========================================================
async def _sendBadJson(json_string, websocket) :

    Request = JackendRequest("badJson", "", websocket)
    await Request.sendWithMessage("No valid json format.")
    
#==========================================================
async def _doAction(json_string, websocket) :
    print("GET:  {}".format(json_string))
    attributes = json.loads(json_string)

    action = attributes["action"]
    if action in FUNCTIONS:
        Request = JackendRequest(action, attributes, websocket)
        await FUNCTIONS[action](Request)
    else:
        err = "Function not registered: '{}'".format(action)
        Request = JackendRequest("MissingFunction", "", websocket)
        await Request.sendWithMessage(err)

#==========================================================
def _isDateValid(checkDate) :
    import datetime
    isCorrectDate = None

    # 0123456789
    # 2020-09-06
    if len(checkDate) != 10:
        return False

    if checkDate[4] != "-" or checkDate[7] != "-":
        return False

    year = checkDate[0:4]
    month = checkDate[5:7]
    day = checkDate[8:10]

    if not year.isdigit() or not month.isdigit() or not day.isdigit():
        return False

    try:
        datetime.datetime(int(year),int(month),int(day))
        isCorrectDate = True
    except ValueError:
        isCorrectDate = False
    return isCorrectDate

#==========================================================
def _isNumber(string):
    return str(string).isdigit()
