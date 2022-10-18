# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'video2Stream.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from scapy.all import *
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
import math
import time
import os
from threading import Thread
import cv2
import numpy as np
from psutil import net_if_addrs

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import *


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)

        #Video
        self.video_path = ''
        self.video_capture = None
        self.frames = 0
        self.fps = 0
        self.interpolation = None
        self.send_pkts = None
        #Packet
        self.flag = False
        self.h16_pb = self.gen_first16_PKT(pkt_len=pkt_len, ctrlWords=ctrl_params)
        self.h16_pb[1] = self.luminJust(TP_AUTO_EN, brt, TEST_PAT,
                               GCG, CSTEP_B, CSTEP_G, CSTEP_R,
                               self.h16_pb[1], pkt_len=pkt_len)
        #self.fstart_time = 0
        #self.fend_time = 0

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        #MainWindow.resize(431, 174)
        MainWindow.setFixedSize(430, 174)
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap("pics/皮卡丘.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap("pics/Triskele.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.openFileButton1 = QtWidgets.QPushButton(self.centralwidget)
        self.openFileButton1.setGeometry(QtCore.QRect(20, 10, 75, 31))
        self.openFileButton1.setObjectName("openFileButton1")
        self.videoGenButton1 = QtWidgets.QPushButton(self.centralwidget)
        self.videoGenButton1.setEnabled(False)
        self.videoGenButton1.setGeometry(QtCore.QRect(340, 10, 75, 31))
        self.videoGenButton1.setObjectName("videoGenButton1")
        self.sendingButton1 = QtWidgets.QPushButton(self.centralwidget)
        self.sendingButton1.setEnabled(False)
        self.sendingButton1.setGeometry(QtCore.QRect(340, 100, 75, 31))
        self.sendingButton1.setObjectName("sendingButton1")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(150, 10, 131, 131))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setTextFormat(QtCore.Qt.RichText)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.dstWidthVal = QtWidgets.QLineEdit(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("隶书")
        font.setPointSize(12)

        reg = QRegExp('[0-9]+$')
        validator = QRegExpValidator(self)
        validator.setRegExp(reg)
        #self.lineEdit.setValidator(validator)

        self.dstWidthVal.setFont(font)
        self.dstWidthVal.setAlignment(QtCore.Qt.AlignCenter)
        self.dstWidthVal.setObjectName("dstWidthVal")
        self.dstWidthVal.setValidator(validator)
        self.dstWidthVal.setText('256')
        self.dstWidthVal.setEnabled(False)
        self.gridLayout.addWidget(self.dstWidthVal, 0, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.dstHeightVal = QtWidgets.QLineEdit(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("隶书")
        font.setPointSize(12)
        self.dstHeightVal.setFont(font)
        self.dstHeightVal.setAlignment(QtCore.Qt.AlignCenter)
        self.dstHeightVal.setObjectName("dstHeightVal")
        self.dstHeightVal.setValidator(validator)
        self.dstHeightVal.setText('48')
        self.dstHeightVal.setEnabled(False)
        self.gridLayout.addWidget(self.dstHeightVal, 1, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)
        self.alg_Box = QtWidgets.QComboBox(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("隶书")
        font.setPointSize(12)
        self.alg_Box.setFont(font)
        self.alg_Box.setObjectName("alg_Box")
        itp_alg = ["LINEAR", "NEAREST", "AREA", "CUBIC", "LANCZOS4"]

        self.alg_Box.addItems(itp_alg)

        self.gridLayout.addWidget(self.alg_Box, 2, 1, 1, 1)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(0, 40, 121, 94))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.layoutWidget1)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.srcVideoName = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(12)
        self.srcVideoName.setFont(font)
        self.srcVideoName.setText("")
        self.srcVideoName.setAlignment(QtCore.Qt.AlignCenter)
        self.srcVideoName.setObjectName("srcVideoName")
        self.gridLayout_3.addWidget(self.srcVideoName, 0, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_9 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(12)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 0, 0, 1, 1)
        self.srcWidthVal = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(12)
        self.srcWidthVal.setFont(font)
        self.srcWidthVal.setText("")
        self.srcWidthVal.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.srcWidthVal.setObjectName("srcWidthVal")
        self.gridLayout_2.addWidget(self.srcWidthVal, 0, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(12)
        self.label_11.setFont(font)
        self.label_11.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 1, 0, 1, 1)
        self.srcHeightVal = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(12)
        self.srcHeightVal.setFont(font)
        self.srcHeightVal.setText("")
        self.srcHeightVal.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.srcHeightVal.setObjectName("srcHeightVal")
        self.gridLayout_2.addWidget(self.srcHeightVal, 1, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(12)
        self.label_12.setFont(font)
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 2, 0, 1, 1)
        self.srcFPS = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(12)
        self.srcFPS.setFont(font)
        self.srcFPS.setText("")
        self.srcFPS.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.srcFPS.setObjectName("srcFPS")
        self.gridLayout_2.addWidget(self.srcFPS, 2, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.openFileButton1.clicked.connect(self.openfile)
        self.alg_Box.activated[str].connect(self.video_process)
        #self.videoGenButton1.clicked.connect(self.video_process)
        self.sendingButton1.clicked.connect(self.streaming)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "VideoWorkshop_V1.0"))
        self.openFileButton1.setText(_translate("MainWindow", "视频载入"))
        self.videoGenButton1.setText(_translate("MainWindow", "生成源"))
        self.sendingButton1.setText(_translate("MainWindow", "发送"))
        self.label_4.setText(_translate("MainWindow", "W:"))
        self.label_5.setText(_translate("MainWindow", "H:"))
        self.label_7.setText(_translate("MainWindow", "ALG:"))
        self.label_9.setText(_translate("MainWindow", "W:"))
        self.label_11.setText(_translate("MainWindow", "H:"))
        self.label_12.setText(_translate("MainWindow", "FPS:"))

    def openfile(self):
        # openfile_name = QFileDialog.getOpenFileName(self, '选择文件', '', 'Excel files(*.xlsx , *.xls)')
        self.sendingButton1.setEnabled(False)
        openfile_name, _ = QFileDialog.getOpenFileName(self, '选择文件', '', "video files(*.avi *.mpg *.mp4 *RMVB *MKV *ASF *WMV);;All Files(*)")
        #print(openfile_name)
        if openfile_name:
            self.video_path = openfile_name
            #print('video_fpath: ', video_path)
        if self.video_path:
            self.getVideoInfo(self.video_path)

    def getVideoInfo(self, video_path):
        self.video_capture = None
        self.video_capture = cv2.VideoCapture(video_path)
        src_video_name = os.path.split(video_path)[1][-13:]
        #video_FourCC = int(video_capture.get(cv2.CAP_PROP_FOURCC))  # 视频编码
        #print("Encoding: {}".format(video_FourCC))
        src_video_width = int(self.video_capture.get(3))
        #print("Width: {}".format(src_video_width))
        src_video_height = int(self.video_capture.get(4))
        #print("Height: {}".format(src_video_height))
        #video_size = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        #              int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        #print("Size: {}".format(video_size))  # (540, 960)
        # 视频总帧数
        self.frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        #print("Frames: {}".format(self.frames))
        # 视频帧率
        self.fps = int(self.video_capture.get(5))
        #print("FPS: {}".format(self.fps))
        self.srcVideoName.setText(src_video_name)
        self.srcWidthVal.setText(str(src_video_width))
        self.srcHeightVal.setText(str(src_video_height))
        self.srcFPS.setText(str(self.fps))
        if self.video_capture:
            #self.videoGenButton1.setEnabled(True)
            self.video_process()

    def video_process(self):
        #videoCapture = cv2.VideoCapture()
        self.sendingButton1.setEnabled(False)
        if self.video_path:
            self.video_capture.open(self.video_path)
            #nframes = self.fps * 6      #for Test
            nframes = self.frames
            #print('Sending Frames: ', nframes)
            #dsize = (int(self.dstWidthVal.text()), int(self.dstHeightVal.text()))
            dsize = (192, 48)   #Hasco
            alg = self.alg_Box.currentText()
            if alg == "LINEAR":
                self.interpolation = cv2.INTER_LINEAR
            elif alg == "NEAREST":
                self.interpolation = cv2.INTER_NEAREST
            elif alg == "AREA":
                self.interpolation = cv2.INTER_AREA
            elif alg == "CUBIC":
                self.interpolation = cv2.INTER_CUBIC
            elif alg == "LANCZOS4":
                self.interpolation = cv2.INTER_LANCZOS4
            #print('dsize: ',dsize)
            dst_fdat = []
            #for i in range(int(self.frames)):
            #self.videoGenButton1.setEnabled(False)
            for i in range(int(nframes)):
                ret, src_frame = self.video_capture.read()
                #print('src_shape: ', src_frame.shape)
                dst_frame = cv2.resize(src_frame, dsize, interpolation=self.interpolation)
                dst_frame = self.padding(dst_frame)
                dst_frame = dst_frame[:,:,[2,1,0]]
                dst_fdat.append(dst_frame)
                #print('dst_shape: ', dst_frame.shape)
            #print('Sending Data: ', dst_fdat[0].shape)
            #self.videoGenButton1.setEnabled(True)
            rgb_pbs = [self.ether_packing(fdat, pkt_len=pkt_len) for fdat in dst_fdat]
            #print('RGB_PBS -- fs: {} - pkts: {} - bpp: {}'.format(len(rgb_pbs), len(rgb_pbs[0]), len(rgb_pbs[0][0])))
            send_pbs = [self.h16_pb + rgb_pb for rgb_pb in rgb_pbs]
            #print('SEND_PBS -- len: {} - pkts: {} - bpp: {}'.format(len(send_pbs), len(send_pbs[0]), len(send_pbs[0][0])))
            send_pkts = []
            for send_pb in send_pbs:
                pkts_1f = []
                for data in send_pb:
                    pkts_1f.append(b''.join([eth_head, data]))
                send_pkts.append(pkts_1f)
            #self.send_pkts = [b''.join([eth_head, data]) for data in send_pbs]
            self.send_pkts = send_pkts
            self.sendingButton1.setEnabled(True)
            print('Sending Info -- $Frames: {} - $Pkts: {} - $PLen: {}'.format(len(send_pkts), len(send_pkts[0]), len(send_pkts[0][0])))
                #break
                #cv2.imwrite("E:/video/pictures/1-1.avi(%d).jpg" % i, frame)

    def padding(self, video_arr, scan_width=256):
        screen_width = 192
        height, width = video_arr.shape[:2]
        if scan_width > screen_width:
            pad = np.zeros([height, scan_width-screen_width, 3])
            #print('padding shape: ',pad.shape)
            video_arr = np.concatenate([video_arr, pad], axis=1)
        #print('Video After Padding: ', video_arr.shape)
        return  video_arr

    def gen_first16_PKT(self, pkt_len=1454, ctrlWords=None):
        pkt16st = []
        for pn in range(16):
            csum = 0
            crc = [0, 0, 0, 0]
            data = [85, 85, 85, 213]
            header = [pn, 0, 0, 0]
            data += header
            if pn == 1:
                ctrl_data = [0] * 32
                if isinstance(ctrlWords, dict):
                    for wn in range(32):
                        if wn in ctrlWords:
                            ctrl_data[wn] = ctrlWords[wn]
                data += ctrl_data
                ctrl_sum = sum(ctrl_data) % 256
                data += [ctrl_sum]
                data += [0] * (pkt_len - 12 - 33)
                csum = sum(header + ctrl_data + [ctrl_sum]) % 65536
            else:
                data += [0] * (pkt_len - 12)
                csum = sum(header) % 65536
            crc = [csum % 256, csum // 256, 0, 0]
            data += crc
            pkt16st.append(bytes(data))
        #print('H16 Length: ', len(pkt16st[0]))
        return pkt16st

    def pix_8bTo10b(self, img_arr):
        img_h, img_w, img_c = img_arr.shape
        z = np.zeros((img_h * img_w * img_c // 4, 5), dtype=np.int16)
        rgb10b_narr = img_arr * 4  # 8b to 10b
        # print('3:',rgb10b_narr[0][0])
        # rgb10b_arr = rgb10b_narr[:,:,-1::-1].reshape((img_h*img_w*img_c//4,4))   #BGR to RGB and flatten ,shape → height * width * 3
        rgb10b_arr = rgb10b_narr.reshape((img_h * img_w * img_c // 4, 4))  # flatten ,shape → height * width * 3
        # print('4:',rgb10b_arr[0])
        for i in range(z.shape[1]):
            if i == 0:
                z[:, i] = rgb10b_arr[:, i]
            elif i <= 3:
                z[:, i] = rgb10b_arr[:, i - 1] * (4 ** (i - 1)) // 256 + rgb10b_arr[:, i] * (4 ** i) % 256
            else:
                z[:, i] = rgb10b_arr[:, i - 1] * (4 ** (i - 1)) // 256
        # print('5:',z[0])
        return z.flatten()

    def frame_packing(self, img_jpg, pkt_len=1454, preamble=4, header=4, csum=4):
        img_np = None
        if isinstance(img_jpg, str):
            pass
        elif isinstance(img_jpg, np.ndarray):
            img_np = img_jpg
        # raw_height, raw_width = img_np.shape[0], img_np.shape[1]

        # rgb_dpath = img_jpg.split('.')[0] + '.dat'
        rgb_blen = pkt_len - preamble - header - csum
        rgb_data = None

        img_np = img_np.astype(np.int16)
        # print(img_np.shape,img_np[0][0])
        rgbs = self.pix_8bTo10b(img_np)
        pns = math.ceil(len(rgbs) / rgb_blen)
        pad_num = pns * rgb_blen - len(rgbs)

        rgb_data = np.concatenate((rgbs, [0] * pad_num))
        # print(pns,pad_num)
        # print(rgb_data.shape)

        # return rgb_data.reshape((-1,rgb_blen)), raw_height, raw_width
        return rgb_data.reshape((-1, rgb_blen))

    def ether_packing(self, img_arr, pkt_len=1454):

        # rgb_hexs = frame_packing(img_arr,row=80,col=256,pkt_len=pkt_len)
        rgb_hexs = self.frame_packing(img_arr, pkt_len=pkt_len)
        rgb_pnum = len(rgb_hexs)
        preamble = np.array(([85, 85, 85, 213] * rgb_pnum)).reshape(-1, 4)
        # print('Preamable: ',preamble)
        header_num = np.arange(16, rgb_pnum + 16).reshape(-1, 1)
        header = np.zeros((rgb_pnum, 4))
        header[:, :2] = np.concatenate((header_num % 256, header_num // 256), axis=1).astype(np.int16)
        # print('Header: ',header)
        csum = np.zeros((rgb_pnum, 4))
        payload = np.concatenate((header, rgb_hexs), axis=1).astype(np.int16)
        # print('Payload: ',payload.shape)
        payload_sum = np.sum(payload, axis=1).reshape(-1, 1)
        csum[:, :2] = np.concatenate((payload_sum % 65536 % 256, payload_sum % 65536 // 256), axis=1).astype(np.int16)
        # print('CSUM: ',csum)
        rgb_pv = np.concatenate((preamble, payload, csum), axis=1).astype(np.int8)
        rgb_pb = [bytes(pv) for pv in rgb_pv]
        # print('RGB_PKT: ',rgb_pkt,rgb_pkt.shape)
        # print('RGB_PKT: ',rgb_pkt[0][:23],rgb_pkt.shape)
        # return data,rgb_pkt
        return rgb_pb

    def luminJust(self, TP_AUTO_EN, brightness, TEST_PAT,
                  GCG, CSTEP_R, CSTEP_G, CSTEP_B, ctrlPac,
                  pkt_len=1454, preamble=4, header=4, crc=4):
        pld_end = pkt_len - crc
        # new_32w = b''.join([ctrlPac[8:18], bytes([brightness]), ctrlPac[19:40]])
        new_32w = b''.join([ctrlPac[8:17],
                            bytes([TP_AUTO_EN]), bytes([brightness]),
                            # ctrlPac[19:36],
                            ctrlPac[19:24], bytes([TEST_PAT]), ctrlPac[25:36],
                            bytes([GCG]), bytes([CSTEP_R]), bytes([CSTEP_G]), bytes([CSTEP_B])])
        ctrlsum = bytes([sum(new_32w) % 256])
        ctrlpload = b''.join([new_32w, ctrlsum, ctrlPac[41:pld_end]])
        csum = bytes([sum(ctrlpload) % 256, sum(ctrlpload) // 256, 0, 0])
        ctrlPac = b''.join([ctrlPac[:8], ctrlpload, csum])
        return ctrlPac

    def streaming(self):
        if self.sendingButton1.text() == '发送':
            self.openFileButton1.setEnabled(False)
            self.dstWidthVal.setEnabled(False)
            self.dstHeightVal.setEnabled(False)
            self.alg_Box.setEnabled(False)
            #self.videoGenButton1.setEnabled(False)
            #self.sendingButton1.setEnabled(False)
            self.sendingButton1.setText('停止')
            print('Streaming Beign~')
            self.flag = False
            sendThread = Thread(target=self.send_video, name='sending')
            sendThread.setDaemon(True)
            sendThread.start()
        else:
            self.flag = True
            self.openFileButton1.setEnabled(True)
            #self.dstWidthVal.setEnabled(True)
            #self.dstHeightVal.setEnabled(True)
            self.alg_Box.setEnabled(True)
            #self.videoGenButton1.setEnabled(True)
            #self.sendingButton1.setEnabled(False)
            self.sendingButton1.setText('发送')

    def send_video(self):
        nframe = 0
        frozen = True
        cost = 0
        while 1:
            if self.flag:
                #self.send_pkts = None
                print()
                print('**Streaming OVER**')
                break
            start_time = time.time()
            self.sendflow(self.send_pkts[nframe])
            #t = time.time() - self.fstart_time
            cost += time.time() - start_time
            if cost < 1/self.fps:
                continue
            #frozen = False
            #self.fstart_time = time.time()
            print('\rFPS: ', 1//cost if cost else self.fps, end='')
            cost = 0
            nframe += 1
            if nframe == self.frames:
                nframe = 0

    def sendflow(self,pkts):
        # sendpfast(pkts, pps=pps,iface=iface)
        # sendp(pkts,iface=iface,socket=socket)
        for pkt in pkts:
            socket.send(pkt)

if __name__ == '__main__':

    #Ctrl
    TEST_EN = 0
    TP_AUTO_EN = 0
    TEST_PAT = 0
    brt = 100
    Rss = 3.9e3
    Vref = 0.8
    GCG_total = [24.17, 30.57, 49.49, 86.61, 103.94, 129.92, 148.48, 173.23]
    GCG = 2
    GC = GCG_total[GCG] * Vref / Rss * 1000
    CSTEP_B = 100  # Blue Color Brightness  - max 3.96mA
    CSTEP_G = 244  # Red Color Brightness	 - max 9.7mA
    CSTEP_R = 244  # Red Color Brightness	 - max 9.7mA
    # CSTEP_B = 45	#Blue Color Brightness - max 1.78mA
    # CSTEP_G = 110	#Green Color Brightness - max 4.36mA;
    # CSTEP_R = 128	#Red Color Brightness - max 5mA;
    ctrl_params = {
                    5:  255,
                    6:  0,
                    7:  143,
                    8:  0,
                    }
    #Network
    dst_mac = 'AA:BB:CC:DD:EE:FF'
    src_mac = '77:88:77:88:77:88'
    dst_ip = '176.16.44.40'
    src_ip = '192.168.226.1'
    pkt_len = 1452
    ip_len = pkt_len + 28
    dst_port = 34501
    src_port = 6400
    udp_len = pkt_len + 8
    eth_head = raw(Ether(src=src_mac,dst=dst_mac)/
                   IP(len=ip_len,dst=dst_ip,src=src_ip)/
                   UDP(sport=src_port,dport=dst_port,len=udp_len))
    netcard_names = list(net_if_addrs().keys())
    #print(netcard_names)
    socket = conf.L2socket(iface='以太网') if '以太网' in netcard_names else None

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())