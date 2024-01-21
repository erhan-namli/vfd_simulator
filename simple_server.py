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

from flask import request, jsonify

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

## STATES
address_1_state = 0


## VARIABLES
cal_data_forward = 1

cal_data_backward = 1

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

        solve_and_emit(address, value)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cal_data_forward', methods=['POST'])
def forward_endpoint():

    global cal_data_forward

    data = request.get_json()

    # Assuming the data you're interested in is in 'value' field
    value = data.get('value')

    # Print the received value to the terminal
    print("Received value from forward_endpoint:", value)

    cal_data_forward = value

    return jsonify({"status": "success"})

@app.route('/cal_data_backward', methods=['POST'])
def backward_endpoint():

    global cal_data_backward

    data = request.get_json()

    # Assuming the data you're interested in is in 'value' field
    value = data.get('value')

    # Print the received value to the terminal
    print("Received value from backward_endpoint:", value)

    cal_data_backward = value

    return jsonify({"status": "success"})

@app.route('/cal_data_backward', methods=['POST'])
def test_endpoint():

    global cal_data

    data = request.get_json()

    # Assuming the data you're interested in is in 'value' field
    value = data.get('value')

    # Print the received value to the terminal
    print("Received value from test endpoint:", value)

    cal_data = value

    return jsonify({"status": "success"})

async def setup_server():

    queue = asyncio.Queue()

    block = CallbackDataBlock(queue, 0x00, [16] *200)

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

def solve_and_emit(address, value):

    global address_1_state
    global cal_data_forward
    global cal_data_backward

    print("address", address, "value", value)

    if(address == 140 and value == [3]):

        socketio.emit('modbus_server_connected')

    if(address == 140 and value == [0]):
      
        socketio.emit('modbus_server_disconnected')

    if(address==1 and value == [1]):
        address_1_state = 1

    if (address == 1 and value == [0]):
        address_1_state = 0
        socketio.emit('stop')

    if(address==2 and value == [420]):
        socketio.emit('forward', {'value': value, 'cal_data_forward': int(cal_data_forward)})

    if (address == 2 and value == [65116]):
        socketio.emit('backward', {'value': value, 'cal_data_backward': int(cal_data_backward)})

if __name__ == "__main__":

    print("debug ", __name__)

    modbus_thread = Thread(target=lambda: asyncio.run(setup_server()))

    modbus_thread.start()

    socketio.run(app, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)