#!/usr/bin/env python

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit, \
    disconnect

# Import dronekit
from dronekit import connect, VehicleMode
from pymavlink import mavutil
from collections import deque
from VideoGrabber import Camera
from rangefinder import rangefinder
import serial
from binascii import unhexlify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

thread_vehicle_state = None
connection_string = None
sitl = None
state = None
vehicle = None

# frame buffer (in seconds)
buffer_len = 25*5
buffer = deque(maxlen=buffer_len)

#Start SITL if no connection string specified
# if not connection_string:
#     import dronekit_sitl
#     sitl = dronekit_sitl.start_default()
#     connection_string = sitl.connection_string()
    

# Connect to the Vehicle. 
#   Set `wait_ready=True` to ensure default attributes are populated before `connect()` returns.
# print "\nConnecting to vehicle on: %s" % connection_string
# vehicle = connect(connection_string, wait_ready=True)
# vehicle.wait_ready('autopilot_version')

def get_serial_data():
    serial = rangefinder('/dev/tty.usbserial-00000000', 115200, 8, 1, 2, '0a4f4e0a', 1)
    serial.fetch_response()

get_serial_data() 

def get_vehicle_state():
    if vehicle.location.global_relative_frame.lat == None:
        raise Exception('no position info')
    if vehicle.armed == None:
        raise Exception('no armed info')
    return {
        "armed": vehicle.armed,
        "alt": vehicle.location.global_relative_frame.alt,
        "mode": vehicle.mode.name,
        "heading": vehicle.heading or 0,
        "lat": vehicle.location.global_relative_frame.lat,
        "lon": vehicle.location.global_relative_frame.lon,
        "gps_eph": vehicle.gps_0.eph,
        "gps_epv": vehicle.gps_0.epv,
        "gps_fix_type": vehicle.gps_0.fix_type,
        "nast": vehicle.gps_0.satellites_visible,
        "battery_level": vehicle.battery.level,
        "battery_voltage": vehicle.battery.voltage,
        "groundspeed": vehicle.groundspeed
    }

def gen_state_thread():
    """Send server generated events to clients."""
    count = 0
    global state
    while True:
        time.sleep(1)
        count += 1
        state = get_vehicle_state()
        socketio.emit('my response',
                      {'data': state, 'count': count},
                      namespace='/test')                             
# def get_onboard_camera():
#     import numpy as np
#     import cv2

#     cam = cv2.VideoCapture(0)
#     while True:
#         ret_val, img = cam.read()
#         if mirror: 
#             img = cv2.flip(img, 1)
#         cv2.imshow('vehicle onboard camera', img)
#         if cv2.waitKey(1) == 27: 
#             break  # esc to quit
#     cv2.destroyAllWindows() 

@app.route('/')
def index():
    global thread_vehicle_state
    if thread_vehicle_state is None:
        thread_vehicle_state = Thread(target=gen_state_thread)
        thread_vehicle_state.daemon = True
        thread_vehicle_state.start()
    return render_template('index.html')

@socketio.on('my event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my broadcast event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


def main():
    app.run(threaded=True, host='0.0.0.0', port=3000)

if __name__ == '__main__':
    socketio.run(main(), debug=True)

