import re
import sys
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, \
    QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QByteArray


class SerialWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.lumin = None
        self.elaps = None
        self.port = None
        self.baud_rate = None
        self.setWindowTitle("WaterFall")
        self.setWindowIcon(QIcon("WaterFall.png"))
        self.serial_port = None
        self.packet_timer = None
        self.ok_num = 0
        self.packet_num = 0

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        baud_label = QLabel("Baud")
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["115200", "9600", "57600", "38400"])
        self.baud_combo.setCurrentIndex(0)
        self.baud_combo.currentIndexChanged.connect(self.save_baud_rate)

        com_label = QLabel("COM")
        self.com_combo = QComboBox()
        self.com_combo.currentIndexChanged.connect(self.save_port)
        #self.update_ports()

        heart_label = QLabel("Elapse")
        self.heart_edit = QLineEdit('1')
        #self.heart_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略为Expanding
        #self.heart_edit.textChanged.connect(lambda: self.text_lable_just(self.heart_edit))
        self.heart_edit.setStyleSheet("color: red;font-weight: bold;")
        self.heart_edit.textChanged.connect(self.save_elaps)
        metric_label = QLabel("ms")

        hbox1 = QHBoxLayout()
        hbox1.addWidget(baud_label)
        hbox1.addWidget(self.baud_combo)
        hbox1.addWidget(com_label)
        hbox1.addWidget(self.com_combo)
        hbox1.addWidget(heart_label)
        hbox1.addWidget(self.heart_edit)
        hbox1.addWidget(metric_label)

        main_layout.addLayout(hbox1)
        lumin_label = QLabel("Lumin")
        self.lumin_edit = QLineEdit("100")
        #self.lumin_edit.setPlaceholderText("100")
        #self.lumin_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略为Expanding
        #self.lumin_edit.textChanged.connect(lambda: self.text_lable_just(self.lumin_edit))
        self.lumin_edit.setStyleSheet("color: blue;font-weight: bold;")
        self.lumin_edit.textChanged.connect(self.save_lumin)

        self.send_button = QPushButton("Send")
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send_packet)
        #self.update_ports()
        state_label = QLabel("Conn")
        #state_label.setStyleSheet("color: red;font-weight: bold;")
        self.text_label = QLabel()
        self.text_label.setStyleSheet("color: red;font-weight: bold;")

        hbox2 = QHBoxLayout()
        hbox2.addWidget(lumin_label)
        hbox2.addWidget(self.lumin_edit)
        hbox2.addWidget(self.send_button)
        hbox2.addWidget(state_label)
        hbox2.addWidget(self.text_label)

        main_layout.addLayout(hbox2)

        self.setLayout(main_layout)

        self.adjustSize()

        self.setFixedSize(self.size())

        self.update_ports()

    def text_lable_just(self, sender):
        # font_metrics = self.token_label.fontMetrics()
        font_metrics = sender.fontMetrics()
        width = font_metrics.width(sender.text())
        height = font_metrics.height()
        # self.token_label.setFixedSize(width + 40, height + 30)
        sender.setFixedSize(width + 10, height)

    def update_ports(self):
        # ports = serial.tools.list_ports.comports()
        # for port in ports:
        #     self.com_combo.addItem(port.device)
        self.com_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if ports:
            self.com_combo.addItems(ports)
            self.send_button.setEnabled(True)

    def save_baud_rate(self, index):
        self.baud_rate = int(self.baud_combo.currentText())

    def save_port(self, index):
        self.port = self.com_combo.currentText()

    def save_elaps(self, text):
        txt_show = re.sub(r'\D', '', text)
        if txt_show.isdigit():
            if int(txt_show) > 10000:
                txt_show = str(int(txt_show)//10)
            else:
                txt_show = str(int(txt_show))
        else:
            txt_show = '0'
        self.heart_edit.setText(txt_show)
        self.elaps = int(txt_show)

    def save_lumin(self, text):
        txt_show = re.sub(r'\D', '', text)
        if txt_show.isdigit():
            if 0 <= int(txt_show) <= 100:
                txt_show = str(int(txt_show))
            elif int(txt_show) > 100:
                txt_show = str(int(txt_show)//10)
            else:
                txt_show = '0'
        else:
            txt_show = '0'
        self.lumin_edit.setText(txt_show)
        self.lumin = int(txt_show)

    def send_packet(self):
        if self.send_button.text() == "Send":
            self.baud_rate = int(self.baud_combo.currentText())
            self.port = self.com_combo.currentText()
            self.elaps = int(self.heart_edit.text())
            if self.serial_port is None:
                try:
                    self.serial_port = serial.Serial(self.port, self.baud_rate, timeout=1)
                except serial.SerialException as e:
                    print(e)
                    return
            # self.lumin = int(self.lumin_edit.text())
            if not self.packet_timer:
                self.packet_timer = QTimer()
                self.packet_timer.timeout.connect(self.send_data)
            self.packet_timer.start(self.elaps)
            self.send_button.setText("End")
            self.heart_edit.setEnabled(False)
            self.lumin_edit.setEnabled(False)
        else:
            if self.serial_port:
                self.serial_port.close()
                self.serial_port = None
            if self.packet_timer:
                self.packet_timer.stop()
            self.send_button.setText("Send")
            self.heart_edit.setEnabled(True)
            self.lumin_edit.setEnabled(True)

    def send_data(self):
        self.lumin = int(self.lumin_edit.text())
        packet = bytearray(
            [0x55, 0xaa, 0x00, 0x00, 0xfe, 0xff, 0x01, 0xff, 0xff, 0xff, 0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x01, 0x00,
             self.lumin])
        packet.extend([0x55, 0x55])
        #print(packet)
        checksum = sum(packet[2:])
        #print(checksum)
        sum_h = checksum // 256
        sum_l = checksum % 256
        #print(bytes([sum_l, sum_h]))
        packet = packet[:-2]
        packet.extend([sum_l, sum_h])
        print(f'Tx: | Elapse: {self.elaps}ms | Lumin: {self.lumin} | {self.port} | {self.baud_rate} | →→→ | {bytes(packet)}')
        self.serial_port.write(packet)
        self.packet_num += 1
        response = self.serial_port.read_all()
        self.check_response(response)

    def check_response(self, response):
        set_OK = bytearray(
            [0xaa, 0x55, 0x00, 0x00, 0xff, 0xfe, 0x01, 0xff, 0xff, 0xff, 0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x00, 0x00,
             0x54, 0x5a])
        if response == set_OK:
            self.ok_num += 1
        if self.ok_num == self.packet_num:
            self.text_label.setText("Good")
        else:
            self.text_label.setText("Fail")
        print(f'Rx: | Lumin: {self.lumin} | Config: {"Good" if response == set_OK else "Fail"} | {"→"*12} | {response} ')
    def closeEvent(self, event):
        if self.serial_port:
            self.serial_port.close()
        if self.packet_timer:
            self.packet_timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialWindow()
    window.show()
    sys.exit(app.exec_())
