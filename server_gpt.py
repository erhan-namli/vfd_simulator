from flask import Flask, render_template
from threading import Thread
import asyncio
from pymodbus import __version__ as pymodbus_version
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartTcpServer, StartAsyncTcpServer
from pymodbus.transaction import ModbusSocketFramer

app = Flask(__name__)

datablock = ModbusSequentialDataBlock(0x00, [16] * 100)
context = ModbusSlaveContext(
    di=datablock, co=datablock, hr=datablock, ir=datablock
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

@app.route('/')
def index():
    return render_template('index.html')

async def run_server():
    server = await StartAsyncTcpServer(
        context=context,
        identity=identity,
        address=('', 3030),
        framer=ModbusSocketFramer,
    )

    return server



def run_flask():
    app.run(debug=True)

if __name__ == "__main__":

    modbus_thread = Thread(target=lambda: asyncio.run(run_server()))
    flask_thread = Thread(target=run_flask)

    modbus_thread.start()
    flask_thread.start()

    modbus_thread.join()
    flask_thread.join()