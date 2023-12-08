import asyncio
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

async def background_task():
    count = 0
    while True:
        count += 1
        socketio.emit('update_data', {'data': count}, namespace='/')
        await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(background_task())
    socketio.start_background_task(target=app.run, debug=True, use_reloader=False)
    socketio.run(app, debug=True, use_reloader=False)
