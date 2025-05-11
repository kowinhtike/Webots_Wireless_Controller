from controller import Robot
from flask import Flask
from flask_socketio import SocketIO, send
import threading
import time

# Initialize Flask-SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Webots Robot
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Get motor devices
left_motor = robot.getDevice('left_motor')
right_motor = robot.getDevice('right_motor')

# Set motors to velocity control mode
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

# Set initial speed (radians per second)
speed = 5
current_command = 'S'

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

def run_webots():
    while robot.step(timestep) != -1:
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
