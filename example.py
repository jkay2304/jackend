
from Jackend import Jackend

async def addition(Request):

    await Request.needAttributeOrSendError("number1", "INT", True)
    await Request.needAttributeOrSendError("number2", "INT", True)

    if Request.getStatus():
        print (Request.getAttribute("number1"))
        number = Request.getAttribute("number1") + Request.getAttribute("number2")

        Request.setMessage(number)

        await Request.send()



# Init
Server = Jackend(5011)

# Functions
Server.registerAction(addition)

# Start!
Server.start()

