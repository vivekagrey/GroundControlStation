#https://firmware.ardupilot.org/Copter/stable-4.0.2/
from dronekit import *
import dronekit.mavlink

import folium
import cv2
#from gmplot import *
#from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import threading


class Second(QMainWindow):
    def __init__(self, parent=None):
        super(Second, self).__init__(parent)
class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.showMaximized()
        self.setGeometry(0,0,1000,500)
        self.setWindowTitle("Johnnette GCS")
        self.setWindowIcon(QIcon("icon.png"))
        #self.setStyleSheet("background-color:red;selection-color: yellow;selection-background-color: blue;border-width: 0px;padding: 0px; spacing: 0px;")
        #self.statusBar().showMessage("Copyright Johnnette Technologies, 2020")
        #self.menubar()
        self.header_frame()
        self.flight_data_stack()
        self.initial_setup_stack()
    def header_frame(self):
        pagelayout = QVBoxLayout()
        pagelayout.setContentsMargins(0,0,0,0)
        pagelayout.setSpacing(0)
        self.head_grid_layout = QGridLayout()
        self.head_grid_layout.setAlignment(Qt.AlignTop)
        self.head_grid_layout.setContentsMargins(0,0,0,0)
        self.header_frame = QFrame()
        #self.header_frame.move(0,0)
        self.header_frame.setMaximumHeight(70)
        self.header_frame.setLayout(self.head_grid_layout)
        self.Stack = QStackedLayout()
        self.Stack.setAlignment(Qt.AlignTop)
        self.header_frame.setStyleSheet("selection-color: black;selection-background-color: powderblue;border-width: 0px;padding: 0px; spacing: 0px;")

        pagelayout.addWidget(self.header_frame)
        pagelayout.addLayout(self.Stack)

        self.widget = QWidget()
        #self.widget.setStyleSheet("border-width: 0px;padding: 0px; spacing: 0px;border:1px solid gray;")
        self.widget.setLayout(pagelayout)
        self.setCentralWidget(self.widget)

        self.stack_wid1 = QWidget()
        self.stack_wid2 = QWidget()
        self.n = 0
        for n, page in enumerate([("Flight data", self.stack_wid1), ("Initial setup", self.stack_wid2)]):
            btn = QPushButton(str(page[0]))
            btn.setFixedSize(100,70)
            btn.pressed.connect(lambda n=n: self.Stack.setCurrentIndex(n))
            self.head_grid_layout.addWidget(btn, 0, n+1)
            self.Stack.addWidget(page[1])

        pushButton = QPushButton("Help")
        pushButton.setFixedSize(100, 70)
        self.head_grid_layout.addWidget(pushButton,0,3)
        pushButton.clicked.connect(self.on_pushButton_clicked)

        self.pushButton_connect = QPushButton("Connect")
        self.pushButton_connect.setFixedSize(100, 70)
        self.head_grid_layout.addWidget(self.pushButton_connect, 0, 8)
        self.pushButton_connect.clicked.connect(self.connect_fc)

        #self.pushButton_connect.setCheckable(True)
        #pushButton_connect.toggle()
        h_label = QLabel()
        pix = QPixmap('logo250x100.jpg')
        pix.scaled(250, 700)
        #h_label.setFixedSize(250,100)
        h_label.setPixmap(pix)
        h_label.show()
        self.head_grid_layout.addWidget(h_label,0,0)

        combobox_grid = QGridLayout()
        self.head_grid_layout.addLayout(combobox_grid,0, 7 )
        combobox_subgrid = QGridLayout()
        combobox_grid.addLayout(combobox_subgrid, 1, 0)

        self.combobox1 = QComboBox()
        self.combobox1.addItem("Select/Enter COM Port")
        self.combobox1.addItem("/dev/ttyACM1")
        self.combobox1.addItem("/dev/ttyACM0")
        self.combobox1.addItem("/dev/ttyUSB0")
        self.combobox1.addItem("SITL")
        #self.combobox1.setEditable(True)
        #self.combobox1.InsertAtTop
        self.combobox1.activated[str].connect(self.combo_text)


        self.combobox2 = QComboBox()
        self.combobox2.addItem("Select/Enter Baud")
        self.combobox2.addItem("57600")
        self.combobox2.addItem("115200")
        self.combobox2.activated[str].connect(self.combo_text)

        combobox3 = QComboBox()
        combobox3.addItems(["MAV ID", "MAV001", "MAV002"])
        combobox3.setEditable(True)
        combobox3.InsertAtTop
        combobox3.activated[str]

        combobox_grid.addWidget(self.combobox1, 0, 0)
        combobox_subgrid.addWidget(self.combobox2, 0, 0)
        combobox_subgrid.addWidget(combobox3, 0, 1)

        spacer1 = QSpacerItem(100, 70)
        self.head_grid_layout.addItem(spacer1, 0, 4)
        spacer2 = QSpacerItem(60, 70)
        self.head_grid_layout.addItem(spacer2, 0, 6)

        self.mode_label = QLabel("MODE")
        self.head_grid_layout.addWidget(self.mode_label, 0, 5)
        self.mode_label.setStyleSheet("font:bold 15pt Comic Sans MS")

        self.pushButtonlaunch = QPushButton("Launch Mission")
        combobox_grid.addWidget(self.pushButtonlaunch, 2, 0)
        self.pushButtonlaunch.clicked.connect(self.launch_mission)
    def disconnect_fc(self):
        if self.pushButton_connect.text() == "Disconnect" or self.cancel_flag == True:
            try:
                self.th.join()
                self.dis_thr = threading.Thread(target=self.disconnect_fc_thread)
                self.dis_thr.start()
                print("disconnect fc method")
            except AttributeError:
                print("e25")
            try:
                self.wps_uploaded = False
            except AttributeError:
                pass
    def disconnect_fc_thread(self):
        print("disconnect_fc_thread method")
        try:
            self.listener_th.join()
        except AttributeError:
            print("36")
        finally:
            self.label_1.setText("yaw")
            self.label_2.setText("gpsinfo")
            self.label_3.setText("voltage")
            self.label_4.setText("altitude")
            self.label_5.setText("groundspeed")
            self.label_6.setText("verticalspeed")
        try:
            self.vehicle.close()
            print("vehicle closed", self.vehicle)
        except AttributeError:
            print("e26")
        self.pushButton_connect.setText("Connect")
        print("e39")
        self.pushButton_connect.setChecked(False)
        print("e38")
        try:
            self.vehicle.flush()
            print("vehicle flushed")
        except AttributeError:
            print("e27")
        try:
            del self.vehicle
            print("vehicle deleted")
        except AttributeError:
            print("e28")
        try:
            print("101")
            self.loc_th.join()
        except:
            print("29")
        try:
            print("102")
            if self.sitl is not None:
                self.sitl.stop()
                print("shutting down sitl")
        except AttributeError:
            print("30")
        if self.cancel_flag == False:
            print("103")
            self.pushButton_connect.clicked.disconnect(self.disconnect_fc)
            self.pushButton_connect.clicked.connect(self.connect_fc)
            print("e37")
        try:
            if self.wps_uploaded == False:
                self.pushButtonlaunch.clicked.disconnect(self.abort)
                self.pushButtonlaunch.setText("Launch Mission")
                self.pushButtonlaunch.clicked.connect(self.launch_mission)
                print("104")
        except (AttributeError, TypeError):
            print("105")
        #print("buttan pressed dis fc thr", self.pushButton_connect.isChecked())
        print("e40")
        self.combobox1.setCurrentIndex(0)
        self.combobox2.setCurrentIndex(0)
        print("e41")
    def combo_text(self):
        self.connection_string = str(self.combobox1.currentText())
        self.baud = str(self.combobox2.currentText())
        print("inside combo", self.connection_string, self.baud)
    def thr(self):
        self.i = True
        print("e18")
        try:
            if self.connection_string == "SITL":
                import dronekit_sitl
                self.sitl = dronekit_sitl.start_default()
                self.connection_string = self.sitl.connection_string()
                self.vehicle = connect(self.connection_string, wait_ready=True)
                try:
                    if self.vehicle and self.cancel_flag == False:
                        self.pushButton_connect.clicked.disconnect(self.connect_fc)
                        self.pushButton_connect.setText("Disconnect")
                        #self.pushButton_connect.setChecked(True)
                        self.timer.stop()
                        self.dialog_connect.close()
                        self.message = 1

                        self.pushButton_connect.clicked.connect(self.disconnect_fc)
                        self.altitude = 15
                        self.alt_text.setValue(15)

                        self.listener_th = threading.Thread(target=self.listener_thr)
                        self.listener_th.start()
                        self.loc_th = threading.Thread(target=self.current_loc_stats)
                        self.loc_th.start()
                except AttributeError:
                    self.timer.stop()
                    self.dialog_connect.close()
                    self.message = 2
                    self.i = False
                    print("e3")
            else:

                if self.connection_string != "Select/Enter COM Port" and self.baud != "Select/Enter Baud":
                    self.vehicle = connect(self.connection_string, wait_ready=False, baud=self.baud)
                    print("after conn------",self.vehicle)
                    print("e16")
                    try:
                        if self.vehicle and self.cancel_flag == False:
                            self.vehicle.wait_ready(True, raise_exception=True)#false
                            self.pushButton_connect.setText("Disconnect")
                            self.pushButton_connect.setChecked(True)
                            self.pushButton_connect.clicked.disconnect(self.connect_fc)
                            self.timer.stop()
                            self.dialog_connect.close()
                            print("e9")
                            self.message = 1
                            self.pushButton_connect.clicked.connect(self.disconnect_fc)
                            self.altitude = 15
                            self.alt_text.setValue(15)
                            self.listener_th = threading.Thread(target=self.listener_thr)
                            self.listener_th.start()
                            self.loc_th = threading.Thread(target=self.current_loc_stats)
                            self.loc_th.start()
                    except (Exception, dronekit.APIException,TypeError) as e:
                        self.timer.stop()
                        self.dialog_connect.close()
                        self.message = 2
                        self.i = False
                        try:
                            self.vehicle.close()
                        except Exception as e:
                            print(e)
                        try:
                            del self.vehicle
                        except Exception as e:
                            print(e)
                        print("e2", str(e))
                else:
                    print("e14")
                    self.message = 5
        #except (serial.SerialException, TypeError, ConnectionRefusedError, AttributeError, FileNotFoundError, ValueError, ConnectionError, APIException, dronekit.mavlink):
        except (Exception, dronekit.APIException, TypeError) as e:
            try:
                self.combobox1.setCurrentIndex(0)
                self.combobox2.setCurrentIndex(0)
                time.sleep(1)
                self.timer.stop()
                self.dialog_connect.close()
                self.tt = True
                print("e13",  str(e))
                if self.i:
                    self.message = 6
                    print("e8")
            except AttributeError:
                try:
                    time.sleep(1)
                    self.timer.stop()
                    self.dialog_connect.close()
                    self.message = 8
                    print("e7")
                except AttributeError:
                    self.message = 2
    def connect_fc(self):
        try:
            self.cancel_th.join()
            print("1001")
        except AttributeError:
            print("e31")
        self.cancel_flag = False
        try:
            cb = self.vehicle
            print("1002")
            self.cb = True
        except AttributeError:
            self.cb = False
            print("e32")
        if self.pushButton_connect.text() == "Connect" and self.cb == False:
            try:
                print("45")
                #self.dis_thr.join()
            except AttributeError:
                print("e33")
            self.th = threading.Thread(target=self.thr)
            self.th.start()
            print("1003")
            self.pushButton_connect.setChecked(False)
            try:
                if self.connection_string != "Select/Enter COM Port" and self.baud != "Select/Enter Baud" or self.connection_string == "SITL":
                    print("1004")
                    self.dialog_connect = QDialog()
                    self.dia_vbox = QVBoxLayout()
                    self.dia_hbox = QGridLayout()
                    self.dialog_connect.setLayout(self.dia_vbox)
                    self.cancel_dia_btn = QPushButton("Cancel")
                    self.dialog_connect.setModal(True)
                    self.dialog_connect.setWindowTitle("Connecting To Vehicle")
                    self.dialog_connect.setWindowFlags(self.dialog_connect.windowFlags() | Qt.CustomizeWindowHint)
                    self.dialog_connect.setWindowFlags(self.dialog_connect.windowFlags() & ~Qt.WindowCloseButtonHint)
                    self.dialog_connect.show()
                    self.progressbar = QProgressBar()
                    self.progressbar.setTextVisible(False)
                    self.progressbar.show()
                    self.progressbar.setGeometry(0, 0, 400, 30)
                    #self.dialog_connect.setGeometry(400, 300, 400, 60)
                    self.cancel_dia_btn.setFixedSize(100,30)
                    self.dia_vbox.addWidget(self.progressbar)
                    self.dia_vbox.addLayout(self.dia_hbox)
                    sp1 = QSpacerItem(100, 30)
                    sp2 = QSpacerItem(100, 30)
                    self.dia_hbox.addItem(sp1,0,0)
                    self.dia_hbox.addItem(sp2,0,1)
                    self.dia_hbox.addWidget(self.cancel_dia_btn,0,2)
                    self.cancel_dia_btn.show()
                    self.cancel_dia_btn.clicked.connect(self.cancel_connect)
                    self.timer = QBasicTimer()
                    self.start_timer()
                    if self.i == False:
                        self.timer.stop()
                        self.dialog_connect.close()
            except AttributeError:
                print("e4")
            self.altitude = 15
            print("1006")
            self.alt_text.setValue(15)
    def start_timer(self):
        self.cnt = 0
        if self.timer.isActive():
            self.timer.stop()
        self.timer.start(200, self)
    def timerEvent(self, event):
        self.cnt = self.cnt + .5
        self.progressbar.setValue(self.cnt)

    def cancel_connect_th(self):
        self.timer.stop()
        self.dialog_connect.close()
        self.disconnect_fc()
    def cancel_connect(self):
        self.cancel_flag = True
        self.cancel_th = threading.Thread(target=self.cancel_connect_th)
        self.cancel_th.start()
    def flight_data_stack(self):
        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setContentsMargins(0,0,0,0)
        self.hbox1 = QHBoxLayout()

        self.hbox1.setAlignment(Qt.AlignTop)
        self.hbox1.setContentsMargins(0,0,0,0)
        self.vbox.addLayout(self.hbox1)

        self.stack_wid1.setLayout(self.vbox)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignTop)
        self.message = 0
        #####vid signal was here
        self.vid = VideoThread()
        self.vid.start()
        self.vid.vid_signal.connect(self.updatevideoframe)
        self.vid.vid_signal.connect(self.show_message)
        self.hbox1.addWidget(self.label, Qt.AlignTop)
        self.fol()
        #self.gmap()
        self.frame = QFrame()
        self.vbox.addWidget(self.frame)
        #self.frame.setMinimumWidth(1300)
        self.details()
    def show_message(self, val):
        if self.message == 1:
            self.message = 0
            print("m1")
            QMessageBox.information(self.widget, "Message", "Connected")
        elif self.message == 2:
            print("m2")
            self.message = 0
            QMessageBox.information(self.widget, "Message", "No vehicle connected")
        elif self.message == 3:
            print("m3")
            self.message = 0
            QMessageBox.information(self.widget, "Message", "Send Wp to UAV/Set AUTO Mode/Connect to Vehicle")
        elif self.message == 4:
            print("m4")
            self.message = 0
            QMessageBox.information(self.widget, "Message", "set the altitude")
        elif self.message == 5:
            self.message = 0
            QMessageBox.information(self.widget, "Message", "Choose Baud/COM Port")
        elif self.message == 6:
            self.message = 0
            QMessageBox.information(self.widget, "Message", "wrong com port")
        elif self.message == 7:
            self.message = 0
            QMessageBox.information(self.widget, "Message", "Waypoints Uploaded To UAV")
        elif self.message == 8:
            self.message = 0
            QMessageBox.information(self.widget, "Message", "Choose Correct Baud/COM Port")
        elif self.message == 9:
            self.message = 0
            QMessageBox.information(self.widget, "Message", "Add Lattitude and Longitude in Decimal")
    def initial_setup_stack(self):
        setup_layout = QVBoxLayout()
        tabs = QTabWidget()
        #tabs.setStyleSheet("background-color:black; color:white;")
        setup_layout.addWidget(tabs)

        tab1 = QWidget()
        tab2 = QWidget()
        tab3 = QWidget()
        tabs.addTab(tab1, "Firmware Setup")
        tabs.addTab(tab2, "Mandatory Hardware Setup")
        tabs.addTab(tab3, "Payload setup")

        self.stack_wid2.setLayout(setup_layout)
    def on_pushButton_clicked(self):
        self.dialog = Second()
        self.dialog.show()
    def updatevideoframe(self, val):
        self.label.setPixmap(val)
        self.label.show()
    def details(self):
        self.tabs = QTabWidget()
        self.vbox.addWidget(self.tabs)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        #self.tabs.setFixedSize(1270, 163)
        #self.tabs.setStyleSheet("background-color:black;color:white;")

        self.tabs.addTab(self.tab1, "Quick stats")
        self.tabs.addTab(self.tab2, "Waypoints")
        self.tabs.addTab(self.tab3, "Action")
        self.tabs.addTab(self.tab4, "Preflight")
        self.waypoints()
        self.action()
        self.quick_stats()
    def action(self):
        self.actiongrid = QGridLayout()
        self.tab3.setLayout(self.actiongrid)
        action_btn_1 = QPushButton("SET MODE")
        self.actiongrid.addWidget(action_btn_1, 0, 1)
        action_btn_1.clicked.connect(self.set_mode)
        action_btn_2 = QPushButton("FORCE ARM")
        self.actiongrid.addWidget(action_btn_2, 0, 2)
        action_btn_2.clicked.connect(self.force_arm)



        action_btn_3 = QPushButton("SET ALTITUDE(in m)")
        self.actiongrid.addWidget(action_btn_3, 0, 3)
        action_btn_3.clicked.connect(self.altitude_method)

        action_btn_4 = QPushButton("SET HOME LOCATION")
        self.actiongrid.addWidget(action_btn_4, 1, 1)
        action_btn_4.clicked.connect(self.set_home_location)

        action_btn_5 = QPushButton("FORCE DISARM")
        self.actiongrid.addWidget(action_btn_5, 1, 2)
        action_btn_5.clicked.connect(self.force_disarm)


        action_btn_8 = QPushButton("SET GROUND SPEED(m/s)")
        self.actiongrid.addWidget(action_btn_8, 1, 3)
        action_btn_8.clicked.connect(self.set_ground_speed)

        self.combobox_action_1 = QComboBox()
        self.combobox_action_1.addItems(["Select Mode", "Stabilize", "Auto", "Guided","Loiter", "Simple Takeoff", "Land", "Alt Hold", "RTL"])
        self.actiongrid.addWidget(self.combobox_action_1,0,0)
        self.combobox_action_1.activated[str].connect(self.mode_text)

        self.combobox_action_2 = QComboBox()
        self.combobox_action_2.addItems(["Select Home location", "57600", "115200"])
        self.actiongrid.addWidget(self.combobox_action_2,1,0)
        # self.combobox_action_2.activated[str].connect(self.combo_text)
        self.gs_spinbox = QSpinBox()
        self.actiongrid.addWidget(self.gs_spinbox,1,4)
        self.gs_spinbox.setRange(0, 25)
        # self.combobox_action_3.activated[str].connect(self.combo_text)
        self.alt_text = QSpinBox()
        self.actiongrid.addWidget(self.alt_text, 0, 4)
        self.alt_text.setRange(0, 10000)
    def set_ground_speed(self):
        try:
            self.vehicle.groundspeed = self.gs_spinbox.value()
        except AttributeError:
            self.message=2
    def set_home_location(self):
        pass
    def altitude_method(self):
        try:
            if self.vehicle:
                self.altitude = self.alt_text.value()
                print(self.altitude)
        except AttributeError:
            self.message = 2
    def mode_text(self):
        self.mode =  str(self.combobox_action_1.currentText())

    def yaw_callback(self, object,attr_name, value):
        val = str(value).split(":")[1]
        self.quickyaw = val.split(",")[1]
        self.label_1.setText(self.quickyaw)
        self.attribute_msg = attr_name

    def gpsinfo_callback(self, object,attr_name, value):
        self.quickgps = str(value).split(":")[1]
        self.label_2.setText(self.quickgps)
        self.attribute_msg = attr_name

    def voltage_callback(self, object,attr_name, value):
        val = str(value).split(":")[1]
        self.quickvoltage = val.split(",")[0]
        self.label_3.setText(self.quickvoltage)
        self.attribute_msg = attr_name

    def altitude_callback(self, object,attr_name, value):
        val = str(value).split(":")[1]
        self.quickalt = val.split(",")[2]
        self.label_4.setText(self.quickalt)
        self.attribute_msg = attr_name

    def groundspeed_callback(self,object, attr_name, value):
        self.quickgroundspeed = attr_name + "=" + str(value)
        self.label_5.setText(self.quickgroundspeed)
        self.attribute_msg = attr_name

    def verticalspeed_callback(self,object, attr_name, value):
        self.quickverticalspeed = "verticalspeed=" + str(value[2])
        self.label_6.setText(self.quickverticalspeed)
        self.attribute_msg = attr_name

    def listener_thr(self):
        while not self.pushButton_connect.text() == "Disconnect":
            time.sleep(2)
        try:
            self.vehicle.add_attribute_listener('attitude', self.yaw_callback)  #
            self.vehicle.add_attribute_listener('location.global_relative_frame', self.altitude_callback)  # in m/s
            self.vehicle.add_attribute_listener('gps_0', self.gpsinfo_callback)  # in m/s
            self.vehicle.add_attribute_listener('battery', self.voltage_callback)  # in m/s
            self.vehicle.add_attribute_listener('groundspeed', self.groundspeed_callback)  # in m/s
            self.vehicle.add_attribute_listener('velocity', self.verticalspeed_callback)  # in m/s
            time.sleep(2)
            self.vehicle.remove_message_listener('attitude', self.yaw_callback)
            self.vehicle.remove_message_listener('location.global_relative_frame', self.altitude_callback)
            self.vehicle.remove_message_listener('gps_0', self.gpsinfo_callback)
            self.vehicle.remove_message_listener('battery', self.voltage_callback)
            self.vehicle.remove_message_listener('groundspeed', self.groundspeed_callback)
            self.vehicle.remove_message_listener('velocity', self.verticalspeed_callback)
        except AttributeError:
            print("listener error")


    def quick_stats(self):
        quickstats_grid = QGridLayout()
        self.tab1.setLayout(quickstats_grid)

        self.label_1 = QLabel("yaw")
        self.label_1.setStyleSheet("font:bold 12pt Comic Sans MS")
        self.label_1.setAlignment(Qt.AlignCenter)
        quickstats_grid.addWidget(self.label_1, 0, 0)

        self.label_2 = QLabel("gps")
        self.label_2.setStyleSheet("font:bold 12pt Comic Sans MS")
        self.label_2.setAlignment(Qt.AlignCenter)
        quickstats_grid.addWidget(self.label_2, 1, 0)

        self.label_3 = QLabel("voltage")
        self.label_3.setStyleSheet("font:bold 12pt Comic Sans MS")
        self.label_3.setAlignment(Qt.AlignCenter)
        quickstats_grid.addWidget(self.label_3, 0, 1)

        self.label_4 = QLabel("altitude")
        self.label_4.setStyleSheet("font:bold 12pt Comic Sans MS")
        self.label_4.setAlignment(Qt.AlignCenter)
        quickstats_grid.addWidget(self.label_4, 1, 1)

        self.label_5 = QLabel("ground speed")
        self.label_5.setStyleSheet("font:bold 12pt Comic Sans MS")
        self.label_5.setAlignment(Qt.AlignCenter)
        quickstats_grid.addWidget(self.label_5, 0, 2)

        self.label_6 = QLabel("vertical speed")
        self.label_6.setStyleSheet("font:bold 12pt Comic Sans MS")
        self.label_6.setAlignment(Qt.AlignCenter)
        quickstats_grid.addWidget(self.label_6, 1, 2)

    def set_mode(self):
        try:
            if self.mode == "Select Mode":
                print("Select Mode")
            elif self.mode == "Guided":
                try:
                    self.set_mode_thr.join()
                except AttributeError:
                    print("mode exception raised")
                finally:
                    self.set_mode_thr = threading.Thread(target=self.set_guidedmode_thr)
                    self.set_mode_thr.start()
                    print("Guided mode set")
            elif self.mode == "Auto":
                try:
                    self.set_mode_thr.join()
                except AttributeError:
                    print("mode exception raised")
                self.set_mode_thr = threading.Thread(target=self.set_automode_thr)
                self.set_mode_thr.start()
                print("Auto mode set")
            elif self.mode == "Loiter":
                try:
                    self.set_mode_thr.join()
                except AttributeError:
                    print("mode exception raised")
                self.set_mode_thr = threading.Thread(target=self.set_loitermode_thr)
                self.set_mode_thr.start()
                print("Loiter mode set")
            elif self.mode == "Land":
                try:
                    self.set_mode_thr.join()
                except AttributeError:
                    print("mode exception raised")
                self.set_mode_thr = threading.Thread(target=self.set_landmode_thr)
                self.set_mode_thr.start()
                print("Land mode set")
            elif self.mode == "Takeoff":
                try:
                    self.set_mode_thr.join()
                except AttributeError:
                    print("mode exception raised")
                #self.set_mode_thr = threading.Thread(target=self.set_takeoffmode_thr)
                #self.set_mode_thr.start()
                print("Takeoff mode set")
            elif self.mode == "Simple Takeoff":
                try:
                    self.set_mode_thr.join()
                except AttributeError:
                    print("mode exception raised")
                self.set_mode_thr = threading.Thread(target=self.set_simpletakeoff_thr)
                self.set_mode_thr.start()
                print("Simple Guided Takeoff mode set")
            elif self.mode == "RTL":
                try:
                    self.set_mode_thr.join()
                except AttributeError:
                    print("mode exception raised")
                self.set_mode_thr = threading.Thread(target=self.set_rtlmode_thr)
                self.set_mode_thr.start()
                print("RTL mode set")
            elif self.mode == "Alt Hold":
                try:
                    self.set_mode_thr.join()
                except AttributeError:
                    print("mode exception raised")
                self.set_mode_thr = threading.Thread(target=self.set_altholdmode_thr)
                self.set_mode_thr.start()
                print("Alt Hold mode set")
            else:
                try:
                    self.set_mode_thr.join()
                except AttributeError:
                    print("mode exception raised")
                self.set_mode_thr = threading.Thread(target = self.set_stabilizemode_thr)
                self.set_mode_thr.start()
                print("Stabilize mode set")
        except AttributeError:
            pass
    def set_stabilizemode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("STABILIZE")
            while not self.vehicle.mode.name == "STABILIZE":
                time.sleep(0.2)
            self.mode_label.setText(str(self.vehicle.mode.name))

        except AttributeError:
            print("No vehicle connected")

    def set_rtlmode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("RTL")
            while not self.vehicle.mode.name == "RTL":
                time.sleep(0.2)
            self.mode_label.setText(str(self.vehicle.mode.name))

        except AttributeError:
            print("No vehicle connected")

    def set_loitermode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("LOITER")
            while not self.vehicle.mode.name == "LOITER":
                time.sleep(0.2)
            self.mode_label.setText(str(self.vehicle.mode.name))

        except AttributeError:
            print("No vehicle connected")

    def set_automode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("AUTO")
            while not self.vehicle.mode.name == "AUTO":
                time.sleep(0.2)
                print("armed",self.vehicle.armed)
            self.mode_label.setText(str(self.vehicle.mode.name))

        except AttributeError:
            print("No vehicle connected")

    def set_landmode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("LAND")
            while not self.vehicle.mode.name == "LAND":
                time.sleep(0.2)
            self.mode_label.setText(str(self.vehicle.mode.name))
        except AttributeError:
            print("No vehicle connected")

    def set_takeoffmode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("TAKEOFF")
            while not self.vehicle.mode.name == "TAKEOFF":
                time.sleep(0.2)
            self.mode_label.setText(str(self.vehicle.mode.name))

        except AttributeError:
            print("No vehicle connected")

    def set_altholdmode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("ALT_HOLD")
            while not self.vehicle.mode.name == "ALT_HOLD":
                time.sleep(0.2)
            self.mode_label.setText(str(self.vehicle.mode.name))

        except AttributeError:
            print("No vehicle connected")

    def set_guidedmode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("GUIDED")
            while not self.vehicle.mode.name == "GUIDED":
                time.sleep(0.1)
            self.mode_label.setText(str(self.vehicle.mode.name))
        except AttributeError:
            print("No vehicle connected")
    def launch_mission_th_method(self):
        try:
            self.vehicle.mode = "GUIDED"
            while not self.vehicle.mode.name == "GUIDED":
                time.sleep(.2)
            self.vehicle.commands.next = 0
            print("Basic pre-arm checks")
            # Don't let the user try to arm until autopilot is ready
            while not self.vehicle.is_armable:
                print(" Waiting for vehicle to initialise...")
                time.sleep(1)
            self.vehicle.arm()
            while not self.vehicle.armed:
                print(" Waiting for arming...")
                time.sleep(1)
            self.vehicle.mode = VehicleMode("AUTO")
            msg = self.vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0)
            self.vehicle.send_mavlink(msg)
            print("55")
            self.mode_label.setText("MISSION MODE")
            self.pushButtonlaunch.clicked.disconnect(self.launch_mission)

            self.pushButtonlaunch.setText("Abort Mission")
            self.pushButtonlaunch.clicked.connect(self.abort)
        except AttributeError:
            print("201")
        try:
            self.pushButton_re.clicked.connect(self.re_launch_mission)
        except TypeError:
            print("60")
    def re_launch_mission(self):
        self.rlm_th = threading.Thread(target=self.re_launch_mission_th)
        self.rlm_th.start()
    def re_launch_mission_th(self):
        if self.vehicle.armed == False:
            self.set_mode_thr = threading.Thread(target=self.set_simpletakeoff_thr)
            self.set_mode_thr.start()
            while self.vehicle.location.global_relative_frame.alt < 5:
                time.sleep(1)
        try:
            self.set_mode_thr.join()
        except AttributeError:
            print("e141")
        self.vehicle.mode = VehicleMode("AUTO")
        self.mode_label.setText("MISSION MODE")
    def launch_mission(self):
        try:
            self.abort_th.join()
            self.launch_mission_th.join()
        except AttributeError:
            print("e57")
        try:
            if self.wps_uploaded == True:
                self.launch_mission_th = threading.Thread(target=self.launch_mission_th_method)
                self.launch_mission_th.start()
            else:
                self.message = 3
        except AttributeError:
            self.message = 3
    def set_simpletakeoff_thr(self):
        try:
            self.mode_label.setText("TAKEOFF")
            print("Basic pre-arm checks")
            #Don't let the user try to arm until autopilot is ready
            while not self.vehicle.is_armable:
                print(" Waiting for vehicle to initialise...")
                time.sleep(1)
            print("Arming motors")
            # Copter should arm in GUIDED mode
            self.vehicle.mode = VehicleMode("GUIDED")
            self.vehicle.armed = True
            while not self.vehicle.mode.name == "GUIDED" and not self.vehicle.armed:
                time.sleep(0.2)

            while not self.vehicle.armed:
                print(" Waiting for arming...")
                time.sleep(1)

            print("Taking off!")
            try:
                self.vehicle.simple_takeoff(self.altitude)  # Take off to target altitude
            except AttributeError:
                self.message = 4

        except AttributeError:
            print("vehicle not connected")
    def current_loc_stats(self):
        while True:
            try:
                print(" location: ", self.vehicle.location.global_relative_frame)
                time.sleep(10)
            except AttributeError:
                pass
    def abort(self):
        try:
            self.set_mode_thr.join()
            self.abort_th.join()
        except AttributeError:
            print("e155")
        try:
            self.launch_mission_th.join()
            self.rlm_th.join()
        except AttributeError:
            print("e56")
        self.abort_th = threading.Thread(target=self.abort_th_method)
        self.abort_th.start()
    def abort_th_method(self):
        try:
            if self.vehicle.location.global_relative_frame.alt >= 0:
                self.vehicle.mode = VehicleMode("RTL")
                self.vehicle.flush()
                print("aborting")
                while self.vehicle.location.global_relative_frame.alt >= 0.2:
                    time.sleep(1)
            self.mds = self.vehicle.commands
            self.mds.clear()
            self.wps_uploaded = False
            self.vehicle.flush()
            self.mode_label.setText(self.vehicle.mode.name)
        except AttributeError:
            print("62")
        try:
            print("commands cleared from UAV")
            self.pushButtonlaunch.clicked.disconnect(self.abort)
        except TypeError as e:
            print(str(e))
        self.pushButtonlaunch.setText("Launch Mission")
        self.pushButtonlaunch.clicked.connect(self.launch_mission)
        self.pushButton_re.clicked.disconnect(self.re_launch_mission)
    def increase_throttle(self):
        pass
    def force_arm(self):
        try:
            print("Trying force arm...")
            self.vehicle.armed = True
        except AttributeError:
            self.message = 2
    def force_disarm(self):
        try:
            print("Trying force arm...")
            self.vehicle.armed = False
        except AttributeError:
            self.message = 2
    def table_item_changed(self, Qitem):
        try:
            test = float(Qitem.text())
        except ValueError:
            self.message = 9
            Qitem.setText(str(0.0))
    def waypoints(self):
        hbox = QHBoxLayout()
        self.tab2.setLayout(hbox)
        self.waypoints_table = QTableWidget()
        hbox.addWidget(self.waypoints_table)
        self.waypoints_table.show()
        self.waypoints_table.itemChanged.connect(self.table_item_changed)

        self.waypoints_table.setRowCount(0)
        self.waypoints_table.setColumnCount(5)

        #self.waypoints_table.setFixedSize(1200, 150)
        self.waypoints_table.setHorizontalHeaderLabels(( "Lattitude", "Longitude", "Move Up", "Move Down", "Remove"))
        self.waypoints_table.setColumnWidth(1, 150)
        self.waypoints_table.setColumnWidth(0, 200)

        waypointButtonWidget = QWidget()
        waypoints_button_grid = QGridLayout()
        waypoints_button_grid.setAlignment(Qt.AlignRight)
        hbox.addLayout(waypoints_button_grid)
        self.wp_count = 0

        btn11 = QPushButton("Upload WP File")
        waypoints_button_grid.addWidget(btn11, 0, 0)
        btn11.clicked.connect(self.upload_custom_wps)

        btn12 = QPushButton("Add Waypoint")
        waypoints_button_grid.addWidget(btn12, 1, 0)
        btn12.clicked.connect(self.add_wp)

        btn13 = QPushButton("Delete all Waypoints")
        waypoints_button_grid.addWidget(btn13, 2, 0)
        btn13.clicked.connect(self.delete_all_wps)

        send_wps_button = QPushButton("Send WPs to UAV")
        waypoints_button_grid.addWidget(send_wps_button, 3, 0)
        send_wps_button.clicked.connect(self.send_wps_to_uav)

        download_wps_button = QPushButton("Download WPs from UAV")
        #waypoints_button_grid.addWidget(download_wps_button, 3, 0)
    def send_wps_to_uav(self):
        swp = threading.Thread(target=self.send_wps_to_uav_th)
        swp.start()
    def send_wps_to_uav_th(self):
        waypoints = {}
        for row in range(self.waypoints_table.rowCount()):
                lat = self.waypoints_table.item(row, 0)
                lon = self.waypoints_table.item(row, 1)
                waypoints[float(lat.text())] = float(lon.text())
        print(waypoints)
        try:
            cmds = self.vehicle.commands

            print("Clear any existing commands")
            cmds.clear()
            try:
                cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, self.altitude))
                for i, j in waypoints.items():
                    cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0,0, 0, 0, 0, 0, i, j, self.altitude))
                cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0,0, 0, 0, 0, i, j, self.altitude))
                print("uploading mission commands")
                cmds.upload()
                time.sleep(3)
                self.message = 7
                self.wps_uploaded = True
            except (AttributeError, UnboundLocalError):
                self.message = 4
        except AttributeError:
            self.message = 2

    def delete_all_wps(self):
        self.wp_count = 0
        self.waypoints_table.setRowCount(self.wp_count)

    def move_wp_down_btn_clicked(self):
        button = self.sender()
        row = self.waypoints_table.indexAt(button.pos()).row()
        if row != self.wp_count-1:
            try:
                lat_plus_1 = self.waypoints_table.item(row + 1, 0).text()
                lon_plus_1 = self.waypoints_table.item(row + 1, 1).text()
                lat = self.waypoints_table.item(row, 0).text()
                lon = self.waypoints_table.item(row, 1).text()
                self.waypoints_table.setItem(row + 1, 0, QTableWidgetItem(lat))
                self.waypoints_table.setItem(row + 1, 1, QTableWidgetItem(lon))
                self.waypoints_table.setItem(row, 0, QTableWidgetItem(lat_plus_1))
                self.waypoints_table.setItem(row, 1, QTableWidgetItem(lon_plus_1))
            except AttributeError:
                self.message = 9
    def move_wp_up_btn_clicked(self):
        button = self.sender()
        row = self.waypoints_table.indexAt(button.pos()).row()
        if row != 0:
            try:
                lat_minus_1 = self.waypoints_table.item(row-1, 0).text()
                lon_minus_1 = self.waypoints_table.item(row-1, 1).text()
                lat = self.waypoints_table.item(row, 0).text()
                lon = self.waypoints_table.item(row, 1).text()
                self.waypoints_table.setItem(row-1, 0, QTableWidgetItem(lat))
                self.waypoints_table.setItem(row - 1, 1, QTableWidgetItem(lon))
                self.waypoints_table.setItem(row, 0, QTableWidgetItem(lat_minus_1))
                self.waypoints_table.setItem(row, 1, QTableWidgetItem(lon_minus_1))
            except AttributeError:
                self.message = 9
    def remove_btn_clicked(self):
        button = self.sender()
        row = self.waypoints_table.indexAt(button.pos()).row()
        self.waypoints_table.removeRow(row)
        self.wp_count -= 1

    def add_wp(self):
        self.waypoints_table.insertRow(self.wp_count)
        self.waypoints_table.setRowHeight(self.wp_count, 15)
        remove_wp_btn = QPushButton("Remove")
        self.waypoints_table.setCellWidget(self.wp_count, 4, remove_wp_btn)
        move_wp_up_btn = QPushButton("Move Up")
        move_wp_down_btn = QPushButton("Move Down")
        self.waypoints_table.setCellWidget(self.wp_count, 2, move_wp_up_btn)
        self.waypoints_table.setCellWidget(self.wp_count, 3, move_wp_down_btn)
        remove_wp_btn.clicked.connect(self.remove_btn_clicked)
        move_wp_up_btn.clicked.connect(self.move_wp_up_btn_clicked)
        move_wp_down_btn.clicked.connect(self.move_wp_down_btn_clicked)
        self.wp_count += 1
    def upload_custom_wps(self):
        import csv
        self.wp_count = 0
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "CSV Format Files (*.csv)", options=options)

        if filename:
            with open(filename, 'r') as csvfile:
                # creating a csv reader object
                csvreader = csv.reader(csvfile)
                self.waypoints_table.setRowCount(0)
                for row_number, row_data in enumerate(csvreader):
                    self.waypoints_table.insertRow(row_number)
                    self.waypoints_table.setRowHeight(row_number, 15)
                    self.wp_count += 1
                    for column_number, data in enumerate(row_data):
                        if column_number < 2:
                            self.waypoints_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                    move_wp_up_btn = QPushButton("Move Up")
                    move_wp_down_btn = QPushButton("Move Down")
                    self.waypoints_table.setCellWidget(row_number, 2, move_wp_up_btn)
                    self.waypoints_table.setCellWidget(row_number, 3, move_wp_down_btn)
                    move_wp_up_btn.clicked.connect(self.move_wp_up_btn_clicked)
                    move_wp_down_btn.clicked.connect(self.move_wp_down_btn_clicked)
                    remove_wp_btn = QPushButton("Remove")
                    self.waypoints_table.setCellWidget(row_number, 4, remove_wp_btn)
                    remove_wp_btn.clicked.connect(self.remove_btn_clicked)

    def menubar(self):
        bar = self.menuBar()
        file = bar.addMenu("File")
        file.addAction("New")
        file.addAction("Open")
        file.addAction("Save")
        file.addAction("Save As")
        edit = bar.addMenu("Edit")
        edit.addAction("Cut")
        edit.addAction("Copy")
        edit.addAction("Paste")
    def gmap(self):
        pass
        """gmap = gmplot.GoogleMapPlotter(28.5355, 77.3910, 18)
        #gmap = gmplot.GoogleMapPlotter.from_geocode("San Francisco")
        gmap.apikey = "AIzaSyDeRNMnZ__VnQDiATiuz4kPjF_c9r1kWe8"
        gmap.draw("my_gmap.html")
        web = QWebEngineView()
        web.resize(620, 400)
        web.load(QUrl("my_gmap.html"))
        web.show()
        self.hbox1.addWidget(web)"""

    def vehicle_trail(self):
        pass
        """try:
            while True:
                location_prev = (self.vehicle.location.global_relative_frame.lat, self.vehicle.location.global_relative_frame.lon)
                time.sleep(2)
                location_new = (self.vehicle.location.global_relative_frame.lat, self.vehicle.location.global_relative_frame.lon)
                folium.PolyLine(locations = [location_prev, location_new], line_opacity = 0.5).add_to(self.my_folmap)
        except AttributeError:
            print("e69")"""
    def add_wp_onMapClick(self, message):
        if self.p.i % 2 == 0:
            self.click_location = []
            print("lat",self.p.i, type(message))
            self.waypoints_table.insertRow(self.wp_count)
            self.waypoints_table.setRowHeight(self.wp_count,15)
            remove_wp_btn = QPushButton("Remove")
            self.waypoints_table.setCellWidget(self.wp_count, 4, remove_wp_btn)
            move_wp_up_btn = QPushButton("Move Up")
            move_wp_down_btn = QPushButton("Move Down")
            self.waypoints_table.setCellWidget(self.wp_count, 2, move_wp_up_btn)
            self.waypoints_table.setCellWidget(self.wp_count, 3, move_wp_down_btn)
            remove_wp_btn.clicked.connect(self.remove_btn_clicked)
            move_wp_up_btn.clicked.connect(self.move_wp_up_btn_clicked)
            move_wp_down_btn.clicked.connect(self.move_wp_down_btn_clicked)
            self.waypoints_table.setItem(self.wp_count, 0, QTableWidgetItem(message))
            self.click_location.append(message)
        else:
            print("lon",self.p.i, message)
            self.waypoints_table.setItem(self.wp_count, 1, QTableWidgetItem(message))
            self.wp_count +=1
            self.click_location.append(message)

    def fol(self):
        self.my_folmap = folium.Map(location=[28.5011226, 77.4099794], zoom_start=10)
        f = open("latlng.html", "r")
        self.my_folmap.template_vars.update({'lat_lng_pop': f.read()})
        #self.my_folmap.polygon_marker(location=[28.5011226, 77.4099794], fill_color="red", fill_opacity=1, radius=10)
        #self.my_folmap.simple_marker(location=[28.5011226, 77.4099794], marker_color="red")
        #self.my_folmap.click_for_marker()
        #self.my_folmap.circle_marker(location=self.click_location, fill_color="red", fill_opacity=1, radius=3)
        #folium.CircleMarker(location=(28.5011226, 77.4099794),radius=5).add_to(self.my_folmap)
        self.my_folmap.create_map("my_folmap.html")
        self.web = QWebEngineView()
        #self.web.resize(600, 420)
        self.p = WebPage()
        self.web.setPage(self.p)
        #self.web.loadFinished.connect(self.onLoadFinished)
        self.web.load(QUrl("file:///home/vivek/Documents/Johnnette_tech/GroundControlStation/my_folmap.html"))
        #self.web.load(QUrl("my_folmap.html"))
        self.web.show()
        self.hbox1.addWidget(self.web, Qt.AlignCenter)
        self.p.loc_signal.connect(self.add_wp_onMapClick)
    def onLoadFinished(self, ok):
        if ok:
            self.web.page().runJavaScript("console.log(1111)", self.ready)
    def ready(self, returnValue):
        print(returnValue)
    def video(self, cap):
        ret, frame = cap.read()
        #frame = cv2.resize(frame, (750, 750))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgbImage = cv2.flip(frame, 1)
        convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                   rgbImage.shape[2] * rgbImage.shape[1], QImage.Format_RGB888)
        convertToQtFormat = QPixmap.fromImage(convertToQtFormat)
        img = QPixmap(convertToQtFormat)
        img = img.scaled(600, 470)
        return img
class WebPage(QWebEnginePage):
    loc_signal = pyqtSignal(str)
    i = 0
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        self.loc_signal.emit(message)
        self.i += 1
class VideoThread(QThread):
    vid_signal = pyqtSignal(object)
    def __init__(self, parent=None):
        super(VideoThread,self).__init__(parent)
        self.cap = cv2.VideoCapture(0)
    def run(self):
        while True:
            val = Window.video(self, self.cap)
            self.vid_signal.emit(val)
