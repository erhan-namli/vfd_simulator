#!/usr/bin/env python3
import asyncio
import logging
from flask import Flask, render_template
from flask_socketio import SocketIO

import helper
from pymodbus import __version__ as pymodbus_version
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSparseDataBlock,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import (
    StartAsyncTcpServer,
    StartAsyncUdpServer,
    StartAsyncSerialServer,
    StartAsyncTlsServer,
)

logging.basicConfig()
_logger = logging.getLogger(__file__)
_logger.setLevel(logging.INFO)

# Flask setup
app = Flask(__name__)
socketio = SocketIO(app)


def emit_data(data):
    socketio.emit("update_data", {"data": data})


@app.route("/")
def index():
    return render_template("index.html")


def setup_server(description=None, context=None, cmdline=None):
    """Run server setup."""
    args = helper.get_commandline(server=True, description=description, cmdline=cmdline)
    if context:
        args.context = context
    if not args.context:
        _logger.info("### Create datastore")
        # The datastores only respond to the addresses that are initialized
        # If you initialize a DataBlock to addresses of 0x00 to 0xFF, a request to
        # 0x100 will respond with an invalid address exception.
        # This is because many devices exhibit this kind of behavior (but not all)
        if args.store == "sequential":
            # Continuing, use a sequential block without gaps.
            datablock = ModbusSequentialDataBlock(0x00, [16] * 100)
        elif args.store == "sparse":
            # Continuing, or use a sparse DataBlock which can have gaps
            datablock = ModbusSparseDataBlock({0x00: 0, 0x05: 1})
        elif args.store == "factory":
            # Alternately, use the factory methods to initialize the DataBlocks
            # or simply do not pass them to have them initialized to 0x00 on the
            # full address range::
            datablock = ModbusSequentialDataBlock.create()

        if args.slaves:
            # The server then makes use of a server context that allows the server
            # to respond with different slave contexts for different slave ids.
            # By default it will return the same context for every slave id supplied
            # (broadcast mode).
            # However, this can be overloaded by setting the single flag to False and
            # then supplying a dictionary of slave id to context mapping::
            #
            # The slave context can also be initialized in zero_mode which means
            # that a request to address(0-7) will map to the address (0-7).
            # The default is False which is based on section 4.4 of the
            # specification, so address(0-7) will map to (1-8)::
            context = {
                0x01: ModbusSlaveContext(
                    di=datablock,
                    co=datablock,
                    hr=datablock,
                    ir=datablock,
                ),
                0x02: ModbusSlaveContext(
                    di=datablock,
                    co=datablock,
                    hr=datablock,
                    ir=datablock,
                ),
                0x03: ModbusSlaveContext(
                    di=datablock,
                    co=datablock,
                    hr=datablock,
                    ir=datablock,
                    zero_mode=True,
                ),
            }
            single = False
        else:
            context = ModbusSlaveContext(
                di=datablock, co=datablock, hr=datablock, ir=datablock
            )
            single = True

        # Build data storage
        args.context = ModbusServerContext(slaves=context, single=single)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    # If you don't set this or any fields, they are defaulted to empty strings.
    # ----------------------------------------------------------------------- #
    args.identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server",
            "MajorMinorRevision": pymodbus_version,
        }
    )
    return args


async def run_async_server(args):
    txt = f"### start ASYNC server, listening on {args.port} - {args.comm}"
    _logger.info(txt)

    if args.comm == "tcp":
        address = (args.host if args.host else "", args.port if args.port else None)
        server = await StartAsyncTcpServer(
            context=args.context,
            identity=args.identity,
            address=address,
            framer=args.framer,
        )
    elif args.comm == "udp":
        address = (
            args.host if args.host else "127.0.0.1",
            args.port if args.port else None,
        )
        server = await StartAsyncUdpServer(
            context=args.context,
            identity=args.identity,
            address=address,
            framer=args.framer,
        )
    elif args.comm == "serial":
        server = await StartAsyncSerialServer(
            context=args.context,
            identity=args.identity,
            port=args.port,
            framer=args.framer,
            baudrate=args.baudrate,
        )
    elif args.comm == "tls":
        address = (args.host if args.host else "", args.port if args.port else None)
        server = await StartAsyncTlsServer(
            context=args.context,
            host="localhost",
            identity=args.identity,
            address=address,
            framer=args.framer,
            certfile=helper.get_certificate("crt"),
            keyfile=helper.get_certificate("key"),
        )
    return server


async def async_helper():
    _logger.info("Starting...")
    run_args = setup_server(description="Run asynchronous server.")
    server = await run_async_server(run_args)

    # Start the Flask app and socketio in a separate thread
    socketio.start_background_task(target=app.run, debug=True, use_reloader=False)

    try:
        # Wait for the server to finish
        await server.serve_forever()
    finally:
        # When the server is closed, stop the Flask app and socketio
        socketio.stop()


@socketio.on("connect")
def handle_connect():
    _logger.info("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    _logger.info("Client disconnected")


if __name__ == "__main__":
    # Start the asyncio event loop
    loop = asyncio.get_event_loop()

    # Run the async_helper function in the event loop
    loop.run_until_complete(async_helper())
