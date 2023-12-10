import logging

from pymodbus import __version__ as pymodbus_version
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification

from pymodbus.server import StartAsyncTcpServer

import asyncio
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS

from threading import Thread

from pymodbus.transaction import ModbusSocketFramer

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

class CallbackDataBlock(ModbusSequentialDataBlock):
    """A datablock that stores the new value in memory,.
    and passes the operation to a message queue for further processing.
    """

    def __init__(self, queue, addr, values):
        """Initialize."""
        self.queue = queue
        super().__init__(addr, values)

    def setValues(self, address, value):
        """Set the requested values of the datastore."""
        super().setValues(address, value)

        if(address == 1):
            print("debug socketio1")

            address_changed(1, 5)

        if (address == 2):
            print("debug socketio2")

        txt = f"Callback from setValues with address {address}, value {value}"
        _logger.debug(txt)

    def getValues(self, address, count=1):
        """Return the requested values from the datastore."""
        result = super().getValues(address, count=count)
        txt = f"Callback from getValues with address {address}, count {count}, data {result}"
        _logger.debug(txt)
        return result

    def validate(self, address, count=1):
        """Check to see if the request is in range."""
        result = super().validate(address, count=count)
        txt = f"Callback from validate with address {address}, count {count}, data {result}"
        _logger.debug(txt)
        return result


def address_changed(address, data):

    if(address==1):

        socketio.emit('update_status', {'value': data})
        print("address_changed_function")

    pass

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('address_1_changed')
def handle_address_1_change(data):
    print("Socket func")
    value = data['value']
    # Do something with the value when address is 1
    print(f"Received address_1_changed event with value: {value}")

    # Update the HTML element with the received value
    socketio.emit('update_status', {'value': value}, broadcast=True)

    # Add your logic here

async def setup_server():

    queue = asyncio.Queue()

    #datablock = ModbusSequentialDataBlock(0x00, [16] * 100)

    block = CallbackDataBlock(queue, 0x00, [16] *5)

    context = ModbusSlaveContext(
        di=block, co=block, hr=block, ir=block
    )

    context = ModbusServerContext(slaves=context, single=True)

    identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server",
            "MajorMinorRevision": pymodbus_version,
        }
    )

    try:

        server = await StartAsyncTcpServer(
            context=context,  # Data storage
            identity=identity,  # server identify
            address=('', 3030),  # listen address
            framer=ModbusSocketFramer,  # The framer strategy to use
        )

    except Exception as e:

        print(f"Error starting server: {e}")

        return None  # Return None in case of an error

    return server

async def run_server():

    await setup_server()




if __name__ == "simple_server":

    print("debug ", __name__)

    modbus_thread = Thread(target=lambda: asyncio.run(setup_server()))

    modbus_thread.start()

    socketio.run(app, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)