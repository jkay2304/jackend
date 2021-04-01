
import pymysql

from jackend import JackendServer


async def addition(Request):

    if await Request.hasAttributeWithError("number1", "INT", True):
        return False 
    if await Request.hasAttributeWithError("number2", "INT", True):
        return False 

    print (Request.getAttribute("number1"))
    number = Request.getAttribute("number1") + Request.getAttribute("number2")

    Request.setMessage(number)

    await Request.send()

# Init
Server = JackendServer(5011)

# Functions
Server.registerAction(addition)

# Start!
Server.start()


