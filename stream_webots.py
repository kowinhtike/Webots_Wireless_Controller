from controller import Robot
from flask import Flask,Response
from flask_socketio import SocketIO, send
import threading
import time
import cv2
import numpy as np

# Initialize Flask-SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Webots Robot
robot = Robot()
timestep = int(robot.getBasicTimeStep())
# Camera Setup
camera = robot.getDevice('camera')
camera.enable(timestep)


# Get motor devices
left_motor = robot.getDevice('left_motor')
right_motor = robot.getDevice('right_motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
speed = 5
current_command = 'S'

latest_frame = None
frame_lock = threading.Lock()

# Robot movement functions
def goForward():
    left_motor.setVelocity(speed)
    right_motor.setVelocity(speed)

def goBackward():
    left_motor.setVelocity(speed * -1)
    right_motor.setVelocity(speed * -1)

def stop():
    left_motor.setVelocity(0)
    right_motor.setVelocity(0)

def goRight():
    left_motor.setVelocity(speed * 1/2)
    right_motor.setVelocity(0)

def goLeft():
    left_motor.setVelocity(0)
    right_motor.setVelocity(speed * 1/2)

# SocketIO event handlers
@socketio.on('status')
def handle_status(msg):
    print('Received message: ' + msg)
    send('Echo: ' + msg)

@socketio.on('control')
def handle_control(msg):
    global current_command
    print('Command received: ' + msg)
    current_command = msg
    send(f'Command {msg} received')

# MJPEG Stream Endpoint
def generate_frames():
    while True:
        time.sleep(0.05)
        with frame_lock:
            if latest_frame is not None:
                frame_copy = latest_frame.copy()
                # Convert Webots image to OpenCV BGR format
                _, buffer = cv2.imencode('.jpg',frame_copy)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
        <html>
        <head><title>Webots Robot Stream</title></head>
        <body>
            <h1>Live Camera Stream</h1>
            <img src="/video_feed" width="640" height="480">
        </body>
        </html>
    '''

def run_webots():
    global latest_frame,frame_lock
    while robot.step(timestep) != -1:
        image = camera.getImage()
        width = camera.getWidth()
        height = camera.getHeight()
        
        # Convert Webots image to OpenCV BGR format
        img_array = np.frombuffer(image, np.uint8).reshape((height, width, 4))
        frame = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
        with frame_lock:
            latest_frame = frame
        if current_command == 'F':
            goForward()
        elif current_command == 'B':
            goBackward()
        elif current_command == 'L':
            goLeft()
        elif current_command == 'R':
            goRight()
        else:
            stop()

def run_flask():
    socketio.run(app, host='0.0.0.0', port=3000,allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    # Start Webots controller in a separate thread
    webots_thread = threading.Thread(target=run_webots)
    webots_thread.daemon = True
    webots_thread.start()
    
    # Start Flask-SocketIO in the main thread
    run_flask()
