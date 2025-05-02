import sys
import random
import datetime
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
from mqtt_init import * 
from kitchen_monitor_db import create_connection, init_db, store_data, fetch_data

# משתנים גלובליים
global clientname, CONNECTED, DB_NAME
CONNECTED = False
r = random.randint(100000, 999999)
clientname = "KitchenMonitor_client-" + str(r)
DB_NAME = "kitchen_data.db"

# נושאי MQTT
gas_sensor_topic = 'pr/home/5976397/gas'
smoke_sensor_topic = 'pr/home/5976397/smoke'
temperature_sensor_topic = 'pr/home/5976397/temperature'
warning_topic = 'pr/kitchen/warnings'
alarm_topic = 'pr/kitchen/alarms'


def time_format():
    return f'{datetime.datetime.now()}  |> '


class Mqtt_client():
    def __init__(self):
        self.broker = ''
        self.port = ''
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopics = []  
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_message_from_broker = None 

    # Setters and getters
    def set_on_message_from_broker(self, on_message_from_broker):
        self.on_message_from_broker = on_message_from_broker

    def get_broker(self):
        return self.broker

    def set_broker(self, value):
        self.broker = value

    def get_port(self):
        return self.port

    def set_port(self, value):
        self.port = value

    def get_clientName(self):
        return self.clientName

    def set_clientName(self, value):
        self.clientName = value

    def get_username(self):
        return self.username

    def set_username(self, value):
        self.username = value

    def get_password(self):
        return self.password

    def set_password(self, value):
        self.password = value

    def get_subscribeTopics(self): 
        return self.subscribeTopics

    def set_subscribeTopics(self, value):  
        self.subscribeTopics = value

    def get_publishTopic(self):
        return self.publishTopic

    def set_publishTopic(self, value):
        self.publishTopic = value

    def get_publishMessage(self):
        return self.publishMessage

    def set_publishMessage(self, value):
        self.publishMessage = value

    def on_log(self, client, userdata, level, buf):
        print(f"log: {buf}")

    def on_connect(self, client, userdata, flags, rc):
        global CONNECTED
        if rc == 0:
            print("connected OK")
            CONNECTED = True
            # לאחר ההתחברות, יש לרשום לנושאים
            for topic in self.subscribeTopics:  
                client.subscribe(topic)  
            # Notify the form
            if self.on_message_from_broker:
                self.on_message_from_broker("connected", "Connected to Broker")
        else:
            print(f"Bad connection Returned code={rc}")
            if self.on_message_from_broker:
                self.on_message_from_broker("error", f"Connection error: {rc}")

    def on_disconnect(self, client, userdata, flags, rc=0):
        global CONNECTED
        CONNECTED = False
        print(f"DisConnected result code {rc}")
        if self.on_message_from_broker:
            self.on_message_from_broker("disconnected", "Disconnected from Broker")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print(f"message from:{topic} {m_decode}")
        if self.on_message_from_broker:
            self.on_message_from_broker(topic, m_decode)

    def connect_to(self):
        # Init paho mqtt client class
        self.client = mqtt.Client(client_id=clientname, clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        try:
            self.client.connect(self.broker, self.port)  # connect to broker
        except Exception as e:
            print(f"{time_format()} Error connecting to broker: {e}")
            if self.on_message_from_broker:
                self.on_message_from_broker("error", f"Connection error: {e}")

    def disconnect_from(self):
        try:
            self.client.disconnect()
        except Exception as e:
            print(f"{time_format()} Error disconnecting from broker: {e}")
            if self.on_message_from_broker:
                self.on_message_from_broker("error", f"Disconnection error: {e}")

    def start_listening(self):
        try:
            self.client.loop_start()
        except Exception as e:
            print(f"{time_format()} Error starting listening loop: {e}")
            if self.on_message_from_broker:
                self.on_message_from_broker("error", f"Error starting listener: {e}")

    def stop_listening(self):
        try:
            self.client.loop_stop()
        except Exception as e:
            print(f"{time_format()} Error stopping listening loop: {e}")
            if self.on_message_from_broker:
                self.on_message_from_broker("error", f"Error stopping listener: {e}")

    def subscribe_to(self, topic): 
        if CONNECTED:
            try:
                self.client.subscribe(topic)
            except Exception as e:
                print(f"{time_format()} Error subscribing to topic {topic}: {e}")
                if self.on_message_from_broker:
                    self.on_message_from_broker("error", f"Error subscribing to {topic}: {e}")
        else:
            print("Can't subscribe. Connection should be established first")

    def publish_to(self, topic, message):
        if CONNECTED:
            try:
                self.client.publish(topic, message)
            except Exception as e:
                print(f"{time_format()} Error publishing to topic {topic}: {e}")
                if self.on_message_from_broker:
                    self.on_message_from_broker("error", f"Error publishing to {topic}: {e}")
        else:
            print("Can't publish. Connection should be established first")


# --- GUI Classes ---
class ConnectionDock(QDockWidget):
    """Connection settings dock."""

    def __init__(self, mc, main_gui):
        QDockWidget.__init__(self)
        self.mc = mc
        self.main_gui = main_gui
        self.mc.set_on_message_from_broker(self.on_message_from_broker)  # Receive messages

        self.eHostInput = QLineEdit(broker_ip)
        self.eHostInput.setInputMask('999.999.999.999')
        self.ePort = QLineEdit(broker_port)
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.eClientID = QLineEdit(clientname)
        self.eUserName = QLineEdit(username)
        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)
        self.eConnectbtn = QPushButton("Connect", self)
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")

        formLayot = QFormLayout()
        formLayot.addRow("Host", self.eHostInput)
        formLayot.addRow("Port", self.ePort)
        formLayot.addRow("Client ID", self.eClientID)
        formLayot.addRow("User Name", self.eUserName)
        formLayot.addRow("Password", self.ePassword)
        formLayot.addRow("Turn On/Off", self.eConnectbtn)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Connect")

    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())
        self.mc.connect_to()
        self.mc.start_listening()
        # Subscribe to all relevant topics
        self.mc.set_subscribeTopics([gas_sensor_topic, smoke_sensor_topic, temperature_sensor_topic, warning_topic, alarm_topic])  # Set the topics list
        for topic in self.mc.get_subscribeTopics():
            self.mc.subscribe_to(topic)

    def on_message_from_broker(self, topic, message):
        """Handle messages from the MQTT broker.  Update GUI and store."""
        if topic == gas_sensor_topic:
            try:
                gas_level = float(message.split(":")[1].strip().replace('%', ''))
                self.main_gui.update_gas_level(gas_level)  # Call the method in main GUI
                # Generate warning/alarm and store to DB
                warning, alarm = generate_warning_alarm(gas_level=gas_level)
                store_data(DB_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), gas_level, None, None, warning, alarm)
                if warning:
                    self.main_gui.add_warning(warning)
                if alarm:
                    self.main_gui.add_alarm(alarm)

            except ValueError:
                print(f"{time_format()} Invalid gas level format: {message}")
        elif topic == smoke_sensor_topic:
            try:
                smoke_level = float(message.split(":")[1].strip())
                self.main_gui.update_smoke_level(smoke_level)
                # Generate warning/alarm and store to DB
                warning, alarm = generate_warning_alarm(smoke_level=smoke_level)
                store_data(DB_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None, smoke_level, None, warning, alarm)
                if warning:
                    self.main_gui.add_warning(warning)
                if alarm:
                    self.main_gui.add_alarm(alarm)
            except ValueError:
                print(f"{time_format()} Invalid smoke level format: {message}")
        elif topic == temperature_sensor_topic:
            try:
                temperature = float(message.split(":")[1].strip().replace('°C', ''))
                self.main_gui.update_temperature(temperature)
                # Generate warning/alarm and store to DB
                warning, alarm = generate_warning_alarm(temperature=temperature)
                store_data(DB_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None, None, temperature, warning, alarm)
                if warning:
                    self.main_gui.add_warning(warning)
                if alarm:
                    self.main_gui.add_alarm(alarm)
            except ValueError:
                print(f"{time_format()} Invalid temperature format: {message}")
        elif topic == warning_topic:
            self.main_gui.add_warning(message)
            store_data(DB_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None, None, None, message, None)
        elif topic == alarm_topic:
            self.main_gui.add_alarm(message)
            store_data(DB_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None, None, None, None, message)

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")


class DataDisplayDock(QDockWidget):
    """Displays sensor data."""

    def __init__(self):
        QDockWidget.__init__(self)

        self.gas_label = QLabel("Gas Level: N/A")
        self.smoke_label = QLabel("Smoke Level: N/A")
        self.temperature_label = QLabel("Temperature: N/A")

        layout = QVBoxLayout()
        layout.addWidget(self.gas_label)
        layout.addWidget(self.smoke_label)
        layout.addWidget(self.temperature_label)

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setWindowTitle("Sensor Data")

    def update_gas_level(self, level):
        self.gas_label.setText(f"Gas Level: {level:.2f}");

    def update_smoke_level(self, level):
        self.smoke_label.setText(f"Smoke Level: {level:.2f}")

    def update_temperature(self, temp):
        self.temperature_label.setText(f"Temperature: {temp:.2f}")


class StatusDock(QDockWidget):
    """Displays warnings and alarms."""

    def __init__(self):
        QDockWidget.__init__(self)

        self.warning_list = QListWidget()
        self.alarm_list = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Warnings:"))
        layout.addWidget(self.warning_list)
        layout.addWidget(QLabel("Alarms:"))
        layout.addWidget(self.alarm_list)

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setWindowTitle("Status")

    def add_warning(self, message):
        self.warning_list.addItem(message)

    def add_alarm(self, message):
        self.alarm_list.addItem(message)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        QMainWindow.__init__(self)

        self.mc = Mqtt_client()

        self.setUnifiedTitleAndToolBarOnMac(True)
        self.setGeometry(30, 100, 800, 600)
        self.setWindowTitle('Kitchen Monitoring System')

        self.dataDisplayDock = DataDisplayDock()
        self.statusDock = StatusDock()
        self.connectionDock = ConnectionDock(self.mc, self)

        self.setCentralWidget(QWidget())  # Placeholder for central widget
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dataDisplayDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.statusDock)

        self.mc.set_on_message_from_broker(self.handle_mqtt_message) #set the callback

        # create database
        init_db(DB_NAME)

    def handle_mqtt_message(self, topic, message):
        """Pass MQTT messages to the appropriate dock."""
        if topic == gas_sensor_topic:
            try:
                gas_level = float(message.split(":")[1].strip().replace('%', ''))
                self.dataDisplayDock.update_gas_level(gas_level)
                # Generate warning/alarm and store to DB
                warning, alarm = generate_warning_alarm(gas_level=gas_level)
                store_data(DB_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  gas_level, None, None, warning, alarm)
                if warning:
                    self.statusDock.add_warning(warning)
                if alarm:
                    self.statusDock.add_alarm(alarm)
            except ValueError:
                print(f"{time_format()} received message with incorrect format. message: {message}")
        elif topic == smoke_sensor_topic:
            try:
                smoke_level = float(message.split(":")[1].strip())
                self.dataDisplayDock.update_smoke_level(smoke_level)
                # Generate warning/alarm and store to DB
                warning, alarm = generate_warning_alarm(smoke_level=smoke_level)
                store_data(DB_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  None, smoke_level, None, warning, alarm)
                if warning:
                    self.statusDock.add_warning(warning)
                if alarm:
                    self.statusDock.add_alarm(alarm)
            except ValueError:
                print(f"{time_format()} received message with incorrect format. message: {message}")
        elif topic == temperature_sensor_topic:
            try:
                temperature = float(message.split(":")[1].strip().replace('°C', ''))
                self.dataDisplayDock.update_temperature(temperature)
                # Generate warning/alarm and store to DB
                warning, alarm = generate_warning_alarm(temperature=temperature)
                store_data(DB_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  None, None, temperature, warning, alarm)
                if warning:
                    self.statusDock.add_warning(warning)
                if alarm:
                    self.statusDock.add_alarm(alarm)
            except ValueError:
                print(f"{time_format()} received message with incorrect format. message: {message}")
        elif topic == warning_topic:
            self.statusDock.add_warning(message)
            store_data(DB_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None, None, None, message, None)
        elif topic == alarm_topic:
            self.statusDock.add_alarm(message)
            store_data(DB_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None, None, None, None, message)


    # Make the methods accessible.
    def update_gas_level(self, level):
        self.dataDisplayDock.update_gas_level(level)

    def update_smoke_level(self, level):
        self.dataDisplayDock.update_smoke_level(level)

    def update_temperature(self, temp):
        self.dataDisplayDock.update_temperature(temp)

    def add_warning(self, message):
        self.statusDock.add_warning(message)

    def add_alarm(self, message):
        self.statusDock.add_alarm(message)



def generate_warning_alarm(gas_level=None, smoke_level=None, temperature=None):
    """
    Generates warning and alarm messages based on sensor levels.

    Args:
        gas_level (float, optional): Gas level. Defaults to None.
        smoke_level (float, optional): Smoke level. Defaults to None.
        temperature (float, optional): Temperature. Defaults to None.

    Returns:
        tuple: (warning_message, alarm_message) - both strings or None.
    """
    warning_message = None
    alarm_message = None

    if gas_level is not None:
        if 40 <= gas_level < 50:
            warning_message = f"Warning: Gas level is {gas_level:.2f}. Potential leak detected."
        elif gas_level >= 50:
            alarm_message = f"Alarm: Gas level is {gas_level:.2f}. High risk of explosion!"

    if smoke_level is not None:
        if 50 <= smoke_level < 60:
            warning_message = f"Warning: Smoke level is {smoke_level:.2f}. Potential fire detected."
        elif smoke_level >= 60:
            alarm_message = f"Alarm: Smoke level is {smoke_level:.2f}. Fire detected!"

    if temperature is not None:
        if 70 <= temperature < 80:
            warning_message = f"Warning: Temperature is {temperature:.2f}°C. High temperature detected."
        elif temperature >= 80:
            alarm_message = f"Alarm: Temperature is {temperature:.2f}°C. Critical temperature level!"

    return warning_message, alarm_message



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwin = MainWindow()
    mainwin.show()
    app.exec_()
