import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
import time
import datetime
from mqtt_init import * # נניח שהגדרות הברוקר שלך כאן

# משתנים גלובליים
global clientname, CONNECTED
CONNECTED = False
r = random.randint(100000, 999999)  # שיהיה אקראי כל פעם
clientname = "TEMP_client-" + str(r)
TEMP_topic = 'pr/home/5976397/temperature'
update_rate = 5000  # מילישניות

class Mqtt_client():
    def __init__(self):
        self.broker = ''
        self.topic = ''
        self.port = ''
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''

    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def set_broker(self, value):
        self.broker = value
    def set_port(self, value):
        self.port = value
    def set_clientName(self, value):
        self.clientName = value
    def set_username(self, value):
        self.username = value
    def set_password(self, value):
        self.password = value
    def set_subscribeTopic(self, value):
        self.subscribeTopic = value
    def set_publishTopic(self, value):
        self.publishTopic = value
    def set_publishMessage(self, value):
        self.publishMessage = value

    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)

    def on_connect(self, client, userdata, flags, rc):
        global CONNECTED
        if rc == 0:
            print("Connected OK")
            CONNECTED = True
            self.on_connected_to_form()
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        global CONNECTED
        CONNECTED = False
        print("Disconnected result code " + str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("Message from:" + topic, m_decode)
        mainwin.subscribeDock.update_mess_win(m_decode)

    def connect_to(self):
        self.client = mqtt.Client(client_id=clientname, clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker", self.broker)
        self.client.connect(self.broker, self.port)

    def disconnect_from(self):
        self.client.disconnect()

    def start_listening(self):
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def subscribe_to(self, topic):
        if CONNECTED:
            self.client.subscribe(topic)
        else:
            print("Can't subscribe. Connection should be established first")

    def publish_to(self, topic, message):
        if CONNECTED:
            self.client.publish(topic, message)
        else:
            print("Can't publish. Connection should be established first")

class ConnectionDock(QDockWidget):
    """Temperature Sensor Emulator"""
    def __init__(self, mc):
        QDockWidget.__init__(self)
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)

        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)

        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)

        self.eClientID = QLineEdit()
        self.eClientID.setText(clientname)

        self.eUserName = QLineEdit()
        self.eUserName.setText(username)

        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)

        self.eConnectbtn = QPushButton("Connect", self)
        self.eConnectbtn.setToolTip("Click to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")

        self.ePublisherTopic = QLineEdit()
        self.ePublisherTopic.setText(TEMP_topic)

        self.TemperatureLevel = QLineEdit()
        self.TemperatureLevel.setText('')

        formLayout = QFormLayout()
        formLayout.addRow("Connect to Broker", self.eConnectbtn)
        formLayout.addRow("Publish topic", self.ePublisherTopic)
        formLayout.addRow("Temperature (°C)", self.TemperatureLevel)

        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Temperature Sensor Emulator")

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")

    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())
        self.mc.connect_to()
        self.mc.start_listening()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.mc = Mqtt_client()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(update_rate)

        self.setGeometry(100, 400, 300, 150)
        self.setWindowTitle('Temperature Sensor Emulator')

        self.connectionDock = ConnectionDock(self.mc)
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

    def update_data(self):
        temperature_level = round(random.uniform(0, 90), 1)  # סימולציה של קריאות טמפרטורה (צלזיוס)
        current_data = f"Temperature: {temperature_level} °C"
        print('Publishing:', current_data)
        self.connectionDock.TemperatureLevel.setText(str(temperature_level))
        self.mc.publish_to(TEMP_topic, current_data)

app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()