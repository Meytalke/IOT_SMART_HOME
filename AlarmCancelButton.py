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
from mqtt_init import *

# משתנה גלובלי לשם הלקוח
global clientname, CONNECTED
CONNECTED = False
r = random.randrange(1, 10000000)
clientname = "AlarmCancel_client-" + str(r)  # שם לקוח רלוונטי יותר

alarm_cancel_topic = 'pr/home/6761513/alarm/cancel'  # נושא MQTT לביטול אזעקה


class Mqtt_client():
    def __init__(self):
        # הגדרת משתני MQTT
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

    # גGetter ו-Setter
    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

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

    def get_subscribeTopic(self):
        return self.subscribeTopic

    def set_subscribeTopic(self, value):
        self.subscribeTopic = value

    def get_publishTopic(self):
        return self.publishTopic

    def set_publishTopic(self, value):
        self.publishTopic = value

    def get_publishMessage(self):
        return self.publishMessage

    def set_publishMessage(self, value):
        self.publishMessage = value

    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)

    def on_connect(self, client, userdata, flags, rc):
        global CONNECTED
        if rc == 0:
            print("connected OK")
            CONNECTED = True
            self.on_connected_to_form()
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        CONNECTED = False
        print("DisConnected result code " + str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:" + topic, m_decode)
        # לא נדרש עדכון ממשק משתמש בהודעה המתקבלת, אבל אפשר להוסיף אם יש צורך.

    def connect_to(self):
        # יצירת מופע של לקוח Paho MQTT
        self.client = mqtt.Client(client_id=clientname, clean_session=True)
        self.client.on_connect = self.on_connect  # קשירת פונקציית ה-callback
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)  # התחברות לברוקר

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
    """Main """

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
        global clientname
        self.eClientID.setText(clientname)

        self.eUserName = QLineEdit()
        self.eUserName.setText(username)

        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)

        self.eKeepAlive = QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")

        self.eSSL = QCheckBox()

        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)

        self.eConnectbtn = QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("Click to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")

        self.eAlarmCancelBtn = QPushButton("Cancel Alarm", self)  # לחצן ביטול האזעקה
        self.eAlarmCancelBtn.setToolTip("Click to cancel the alarm")
        self.eAlarmCancelBtn.clicked.connect(self.alarm_cancel_click)
        self.eAlarmCancelBtn.setStyleSheet("background-color: green")  # צבע ירוק כברירת מחדל

        self.ePublisherTopic = QLineEdit()
        self.ePublisherTopic.setText(alarm_cancel_topic)

        formLayot = QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectbtn)
        formLayot.addRow("Pub topic", self.ePublisherTopic)
        formLayot.addRow("Cancel Alarm", self.eAlarmCancelBtn)  # הוספת לחצן ביטול האזעקה

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Connect")

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

    def alarm_cancel_click(self):
        """פונקציה שנקראת בעת לחיצה על לחצן ביטול האזעקה"""
        self.mc.publish_to(self.ePublisherTopic.text(), '{"alarm_status": "canceled"}')  # פרסום הודעה
        print("Alarm cancellation message sent!")
        #  אפשר להוסיף כאן קוד לשינוי צבע הכפתור אם רוצים אינדיקציה ויזואלית.
        self.eAlarmCancelBtn.setStyleSheet("background-color: gray")  # לדוגמה, הפיכת הכפתור לאפור לאחר הלחיצה


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # Init of Mqtt_client class
        self.mc = Mqtt_client()

        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 100, 300, 150)
        self.setWindowTitle('Alarm Cancel Button')

        # Init QDockWidget objects
        self.connectionDock = ConnectionDock(self.mc)

        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)


app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
