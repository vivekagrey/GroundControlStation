
from dronekit import *
import dronekit.mavlink
from pymavlink import mavutil
import cv2
import os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import threading
import logging

class QPlainTextEditLogger(logging.Handler, QObject):
    appendPlainText = pyqtSignal(str)
    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)    
        self.appendPlainText.connect(self.widget.appendPlainText)
    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText.emit(msg)
class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.showMaximized()
        self.setGeometry(0,0,1000,500)
        self.setWindowTitle("Johnnette GCS")
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet("background-color:white; selection-color: white; selection-background-color: blue;border-width: 0px;padding: 0px; spacing: 0px;")
        #self.statusBar().showMessage("Copyright Johnnette Technologies, 2021")
        #self.menubar()
        self.log_msg = pyqtSignal(str, name='valChanged')
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
        self.head_grid_layout.setSpacing(0)
        self.header_frame = QFrame()
        #self.header_frame.move(0,0)
        self.header_frame.setMaximumHeight(70)
        self.header_frame.setLayout(self.head_grid_layout)
        self.Stack = QStackedLayout()
        self.Stack.setAlignment(Qt.AlignTop)
        #self.header_frame.setStyleSheet("selection-color: black;selection-background-color: powderblue;border-width: 0px;padding: 0px; spacing: 0px;")

        pagelayout.addWidget(self.header_frame)
        pagelayout.addLayout(self.Stack)

        self.widget = QWidget()
        #self.widget.setStyleSheet("border-width: 0px;padding: 0px; spacing: 0px;border:1px solid gray;")
        self.widget.setLayout(pagelayout)
        self.setCentralWidget(self.widget)

        self.stack_wid1 = QWidget()
        self.stack_wid2 = QWidget()
        self.stack_wid3 = QWidget()
        self.n = 1
        for n, page in enumerate([("Flight data", self.stack_wid1), ("Initial setup", self.stack_wid2), ("Help", self.stack_wid3)]):
            self.btn_ = QPushButton(str(page[0]))
            self.btn_.setFixedSize(100,70)
            self.btn_.setStyleSheet("QPushButton"
                             "{"
                             "background-color : white;"
                             "border-radius: 75px;"
                             "}"
                             "QPushButton::pressed"
                             "{"
                             "background-color : lightblue;"
                             "}")
            self.btn_.pressed.connect(lambda n=n: self.Stack.setCurrentIndex(n))
            self.head_grid_layout.addWidget(self.btn_, 0, n+1)
            self.Stack.addWidget(page[1])



        # pushButton = QPushButton("Help")
        # pushButton.setFixedSize(100, 70)
        # self.head_grid_layout.addWidget(pushButton,0,3)
        # pushButton.clicked.connect(self.on_pushButton_clicked)

        self.pushButton_connect = QPushButton("Connect")
        self.pushButton_connect.setFixedSize(100, 70)
        self.pushButton_connect.setStyleSheet("QPushButton"
                             "{"
                             "background-color : white;"
                             "}"
                             "QPushButton::pressed"
                             "{"
                             "background-color : lightblue;"
                             "}")
        self.head_grid_layout.addWidget(self.pushButton_connect, 0, 9)
        self.pushButton_connect.clicked.connect(self.connect_fc)

        #self.pushButton_connect.setCheckable(True)
        #self.pushButton_connect.toggle()
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
        self.combobox1.addItem("127.0.0.1:14540")
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
        spacer3 = QSpacerItem(20, 70)
        self.head_grid_layout.addItem(spacer3, 0, 8)
        spacer4 = QSpacerItem(10, 70)
        self.head_grid_layout.addItem(spacer4, 0, 10)

        label_grid = QGridLayout()
        self.head_grid_layout.addLayout(label_grid, 0, 5)

        self.mode_label = QLabel("MODE")
        label_grid.addWidget(self.mode_label, 0, 0)
        self.mode_label.setStyleSheet("font:bold 15pt Liberation Sans")

        self.details_label = QLabel("")
        label_grid.addWidget(self.details_label, 1, 0)
        self.details_label.setStyleSheet("font:Normal 12pt Liberation Sans")

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
            #self.loc_th.join()
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
            self.pushButtonlaunch.clicked.disconnect(self.abort)
            self.pushButtonlaunch.setText("Launch Mission")
            self.pushButtonlaunch.clicked.connect(self.launch_mission)
            print("104")
        except Exception as e:
            print("501", e)
        #print("buttan presse
        # d dis fc thr", self.pushButton_connect.isChecked())
        print("e40")
        self.combobox1.setCurrentIndex(0)
        self.combobox2.setCurrentIndex(0)
        print("e41")
    def combo_text(self):
        self.connection_string = str(self.combobox1.currentText())
        self.baud = str(self.combobox2.currentText())
        print("inside combo", self.connection_string, self.baud)
    def PX4setMode(self, mavMode):
        self.vehicle._master.mav.command_long_send(self.vehicle._master.target_system, self.vehicle._master.target_component,
                                               mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                                               mavMode,
                                               0, 0, 0, 0, 0, 0)
        print("pxmode",self.vehicle.home_location)
        
        time.sleep(2)
    def autopilot_logs_tab(self):    
        logTextBox = QPlainTextEditLogger(self)
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)

        # self.autopilot_logger = logging.getLogger()
        # self.autopilot_logger.addHandler(logTextBox)
        # # You can control the logging level
        # self.autopilot_logger.setLevel(logging.DEBUG)

        # self.label_logs = QLabel("Logs")
        # self.label_logs.setStyleSheet("font:bold 12pt Comic Sans MS")
        # self.label_logs.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(logTextBox.widget)
        self.tab4.setLayout(layout)

    # def test(self, m):
    #     self.autopilot_logger.debug("gvhjgj")
    #     self.autopilot_logger.debug("gvhjgj")
    #     self.autopilot_logger.debug("gvhjgj")
    #     self.autopilot_logger.debug("gvhjgj")
    #     self.autopilot_logger.debug("gvhjgj")

    #     self.autopilot_logger.log(
    #             msg=m.text.strip(),
    #             level=self._mavlink_statustext_severity[m.severity]
    #         )

    # def statustext_callback(self, object, attr_name, m):
        
    #     # sev=m.severity
    #     # msg=m.text.strip()
    #     #self.logs_text_field.appendPlainText(self.statustext_severity[sev]+": autopilot: "+msg)
    #     #print(self.statustext_severity[sev]+": autopilot:", msg)
    #     #self.label_logs.setText(self.statustext_severity[sev]+": autopilot: "+msg)
    #     # self.log_msg.valChanged.connect(self.test)
    #     # self.log_msg.emit(m)
    
    def thr(self):
        self.i = True
        print("e18")
        try:
            self._mavlink_statustext_severity = {
            0: logging.CRITICAL,
            1: logging.CRITICAL,
            2: logging.CRITICAL,
            3: logging.ERROR,
            4: logging.WARNING,
            5: logging.INFO,
            6: logging.INFO,
            7: logging.DEBUG
        }
            self.statustext_severity = {
            0: "CRITICAL",
            1: "CRITICAL",
            2: "CRITICAL",
            3: "ERROR",
            4: "WARNING",
            5: "INFO",
            6: "INFO",
            7: "DEBUG"
        }

            if self.connection_string == "SITL" or self.connection_string == "127.0.0.1:14540":
                import dronekit_sitl
                if self.connection_string == "SITL":
                    self.sitl = dronekit_sitl.start_default(lat=28.59622800000000, lon=77.38277600000000)
                    self.connection_string = self.sitl.connection_string()
                self.vehicle = connect(self.connection_string, wait_ready=False)
                # self.vehicle.add_message_listener('STATUSTEXT', self.statustext_callback)
                # self.vehicle.wait_ready(raise_exception=False)
                io = 0
                while (self.vehicle.mode == None or self.vehicle.airspeed == None or self.vehicle.parameters == None or self.vehicle.gps_0 == None or self.vehicle.armed == None or self.vehicle.attitude == None):   
                    waiting_params = [  "armed", 'mode',"parameters", 'airspeed',"gps_0","attitude"]
                    #vehicle.wait_ready('mode','airspeed',"parameters", "gps_0", "armed","attitude")
                    self.vehicle.wait_ready(waiting_params[io])
                    print("waiting...", waiting_params[io])
                    io+=1
                    self.progressbar.setValue(io*(100/6))
                    time.sleep(0.5)
                if "px4" in str(self.vehicle.version).lower():
                    self.px = True
                else:
                    self.px = False
                try:
                    if self.vehicle and self.cancel_flag == False:
                        self.pushButton_connect.clicked.disconnect(self.connect_fc)
                        self.pushButton_connect.setText("Disconnect")
                        #self.pushButton_connect.setChecked(True)
                        print("errrrrrrr2")

                        #self.timer.stop()
                        print("errrrrrrr3")
                        self.dialog_connect.close()
                        self.message = 1
                        print("aft m=1")
                        self.pushButton_connect.clicked.connect(self.disconnect_fc)
                        self.altitude = 15
                        self.alt_text.setValue(15)

                        self.listener_th = threading.Thread(target=self.listener_thr)
                        self.listener_th.start()
                        #self.loc_th = threading.Thread(target=self.current_loc_stats)
                        #self.loc_th.start()
                        print("100000")
                except AttributeError as e:
                    print(e)
                    #self.timer.stop()
                    self.dialog_connect.close()
                    self.message = 2
                    self.i = False
                    print("e3")
            else:
                if self.connection_string != "Select/Enter COM Port" and self.baud != "Select/Enter Baud":
                    self.vehicle = connect(self.connection_string, wait_ready=False, baud=self.baud)
                    io = 0
                    while (self.vehicle.mode == None or self.vehicle.airspeed == None or self.vehicle.parameters == None or self.vehicle.gps_0 == None or self.vehicle.armed == None or self.vehicle.attitude == None):   
                        waiting_params = [  "armed", 'mode',"parameters", 'airspeed',"gps_0","attitude"]
                        #vehicle.wait_ready('mode','airspeed',"parameters", "gps_0", "armed","attitude")
                        self.vehicle.wait_ready(waiting_params[io])
                        print("waiting...", waiting_params[io])
                        io+=1
                        self.progressbar.setValue(io*(100/6))
                        time.sleep(0.5)
                        print("after conn------",self.vehicle)
                        print("e16")
                    if "px4" in str(self.vehicle.version).lower():
                        self.px = True
                    else:
                        self.px = False
                    try:
                        if self.vehicle and self.cancel_flag == False:
                            self.vehicle.wait_ready(True, raise_exception=False)#false
                            self.pushButton_connect.setText("Disconnect")
                            self.pushButton_connect.setChecked(True)
                            self.pushButton_connect.clicked.disconnect(self.connect_fc)
                            #self.timer.stop()
                            self.dialog_connect.close()
                            print("e9")
                            self.message = 1
                            self.pushButton_connect.clicked.connect(self.disconnect_fc)
                            self.altitude = 15
                            self.alt_text.setValue(15)
                            self.listener_th = threading.Thread(target=self.listener_thr)
                            self.listener_th.start()
                            #self.loc_th = threading.Thread(target=self.current_loc_stats)
                            #self.loc_th.start()
                    except (Exception, dronekit.APIException,TypeError) as e:
                        #self.timer.stop()
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
                #self.timer.stop()
                self.dialog_connect.close()
                self.tt = True
                print("e13",  str(e))
                if self.i:
                    self.message = 6
                    print("e8")
            except AttributeError:
                try:
                    time.sleep(1)
                    #self.timer.stop()
                    self.dialog_connect.close()
                    self.message = 8
                    print("e7")
                except AttributeError:
                    self.message = 2
        self.mode_label.setText(str(self.vehicle.mode.name))
        self.details_label.setText("")
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
                if self.connection_string != "Select/Enter COM Port" and self.baud != "Select/Enter Baud" or self.connection_string == "SITL" or self.connection_string == "127.0.0.1:14540":
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
                    #self.timer = QBasicTimer()
                    #self.start_timer()
                    if self.i == False:
                        #self.timer.stop()
                        self.dialog_connect.close()
            except AttributeError:
                print("e4")
            self.altitude = 15
            print("1006")
            self.alt_text.setValue(15)
    # def start_timer(self):
    #     self.cnt = 0
    #     if self.timer.isActive():
    #         self.timer.stop()
    #     self.timer.start(50, self)
    # def timerEvent(self, event):
    #     self.cnt = self.cnt + .5
    #     self.progressbar.setValue(self.cnt)

    def cancel_connect_th(self):
        #self.timer.stop()
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
    def get_distance_metres(self, aLocation1, aLocation2):
        """
        Returns the ground distance in metres between two LocationGlobal objects.

        This method is an approximation, and will not be accurate over large distances and close to the 
        earth's poles. It comes from the ArduPilot test code: 
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """
        dlat = aLocation2.lat - aLocation1.lat
        dlong = aLocation2.lon - aLocation1.lon
        return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5
    def position_messages_from_tlog(self, filename):
        """
        Given telemetry log, get a series of wpts approximating the previous flight
        """
        # Pull out just the global position msgs
        messages = []
        mlog = mavutil.mavlink_connection(filename)
        while True:
            try:
                m = mlog.recv_match(type=['GLOBAL_POSITION_INT'])
                if m is None:
                    break
            except Exception:
                break
            # ignore we get where there is no fix:
            if m.lat == 0:
                continue
            messages.append(m)

        # Shrink the number of points for readability and to stay within autopilot memory limits. 
        # For coding simplicity we:
        #   - only keep points that are with 3 metres of the previous kept point.
        #   - only keep the first 100 points that meet the above criteria.
        num_points = len(messages)
        keep_point_distance=3 #metres
        kept_messages = []
        kept_messages.append(messages[0]) #Keep the first message
        pt1num=0
        pt2num=1
        while True:
            #Keep the last point. Only record 99 points.
            if pt2num==num_points-1 or len(kept_messages)==99:
                kept_messages.append(messages[pt2num])
                break
            pt1 = LocationGlobalRelative(messages[pt1num].lat/1.0e7,messages[pt1num].lon/1.0e7,0)
            pt2 = LocationGlobalRelative(messages[pt2num].lat/1.0e7,messages[pt2num].lon/1.0e7,0)
            distance_between_points = self.get_distance_metres(pt1,pt2)
            if distance_between_points > keep_point_distance:
                kept_messages.append(messages[pt2num])
                pt1num=pt2num
            pt2num=pt2num+1

        return kept_messages
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
        self.tabs.addTab(self.tab4, "Autopilot Logs")
        self.waypoints()
        self.action()
        self.quick_stats()
        self.autopilot_logs_tab()

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

        action_btn_4 = QPushButton("Download Logs")
        self.actiongrid.addWidget(action_btn_4, 1, 1)
        #action_btn_4.clicked.connect(self.download_logs)

        action_btn_5 = QPushButton("FORCE DISARM")
        self.actiongrid.addWidget(action_btn_5, 1, 2)
        action_btn_5.clicked.connect(self.force_disarm)


        action_btn_8 = QPushButton("SET GROUND SPEED(m/s)")
        self.actiongrid.addWidget(action_btn_8, 1, 3)
        action_btn_8.clicked.connect(self.set_ground_speed)

        self.combobox_action_1 = QComboBox()
        self.combobox_action_1.addItems(["Select Mode", "Stabilize", "Guided","Loiter", "Simple Takeoff", "Land", "Alt Hold", "RTL"])
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

    def download_logs(self):
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
    def yaw_callback(self, object, attr_name, value):
        val = str(value).split(":")[1]
        self.quickyaw = val.split(",")[1]
        self.label_1.setText(self.quickyaw)
        self.attribute_msg = attr_name

    def gpsinfo_callback(self, object, attr_name, value):
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

    def sysStatus_callback(self,object, attr_name, value):
        self.modelis = (str(value)).split(":")[1]
        self.mode_label.setText(self.modelis)
        self.attribute_msg = attr_name
    def listener_thr(self):
        while not self.pushButton_connect.text() == "Disconnect":
            time.sleep(2)
        try:
            self.vehicle.add_attribute_listener('attitude', self.yaw_callback)  #
            self.vehicle.add_attribute_listener('location.global_relative_frame', self.altitude_callback)  # in m/s
            self.vehicle.add_attribute_listener('gps_0', self.gpsinfo_callback)  # in m/s
            self.vehicle.add_attribute_listener('voltage', self.voltage_callback)  # in m/s
            self.vehicle.add_attribute_listener('groundspeed', self.groundspeed_callback)  # in m/s
            self.vehicle.add_attribute_listener('velocity', self.verticalspeed_callback)  # in m/s
            self.vehicle.add_attribute_listener('mode', self.sysStatus_callback)  # in m/s

            # time.sleep(2)
            # self.vehicle.remove_attribute_listener('mode', self.sysStatus_callback)
            # self.vehicle.remove_attribute_listener('attitude', self.yaw_callback)
            # self.vehicle.remove_attribute_listener('location.global_relative_frame', self.altitude_callback)
            # self.vehicle.remove_attribute_listener('gps_0', self.gpsinfo_callback)
            # self.vehicle.remove_attribute_listener('voltage', self.voltage_callback)
            # self.vehicle.remove_attribute_listener('groundspeed', self.groundspeed_callback)
            # self.vehicle.remove_attribute_listener('velocity', self.verticalspeed_callback)
        except Exception as e:
            print(e)


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
            # elif self.mode == "Auto":
            #     self.home_position_set = False

            #     try:
            #         self.set_mode_thr.join()
            #     except AttributeError:
            #         print("mode exception raised")                
            #     if self.px:
            #         self.PX4setMode(4)
            #         print("px4 auto", self.px)
            #     else:
            #         self.set_mode_thr = threading.Thread(target=self.set_automode_thr)
            #         self.set_mode_thr.start()
            #         print("px4 auto", self.px)
            #     print("Auto mode set")
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
            # elif self.mode == "Takeoff":
            #     print("takeoff")
            #     try:
            #         self.set_mode_thr.join()
            #     except AttributeError:
            #         print("mode exception raised")
            #     self.set_mode_thr = threading.Thread(target=self.set_takeoffmode_thr)
            #     self.set_mode_thr.start()
            #     print("Takeoff mode set")
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
            
            self.details_label.setText("")

        except AttributeError:
            print("No vehicle connected")

    def set_rtlmode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("RTL")
            while not self.vehicle.mode.name == "RTL":
                time.sleep(0.2)
            
            self.details_label.setText("")

        except AttributeError:
            print("No vehicle connected")

    def set_loitermode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("LOITER")
            while not self.vehicle.mode.name == "LOITER":
                time.sleep(0.2)
            
            self.details_label.setText("")

        except AttributeError:
            print("No vehicle connected")

    # def set_automode_thr(self):
    #     try:
    #         self.vehicle.mode = VehicleMode("AUTO")
    #         while not self.vehicle.mode.name == "AUTO":
    #             time.sleep(0.2)
    #             print("armed",self.vehicle.armed)
    #         
    #          self.details_label.setText("")

    #     except AttributeError:
    #         print("No vehicle connected")

    def set_landmode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("LAND")
            while not self.vehicle.mode.name == "LAND":
                time.sleep(0.2)
            
            self.details_label.setText("")
        except AttributeError:
            print("No vehicle connected")

    # def set_takeoffmode_thr(self):
    #     try:
    #         self.vehicle.mode = VehicleMode("TAKEOFF")
    #         while not self.vehicle.mode.name == "TAKEOFF":
    #             time.sleep(0.2)
    #         
    #         self.details_label.setText("")
    #     except AttributeError:
    #         print("No vehicle connected")

    def set_altholdmode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("ALT_HOLD")
            while not self.vehicle.mode.name == "ALT_HOLD":
                time.sleep(0.2)
            
            self.details_label.setText("")

        except AttributeError:
            print("No vehicle connected")

    def set_guidedmode_thr(self):
        try:
            self.vehicle.mode = VehicleMode("GUIDED")
            while not self.vehicle.mode.name == "GUIDED":
                time.sleep(0.1)
            
            self.details_label.setText("")
        except AttributeError:
            print("No vehicle connected")

    #Create a message listener for home position fix
    
    def launch_mission_th_method(self):
        try:
            if not self.px:
                self.vehicle.mode = "GUIDED"
                self.vehicle.armed = True
                while not self.vehicle.mode.name == "GUIDED":
                    time.sleep(1.0)
                while not self.vehicle.is_armable:
                    print(" Waiting for vehicle to initialise...")
                    time.sleep(1)
            else:
                self.PX4setMode(4)
                time.sleep(1)
                self.vehicle.armed = True
            #self.vehicle.commands.next = 1
            # print("565656565656")
            # if self.vehicle.mode.name != "AUTO" and self.vehicle.mode.name != "MISSION":
            #     print("hi",self.vehicle.mode.name)
            #     self.message = 3
            #     return   
            #print("Basic pre-arm checks")
            # Don't let the user try to arm until autopilot is ready            
            while not self.vehicle.armed:
                print(" Waiting for arming...")
                time.sleep(1)
            if not self.px:
                print("not px4")
                msg = self.vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0)
                self.vehicle.send_mavlink(msg)
            self.next = threading.Thread(target=self.next_wp)
            self.next.start()
            self.mode_label.setText("MISSION MODE")
            #self.pushButtonlaunch.clicked.disconnect(self.launch_mission)
            #self.pushButtonlaunch.setText("Abort Mission")
            #self.pushButtonlaunch.clicked.connect(self.abort)
        except AttributeError:
            print("201")
    def next_wp(self):
        # monitor mission execution
        if self.px:
            nextwaypoint = self.vehicle.commands.next
            while nextwaypoint <= len(self.vehicle.commands):
                if self.vehicle.commands.next > nextwaypoint:
                    display_seq = self.vehicle.commands.next
                    print("Moving to waypoint %s" % display_seq)
                    self.details_label.setText("Moving to waypoint %s" % display_seq)
                    nextwaypoint = self.vehicle.commands.next
                time.sleep(1)
                print("ma", nextwaypoint, len(self.vehicle.commands))
                if  nextwaypoint == len(self.vehicle.commands):
                    break
        else:
            self.vehicle.commands.next = 0
            nextwaypoint = self.vehicle.commands.next
            while nextwaypoint <= len(self.vehicle.commands) :
                if self.vehicle.commands.next > nextwaypoint and self.vehicle.commands.next > 1:
                    display_seq = self.vehicle.commands.next - 1
                    print("Moving to waypoint - %s" % display_seq)
                    self.details_label.setText("Moving to waypoint %s" % display_seq)
                    nextwaypoint = self.vehicle.commands.next
                time.sleep(1)
                print("ma", nextwaypoint, len(self.vehicle.commands))
                if  nextwaypoint == len(self.vehicle.commands):
                    break
        #self.details_label.setText("Mission accompliced")
            # wait for the vehicle to land
        # while self.vehicle.commands.next > 0:
        #     time.sleep(1)
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
        self.details_label.setText("")
    def launch_mission(self):
        try:
            self.abort_th.join()
            self.launch_mission_th.join()
        except AttributeError:
            print("e57")
        try:
            if self.wps_uploaded2uav == True:
                self.launch_mission_th = threading.Thread(target=self.launch_mission_th_method)
                self.launch_mission_th.start()
            else:
                self.message = 3
        except AttributeError:
            self.message = 3
    def set_simpletakeoff_thr(self):
        try:
            self.mode_label.setText("TAKEOFF")
            self.details_label.setText("")
            print("Basic pre-arm checks")
            #Don't let the user try to arm until autopilot is ready
            # while not self.vehicle.is_armable:
            #     print(" Waiting for vehicle to initialise...")
            #     time.sleep(1)
            # print("Arming motors")
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
                self.mode_label.setText("Mission Aborted")
                self.details_label.setText("")
                while self.vehicle.location.global_relative_frame.alt >= 0.2:
                    time.sleep(1)
            self.mds = self.vehicle.commands
            self.mds.clear()
            self.wps_uploaded2uav = False
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
        #self.pushButton_re.clicked.disconnect(self.re_launch_mission)
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
        self.wp_count = 0
        hbox = QHBoxLayout()
        self.tab2.setLayout(hbox)
        self.waypoints_table = QTableWidget()
        hbox.addWidget(self.waypoints_table)
        self.waypoints_table.horizontalHeader().setStretchLastSection(True)
        self.waypoints_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #self.waypoints_table.verticalHeader().setVisible(False)
        self.waypoints_table.show()
        self.waypoints_table.itemChanged.connect(self.table_item_changed)
        self.waypoints_table.setEditTriggers(QTableWidget.NoEditTriggers)
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
        btn11 = QPushButton("Upload WP File")
        waypoints_button_grid.addWidget(btn11, 0, 0)
        btn11.clicked.connect(self.upload_custom_wps)

        btn12 = QPushButton("Download Logs")
        waypoints_button_grid.addWidget(btn12, 1, 0)
        btn12.clicked.connect(self.download_logs)

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
        waypoints = []
        print("row count:", self.waypoints_table.rowCount())
        for row in range(self.waypoints_table.rowCount()):
            waypoint = {}
            lat = self.waypoints_table.item(row, 0)
            lon = self.waypoints_table.item(row, 1)
            waypoint[float(lat.text())] = float(lon.text())
            waypoints.append(waypoint)
            self.vehicle
        try:
            cmds = self.vehicle.commands
            print("Clear any existing commands")
            cmds.clear()
            # if self.vehicle.home_location is None:
            #     self.vehicle.home_location = LocationGlobal(-35.3628118424579,149.16467813602, self.altitude)
            #     print(self.vehicle.home_location)
            #home = self.vehicle.location.global_relative_frame
            # self.vehicle.home_location=vehicle.location.global_frame

            try:
                if self.vehicle.home_location is None:
                    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0,self.altitude))
                else:
                    print("loc not none")
                    cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 0, 0, 0, 0, self.vehicle.home_location.lat, self.vehicle.home_location.lon, self.altitude))
                for wp in waypoints:
                    i, j = list(wp.keys()), list(wp.values())
                    print("hi", float(i[0]),j[0])
                    cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0, i[0], j[0], self.altitude))
                #cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 1, 0, 0, 0, 0, 0, 0, 0))
                #cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 1, 0, 0, 0, 0, i[0], j[0], self.altitude))
                print("uploading mission commands")
                cmds.upload()
                time.sleep(1)
                self.message = 7
                self.wps_uploaded2uav = True
            #except (AttributeError, UnboundLocalError):
            except Exception as e:
                print(e)
                self.message = 4
        except Exception as e:
            print(e)
            self.message = 2

    def delete_all_wps(self):
        for row in range(self.wp_count):
            self.remove_btn_clicked(custom_wp=True)

    def move_wp_down_btn_clicked(self):
        button = self.sender()
        row = self.waypoints_table.indexAt(button.pos()).row()
        if row != self.wp_count-1:
            try:
                lat_plus_1 = self.waypoints_table.item(row + 1, 0).text()
                lon_plus_1 = self.waypoints_table.item(row + 1, 1).text()
                id_plus_1 = self.waypoints_table.verticalHeaderItem(row + 1).text()
                rowID_plus_1 = QTableWidgetItem(id_plus_1)

                lat = self.waypoints_table.item(row, 0).text()
                lon = self.waypoints_table.item(row, 1).text()
                id = self.waypoints_table.verticalHeaderItem(row).text()
                rowID = QTableWidgetItem(id)

                self.waypoints_table.setItem(row + 1, 0, QTableWidgetItem(lat))
                self.waypoints_table.setItem(row + 1, 1, QTableWidgetItem(lon))
                self.waypoints_table.setVerticalHeaderItem(row + 1, rowID)

                self.waypoints_table.setItem(row, 0, QTableWidgetItem(lat_plus_1))
                self.waypoints_table.setItem(row, 1, QTableWidgetItem(lon_plus_1))
                self.waypoints_table.setVerticalHeaderItem(row,rowID_plus_1)

            except AttributeError:
                self.message = 9
    def move_wp_up_btn_clicked(self):
        button = self.sender()
        row = self.waypoints_table.indexAt(button.pos()).row()
        if row != 0:
            try:
                lat_minus_1 = self.waypoints_table.item(row - 1, 0).text()
                lon_minus_1 = self.waypoints_table.item(row - 1, 1).text()
                id_minus_1 = self.waypoints_table.verticalHeaderItem(row - 1).text()
                rowID_minus_1 = QTableWidgetItem(id_minus_1)

                lat = self.waypoints_table.item(row, 0).text()
                lon = self.waypoints_table.item(row, 1).text()
                id = self.waypoints_table.verticalHeaderItem(row).text()
                rowID = QTableWidgetItem(id)

                self.waypoints_table.setItem(row - 1, 0, QTableWidgetItem(lat))
                self.waypoints_table.setItem(row - 1, 1, QTableWidgetItem(lon))
                self.waypoints_table.setVerticalHeaderItem(row - 1, rowID)

                self.waypoints_table.setItem(row, 0, QTableWidgetItem(lat_minus_1))
                self.waypoints_table.setItem(row, 1, QTableWidgetItem(lon_minus_1))
                self.waypoints_table.setVerticalHeaderItem(row,rowID_minus_1)
            except AttributeError:
                self.message = 9
    def remove_btn_clicked(self,custom_wp = False):
        button = self.sender()
        if custom_wp:
            while self.wp_count != 0:
                try:
                    id = self.waypoints_table.verticalHeaderItem(0).text()
                    self.waypoints_table.removeRow(0)
                    self.markerEvent(marker=False,id=id)
                    self.wp_count -= 1
                except Exception as e:
                    print(e)
                    break
        else:
            row = self.waypoints_table.indexAt(button.pos()).row()
            id = self.waypoints_table.verticalHeaderItem(row).text()
            self.waypoints_table.removeRow(row)
            self.markerEvent(marker=False,id=id)
            self.wp_count -= 1

            
    def remove_wp_from_table_by_click(self, message):
        for row in range(self.waypoints_table.rowCount()):
            lat = self.waypoints_table.item(row, 0)
            lon = self.waypoints_table.item(row, 1)
            if float(lat.text()) == float(message[1]) and float(lon.text()) == float(message[2]):
                self.waypoints_table.removeRow(row)
                self.wp_count-=1
                break
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
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  filter="CSV Format Files (*.csv);;TLog files (*.tlog)", options=options)
        if filename:
            if self.wp_count:
                msg = QMessageBox.warning(self.widget, "Warning", "Waypoints' table will be overwritten.\nAre you Sure?",buttons = QMessageBox.Ok | QMessageBox.Cancel )
            else:
                msg = QMessageBox.Ok
            if msg == QMessageBox.Ok:
                if ".tlog" in filename:
                    print("Generating waypoints from tlog...")
                    messages = self.position_messages_from_tlog("flight.tlog")
                    print(" Generated %d waypoints from tlog" % len(messages))
                    if len(messages) == 0:
                        print("No position messages found in log")
                        exit(0)
                    wp = []
                    for pt in messages:
                    #print "Point: %d %d" % (pt.lat, pt.lon,)
                        lat = pt.lat
                        lon = pt.lon
                        print(lat, lon)
                        self.markerEvent(marker=True,lat=lat,lng=lon)

                else:
                    with open(filename, 'r') as csvfile:
                        # creating a csv reader object
                        csvreader = csv.reader(csvfile)
                        # self.waypoints_table.setRowCount(0)
                        for row in range(self.wp_count):
                            self.remove_btn_clicked(custom_wp=True)
                        for row_number, row_data in enumerate(csvreader):
                            # self.waypoints_table.insertRow(row_number)
                            # self.waypoints_table.setRowHeight(row_number, 15)
                            try:                  
                                wp = []
                                for column_number, data in enumerate(row_data):
                                    if column_number < 2:
                                        #self.waypoints_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                                        wp.append(str(data))
                                        print(wp)
                                    else:return
                                self.markerEvent(marker=True,lat=wp[0],lng=wp[1])
                            except Exception as e:
                                print(e)
                            # self.wp_count+=1
                            # print("marker_id", self.markerID)
                            # rowID = QTableWidgetItem(self.markerID)
                            # self.waypoints_table.setVerticalHeaderItem(self.wp_count,rowID)
                            # move_wp_up_btn = QPushButton("Move Up")
                            # move_wp_down_btn = QPushButton("Move Down")
                            # self.waypoints_table.setCellWidget(row_number, 2, move_wp_up_btn)
                            # self.waypoints_table.setCellWidget(row_number, 3, move_wp_down_btn)
                            # move_wp_up_btn.clicked.connect(self.move_wp_up_btn_clicked)
                            # move_wp_down_btn.clicked.connect(self.move_wp_down_btn_clicked)
                            # remove_wp_btn = QPushButton("Remove")
                            # self.waypoints_table.setCellWidget(row_number, 4, remove_wp_btn)
                            # remove_wp_btn.clicked.connect(self.remove_btn_clicked)

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


    def updateMarkerID(self,message):
            message = message.split(',')
            self.markerID = message[3]
    def add_wp_onMapClick(self, message):
            message = message.split(',')
            if int(message[0]):
                self.waypoints_table.insertRow(self.wp_count)
                rowID = QTableWidgetItem(self.markerID)
                self.waypoints_table.setVerticalHeaderItem(self.wp_count,rowID)
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
                item1 = QTableWidgetItem(message[1])
                item2 = QTableWidgetItem(message[2])
                self.waypoints_table.setItem(self.wp_count, 0, item1)
                self.waypoints_table.setItem(self.wp_count, 1, item2)
                self.wp_count +=1
            else:
                self.remove_wp_from_table_by_click(message)
    def fol(self):
    #     f = open("latlng.html", "r")
    #     self.my_folmap.template_vars.update({'lat_lng_pop': f.read()})
        self.web = QWebEngineView()
        # self.web.resize(600, 420)
        self.p = WebPage()
        self.web.setPage(self.p)
        # self.web.loadFinished.connect(self.onLoadFinished)
        # path = os.path.dirname(os.path.realpath(__file__))
        # path = os.path.join(path, "customMap.html")
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "customMap.html"))
        localurl = QUrl.fromLocalFile(file_path)
        self.web.load(QUrl(localurl))
        # self.web.load(QUrl("my_folmap.html"))
        self.web.show()
        self.hbox1.addWidget(self.web, Qt.AlignCenter)
        self.p.loc_signal.connect(self.updateMarkerID)
        self.p.loc_signal.connect(self.add_wp_onMapClick)

    #def fol(self):
    #     self.mymap = folium.Map(location=[28.5011226, 77.4099794], zoom_start=10)
    #     a=self.mymap.circle_marker(location=[28.5011226, 77.4099794], radius=500, fill_opacity=.6)
    #     self.mymap.create_map("test.html")
    #     self.web = QWebEngineView()
    #     self.p = WebPage()
    #     self.web.setPage(self.p)
    #     self.web.load(QUrl("file:///home/vivek/Documents/Johnnette_tech/GroundControlStation/test.html"))
    #     self.web.show()
    #     self.hbox1.addWidget(self.web, Qt.AlignCenter)
    #     #self.web.loadFinished.connect(self.onLoadFinished)
    #     self.p.loc_signal.connect(self.add_wp_onMapClick)
    def markerEvent(self, marker,id=None,lat=None,lng=None):
        if marker:
            self.web.page().runJavaScript("python_call_add("+lat+","+lng+");", self.ready)
        else:
            self.web.page().runJavaScript("python_call_remove("+id+");", self.ready)
    def ready(self, returnValue):
        pass
        #print("hi====",returnValue)
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
        #print("jsmessage",message, level, lineNumber)
        self.loc_signal.emit(message)
        self.i += 1
# class Connector(QThread):
#     sig = pyqtSignal(str)
#     def __init__(self, parent=None):
#         super(Connector,self).__init__(parent)

class VideoThread(QThread):
    vid_signal = pyqtSignal(object)
    def __init__(self, parent=None):
        super(VideoThread,self).__init__(parent)
        self.cap = cv2.VideoCapture(0)
        self._lock = threading.Lock()
        self.running = False
    def stop(self):
        self.running = False
        print('received stop signal from window.')
        with self._lock:
            self._do_before_done()

    def _do_work(self):
        val = Window.video(self, self.cap)
        self.vid_signal.emit(val)

    def _do_before_done(self):
        print('waiting 3 seconds before thread done..')
        for i in range(3, 0, -1):
            print('{0} seconds left...'.format(i))
            self.sleep(1)
        print('ok, thread done.')
    def run(self):
        self.running = True
        while self.running:
            with self._lock:
                self._do_work()

