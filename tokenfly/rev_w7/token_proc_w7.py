import struct
#import hashlib
import sys

from PyQt5.QtGui import QPalette, QColor, QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QLineEdit, QPushButton, QVBoxLayout, QWidget, \
    QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QRect
import serial
import serial.tools.list_ports

TOKEN_SIGNATURE_BITS = 19
TOKEN_COUNTER_RESYNC = 16
TOKEN_COMMAND_BITS = 3
TOKEN_EXT_COMMAND_BITS = 3
TOKEN_KEY_LENGTH = 20
TOKEN_COUNTER_LONG_RESYNC = 200
TOKEN_NUM_COUNTER_WINDOW_WORDS = (TOKEN_COUNTER_RESYNC + 15) // 16 + 1

TOKEN_SIGNATURE_MASK = (1 << TOKEN_SIGNATURE_BITS) - 1
TOKEN_COMMAND_POS = TOKEN_SIGNATURE_BITS
TOKEN_COMMAND_MASK = ((1 << TOKEN_COMMAND_BITS) - 1) << TOKEN_COMMAND_POS
TOKEN_PAYLOAD_POS = TOKEN_COMMAND_POS + TOKEN_COMMAND_BITS
TOKEN_PAYLOAD_MASK = ((1 << 32) - 1) << TOKEN_PAYLOAD_POS
TOKEN_EXT_COMMAND_POS = TOKEN_COMMAND_POS + TOKEN_COMMAND_BITS
TOKEN_EXT_COMMAND_MASK = ((1 << TOKEN_EXT_COMMAND_BITS) - 1) << TOKEN_EXT_COMMAND_POS
TOKEN_EXT_PAYLOAD_POS = TOKEN_EXT_COMMAND_POS + TOKEN_EXT_COMMAND_BITS
TOKEN_EXT_PAYLOAD_MASK = ((1 << 32) - 1) << TOKEN_EXT_PAYLOAD_POS

SHA1_SZ = 20

class TokenFlyUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.baud_rate = None
        self.port = None
        self.cmd_table = ['unlock absolute', 'unlock relative', 'demo mode', 'unlock forever', 'calibrate', 'set counter', 'UNKNOWN']
        self.cmd_int = [0, 1, 2, 7, 8, 9, 3]
        self.CMD = 0  # 设置初始值为0
        self.Counter = 0  # 设置初始值为0
        self.Payload = 24  # 设置初始值为24
        self.token = None
        self.msg = None
        #self.token_label = QLabel("", self)
        #self.update_token_label()  # 生成初始的token值并显示
        self.initUI()

    def initUI(self):
        self.setWindowTitle("TokenFly")
        #self.setFixedSize(1000, 500)
        self.setWindowIcon(QIcon('anchor.ico'))

        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)

        font = QFont("Times New Roman", 12)
        stylesheet = "color: red; font-weight: bold;"

        # 区域1水平布局
        region1_layout = QHBoxLayout()
        region1_layout.setSpacing(0)
        
        baud_label = QLabel("Baud", self)
        #baud_label.setAlignment(Qt.AlignCenter)
        #baud_label.resize(200, 30)
        #baud_label.move(25, 20)
        #baud_label.setFont(font)
        #baud_label.setStyleSheet("color: blue; font-size: 30px; font-weight: bold;")
        baud_label.setStyleSheet(stylesheet)
        region1_layout.addWidget(baud_label)

        self.baud_combo = QComboBox(self)
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        #self.baud_combo.resize(150, 30)
        #self.baud_combo.move(50, 50)
        self.baud_combo.currentIndexChanged.connect(self.set_baud_rate)
        region1_layout.addWidget(self.baud_combo)

        com_label = QLabel("COM", self)
        com_label.setStyleSheet(stylesheet)
        #com_label.setAlignment(Qt.AlignCenter)
        #com_label.resize(200, 30)
        #com_label.move(475, 20)
        region1_layout.addWidget(com_label)

        self.com_combo = QComboBox(self)
        #self.com_combo.resize(150, 30)
        #self.com_combo.move(500, 50)
        self.com_combo.currentIndexChanged.connect(self.set_port)
        region1_layout.addWidget(self.com_combo)
        
        region1_layout.addStretch(0)

        main_layout.addLayout(region1_layout)

        # 区域2水平布局
        region2_layout = QHBoxLayout()
        cmd_label = QLabel("CMD", self)
        cmd_label.setStyleSheet(stylesheet)
        cmd_label.setAlignment(Qt.AlignCenter)
        #cmd_label.resize(200, 30)
        #cmd_label.move(25, 150)
        region2_layout.addWidget(cmd_label)

        self.cmd_combo = QComboBox(self)
        self.cmd_combo.addItems(self.cmd_table)
        #self.cmd_combo.resize(150, 30)
        #self.cmd_combo.move(50, 180)
        self.cmd_combo.setCurrentIndex(self.CMD)  # 设置初始值
        self.cmd_combo.currentIndexChanged.connect(self.set_cmd)
        region2_layout.addWidget(self.cmd_combo)

        counter_label = QLabel("Counter", self)
        counter_label.setStyleSheet(stylesheet)
        #counter_label.resize(200, 30)
        #counter_label.move(300, 150)
        region2_layout.addWidget(counter_label)

        self.counter_edit = QLineEdit(self)
        #self.counter_edit.resize(150, 30)
        #self.counter_edit.move(300, 180)
        self.counter_edit.setText(str(self.Counter))  # 设置初始值
        self.counter_edit.textChanged.connect(self.set_counter)
        region2_layout.addWidget(self.counter_edit)

        payload_label = QLabel("Payload", self)
        payload_label.setStyleSheet(stylesheet)
        #self.payload_label.resize(200, 30)
        #self.payload_label.move(550, 150)
        region2_layout.addWidget(payload_label)

        self.payload_edit = QLineEdit(self)
        #self.payload_edit.resize(150, 30)
        #self.payload_edit.move(550, 180)
        self.payload_edit.setText(str(self.Payload))  # 设置初始值
        self.payload_edit.textChanged.connect(self.set_payload)
        region2_layout.addWidget(self.payload_edit)

        self.get_btn = QPushButton("Get", self)
        #self.get_btn.resize(50, 40)
        #self.get_btn.move(720, 180)
        self.get_btn.clicked.connect(self.update_token_label)
        region2_layout.addWidget(self.get_btn)

        self.parse_btn = QPushButton("Valid", self)
        #self.parse_btn.resize(50, 40)
        #self.parse_btn.move(50, 400)
        self.parse_btn.clicked.connect(self.get_message_from_token)
        #region2_layout.addWidget(self.parse_btn)

        main_layout.addLayout(region2_layout)

        # 区域3水平布局
        region3_layout = QHBoxLayout()
        token_label = QLabel("Token", self)
        token_label.setStyleSheet(stylesheet)
        #token_label.resize(200, 30)
        #token_label.move(50, 300)
        region3_layout.addWidget(token_label)
        #region3_layout.addWidget(self.get_btn)

        #self.token_label = QLabel("", self)
        #rainbow_palette = QPalette()
        #rainbow_palette.setColor(QPalette.WindowText, QColor(Qt.darkGreen))
        #self.token_label.setPalette(rainbow_palette)
        ##self.token_label.resize(550, 50)
        ##self.token_label.move(50, 330)
        ##self.token_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        ##self.token_label.setStyleSheet("QLabel { border: 1px solid green; padding: 5px; font-weight: bold; }")
        #region3_layout.addWidget(self.token_label)

        self.token_edit = QLineEdit(self)
        #rainbow_palette = QPalette()
        #rainbow_palette.setColor(QPalette.WindowText, QColor(Qt.darkGreen))
        #self.token_edit.setPalette(rainbow_palette)
        self.token_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略为Expanding
        self.token_edit.textChanged.connect(self.token_lable_just)
        self.token_edit.setStyleSheet("color: red;font-weight: bold;")
        #self.token_edit.resize(150, 30)
        #self.token_edit.move(550, 180)
        self.token_edit.setEnabled(False)  # 设置初始值
        #self.token_edit.textChanged.connect(self.set_payload)
        region3_layout.addWidget(self.token_edit)
        region3_layout.addWidget(self.parse_btn)
        self.send_btn = QPushButton("Send", self)
        #self.send_btn.resize(100, 100)
        #self.send_btn.move(600, 330)
        self.send_btn.clicked.connect(self.send_token)
        self.send_btn.setEnabled(False)
        region3_layout.addWidget(self.send_btn)

        region1_layout.addStretch(1)

        main_layout.addLayout(region3_layout)

        self.setCentralWidget(main_widget)
        
        self.adjustSize()
        
        self.setFixedSize(self.size())

        self.update_ports()
        self.update_token_label()

    def set_baud_rate(self, index):
        self.baud_rate = int(self.baud_combo.currentText())

    def update_ports(self):
        self.com_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if ports:
            self.com_combo.addItems(ports)
            self.send_btn.setEnabled(True)

    def set_port(self, index):
        self.port = self.com_combo.currentText()

    def set_cmd(self, index):
        self.CMD = self.cmd_int[index]

    def set_counter(self, text):
        try:
            self.Counter = int(text)
        except ValueError:
            pass

    def set_payload(self, text):
        try:
            self.Payload = int(text)
        except ValueError:
            pass

    def token_lable_just(self, text):
        #font_metrics = self.token_label.fontMetrics()
        font_metrics = self.token_edit.fontMetrics()
        width = font_metrics.width(text)
        height = font_metrics.height()
        #self.token_label.setFixedSize(width + 40, height + 30)
        self.token_edit.setFixedSize(width+10, height)

    def update_token_label(self):
        self.token_edit.setEnabled(False)
        self.cmd_combo.setEnabled(True)
        self.counter_edit.setEnabled(True)
        self.payload_edit.setEnabled(True)
        if self.cmd_combo.currentIndex() == len(self.cmd_table) - 1:
            self.cmd_combo.setCurrentIndex(0)
            self.payload_edit.setText(str(24))
        self.token = token_generation(self.CMD, self.Counter, self.Payload)
        #self.token_lable_just()
        #self.token_label.setText(str(self.token))
        self.token_edit.setText(str(self.token))

    def get_message_from_token(self):
        self.token_edit.setEnabled(True)
        self.token_edit.adjustSize()
        self.cmd_combo.setEnabled(False)
        self.counter_edit.setEnabled(False)
        self.payload_edit.setEnabled(False)
        self.msg = token_parse(int(self.token_edit.text()))
        if self.msg:
            self.cmd_combo.setCurrentIndex(len(self.cmd_table)-1 if self.msg.cmd not in self.cmd_int
                                      else self.cmd_int.index(self.msg.cmd))
            self.counter_edit.setText(str(self.msg.counter))
            self.payload_edit.setText(str(self.msg.payload.u32))
        else:
            self.cmd_combo.setCurrentIndex(len(self.cmd_table)-1)
            self.counter_edit.setText("0")
            self.payload_edit.setText("0")

        #for test
        if not self.msg:
            print(f"token {self.token_edit.text()} is invalid!")
        else:
            print(f'cmd {self.msg.cmd}, '
                  f'{"UNKNOWN" if self.msg.cmd not in self.cmd_int else self.cmd_table[self.cmd_int.index(self.msg.cmd)]}, '
                  f'payload {self.msg.payload.u32}')

    def send_token(self):
        self.baud_rate = int(self.baud_combo.currentText())
        self.port = self.com_combo.currentText()
        send_str = self.token_edit.text()
        if self.serial_port is None:
            try:
                self.serial_port = serial.Serial(self.port, self.baud_rate, timeout=1)
                self.send_btn.setText("End")
            except serial.SerialException as e:
                print(e)
                return

        #token = token_generation(self.CMD, self.Counter, self.Payload)
        #self.serial_port.write(self.token.encode())
        self.serial_port.write(send_str.encode('utf-8'))

        print(f'{self.port} - {self.baud_rate}  →→→  {send_str} - {send_str.encode("utf-8")}')

        if self.send_btn.text() == "End":
            self.serial_port.close()
            self.serial_port = None
            self.send_btn.setText("Send")

    def closeEvent(self, event):
        if self.serial_port is not None:
            self.serial_port.close()
        event.accept()

class TokenCmd:
    token_cmd_unlock_absolute = 0
    token_cmd_unlock_relative = 1
    token_cmd_demo_mode = 2
    token_cmd_ext = 7
    token_cmd_unlock_forever = 7
    token_cmd_calibrate = 8
    token_cmd_set_counter = 9
    token_cmd_misc = 10
    token_cmd_max = 11

class TokenPayload:
    def __init__(self, value):
        self.absolute_unlock = value
        self.relative_unlock = value
        self.counter = value
        self.calibration = value
        self.misc = value
        self.u32 = value

class TokenMsg:
    def __init__(self):
        self.cmd = 0
        self.payload = TokenPayload(0)
        self.counter = 0

class Token:
    def __init__(self):
        self.cmd = 0
        self.payload = TokenPayload(0)
        self.signature = 0

class TokenState:
    def __init__(self):
        self.secret_key = bytearray(TOKEN_KEY_LENGTH)
        self.token_counter = 0
        self.token_counter_window = bytearray(TOKEN_NUM_COUNTER_WINDOW_WORDS * 2)

def token_key_init(state, key, key_length, counter):
    if not state or not key:
        return "token_error_invalid_argument"
    if key_length != TOKEN_KEY_LENGTH:
        return "token_error_key_invalid"

    state.secret_key = bytearray(key)
    state.token_counter_window = bytearray(TOKEN_NUM_COUNTER_WINDOW_WORDS * 2)

    state = token_set_counter(state, counter)

    return state

def token_set_counter(state, counter):
    word_idx = counter // 16 % TOKEN_NUM_COUNTER_WINDOW_WORDS
    bit_idx = counter & 15

    state.token_counter_window = bytearray(TOKEN_NUM_COUNTER_WINDOW_WORDS * 2)
    state.token_counter_window[word_idx * 2] = 0xFF
    state.token_counter_window[word_idx * 2 + 1] = 0xFF
    state.token_counter_window[word_idx * 2] &= ~((1 << bit_idx) - 1)
    state.token_counter = counter
    
    return state
    

def token_sign(state, token):
    if not state or not token:
        return "token_error_invalid_argument"

    token.signature = token_compute_signature(state.secret_key, token.cmd, token.payload.relative_unlock, state.token_counter)

    return token

def token_compute_signature(key, cmd, payload, counter):
    #tohash = struct.pack('<III', cmd, payload, counter)
    tohash = struct.pack('<III', cmd, payload & 0xffffffff, counter & 0xffffffff)
    return token_hotp_calc(key, tohash)

def token_hotp_calc(key, buffer):
    h = hmac_sha1_init(key, TOKEN_KEY_LENGTH)
    hash_val = hmac_sha1_done(hmac_sha1_process(h, buffer))

    offset = hash_val[SHA1_SZ - 1] & 0x0f

    code = ((hash_val[offset] & 0x7f) << 24) | \
           ((hash_val[offset + 1] & 0xff) << 16) | \
           ((hash_val[offset + 2] & 0xff) << 8) | \
           (hash_val[offset + 3] & 0xff)

    return code % (1 << TOKEN_SIGNATURE_BITS)

def token_generation(cmd, counter, payload):
    key = bytearray([
        0x25, 0xf2, 0xba, 0x3f, 0xe8, 0x31, 0xe1, 0xef, 0xef, 0x22,
        0x7e, 0xf5, 0x19, 0xae, 0x34, 0xd3, 0x79, 0xaf, 0xe7, 0xcb,
    ])
    state = TokenState()
    state = token_key_init(state, key, TOKEN_KEY_LENGTH, counter)
    my_token = Token()
    my_token.cmd = cmd
    my_token.payload = TokenPayload(payload)
    if cmd == TokenCmd.token_cmd_unlock_forever:
        my_token.payload = TokenPayload(0)
    my_token = token_sign(state, my_token)
    encoded_token = token_packed_encode(my_token)
    return encoded_token

IPAD = 0x36
OPAD = 0x5c
PAD_SZ = 64
SHA1_SZ = 20  # 160 bits

def hmac_sha1_init(key, key_length):
    hm = {
        "state": sha1_init(),
        "sec": bytearray(64)
    }
    hm["state"]["buf"] = bytearray(64)
    
    if key_length > PAD_SZ:
        hm["state"] = sha1_process(hm["state"], key)
        hm["sec"] = sha1_done(hm["state"])

    else:
        hm["sec"][:key_length] = key

    pad = bytearray(PAD_SZ)
    for i in range(PAD_SZ):
        pad[i] = hm["sec"][i] ^ 0x36

    hm["state"] = sha1_process(hm["state"], pad)

    return hm

def hmac_sha1_process(hm, buffer):
    hm["state"] = sha1_process(hm["state"], buffer)
    return hm

def hmac_sha1_done(hm):
    pad = bytearray(PAD_SZ)
    mac = sha1_done(hm["state"])

    for i in range(PAD_SZ):
        pad[i] = hm["sec"][i] ^ 0x5c
    
    buf = hm["state"]["buf"]
    hm["state"] = sha1_init()
    hm["state"]["buf"] = buf
    hm["state"] = sha1_process(hm["state"], pad)
    hm["state"] = sha1_process(hm["state"], mac)

    return sha1_done(hm["state"])
    
# Define the SHA-1 finalization function
def sha1_done(state):
    # Increase the length of the message
    state['length'] += state['curlen'] * 8

    # Append the '1' bit
    state['buf'][state['curlen']] = 0x80
    state['curlen'] += 1

    # If the length is currently above 56 bytes, append zeros and compress
    if state['curlen'] > 56:
        for i in range(state['curlen'], 64):
            state['buf'][i] = 0
        sha1_compress(state)
        state['curlen'] = 0

    # Pad up to 56 bytes of zeros
    for i in range(state['curlen'], 56):
        state['curlen'] += 1
        state['buf'][i] = 0

    # Mark the top bits zero
    for i in range(56, 60):
        state['buf'][i] = 0

    # Append length
    for i in range(60, 64):
        state['buf'][i] = (state['length'] >> ((63 - i) * 8)) & 255

    state = sha1_compress(state)

    # Copy output
    res = [(state['state'][i >> 2] >> (((3 - i) & 3) << 3)) & 255 for i in range(20)]
    return res

def sha1_compress(state):
    a, b, c, d, e = state["state"]

    W = [0] * 80
    for i in range(16):
        W[i] = struct.unpack(">I", state["buf"][i*4:i*4+4])[0]

    for i in range(16, 80):
        #W[i] = (W[i-3] ^ W[i-8] ^ W[i-14] ^ W[i-16]) << 1
        j = W[i-3] ^ W[i-8] ^ W[i-14] ^ W[i-16]
        W[i] = (j << 1) | (j >> 31)
        W[i] &= 0xFFFFFFFF

    for i in range(80):
        if i < 20:
            f = (b & c) | ((~b) & d)
            k = 0x5A827999
        elif i < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif i < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6

        temp = ((a << 5) | (a >> 27)) + f + e + k + W[i]
        temp &= 0xFFFFFFFF
        e = d
        d = c
        c = ((b << 30) | (b >> 2)) & 0xFFFFFFFF
        #c = ((b << 30) | (b >> 2))
        b = a
        a = temp

    state["state"] = [(x+y) & 0xFFFFFFFF for x, y in zip(state["state"], [a, b, c, d, e])]
    return state
    
def sha1_init():
    return {"state": [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0],
            "curlen": 0,
            "length": 0
            #,"buf": bytearray(64)
            }

def sha1_process(state, buf):
    for byte in buf:
        state['buf'][state['curlen']] = byte
        state['curlen'] += 1

        if state['curlen'] == 64:
            #state = sha1_compress(state, buf)
            state = sha1_compress(state)
            state['length'] += 512
            state['curlen'] = 0
    return state
    
def token_packed_encode(token):
    if not token:
        return "token_error_invalid_argument"

    if token.signature >= (1 << TOKEN_SIGNATURE_BITS):
        return "token_error_invalid_argument"

    if token.cmd >= TokenCmd.token_cmd_max:
        return "token_error_invalid_command"

    packed = token.signature
    if token.cmd < TokenCmd.token_cmd_ext:
        packed |= token.cmd << TOKEN_COMMAND_POS
        packed |= token.payload.u32 << TOKEN_PAYLOAD_POS
    else:
        packed |= TokenCmd.token_cmd_ext << TOKEN_COMMAND_POS
        packed |= (token.cmd - TokenCmd.token_cmd_ext) << TOKEN_EXT_COMMAND_POS
        packed |= token.payload.u32 << TOKEN_EXT_PAYLOAD_POS

    return packed

def token_parse(token_val):
    key = bytearray([
        0x25, 0xf2, 0xba, 0x3f, 0xe8, 0x31, 0xe1, 0xef, 0xef, 0x22,
        0x7e, 0xf5, 0x19, 0xae, 0x34, 0xd3, 0x79, 0xaf, 0xe7, 0xcb,
    ])
    # 解析token_value并创建token对象
    #token = Token()
    #token.payload = TokenPayload(0)
    token = token_packed_decode(token_val, Token())
    if not token:
        #print(f"token {token_val} is invalid!")
        return None
    ## 创建state和msg对象
    state = token_key_init(TokenState(), key, TOKEN_KEY_LENGTH, 0)
    #msg = TokenMsg()

    # 调用token_validate_and_update函数来提取msg
    msg = token_validate_and_update(state, token, TokenMsg())
    #if not msg:
    #    print(f"token {token_val} is invalid!")
    #    return None

    return msg

def token_packed_decode(packed, token):
    if not token or not packed:
        return 

    if packed >= (1 << (TOKEN_EXT_PAYLOAD_POS + 32)):
        return 

    token.signature = packed & TOKEN_SIGNATURE_MASK
    token.cmd = (packed & TOKEN_COMMAND_MASK) >> TOKEN_COMMAND_POS
    if token.cmd == TokenCmd.token_cmd_ext:
        token.cmd += (packed & TOKEN_EXT_COMMAND_MASK) >> TOKEN_EXT_COMMAND_POS
        token.payload.u32 = (packed & TOKEN_EXT_PAYLOAD_MASK) >> TOKEN_EXT_PAYLOAD_POS
    else:
        token.payload.u32 = (packed & TOKEN_PAYLOAD_MASK) >> TOKEN_PAYLOAD_POS

    return token

def token_validate_and_update(state, token, msg):
    if not state or not token or not msg:
        #return TokenError.INVALID_ARGUMENT
        return

    msg, state = token_validate(state, token, msg)
    return msg
    #if ret == TokenError.OK:
    #    return token_state_update(state, msg)
    #else:
    #    return ret

def token_counter_unused(state, counter):
    if counter // 16 > state.token_counter // 16:
        return 1

    word_idx = counter // 16 % len(state.token_counter_window)
    bit_idx = counter & 15

    #return not (state.token_counter_window[word_idx] & (1 << bit_idx))
    return (state.token_counter_window[word_idx] & (1 << bit_idx))

def token_validate(state, token, msg):
    min_counter, max_counter = 0, 0

    if token.cmd == TokenCmd.token_cmd_unlock_relative:
        min_counter = state.token_counter - min(state.token_counter, TOKEN_COUNTER_RESYNC)
        max_counter = state.token_counter + TOKEN_COUNTER_RESYNC
    else:
        min_counter = state.token_counter
        max_counter = state.token_counter + TOKEN_COUNTER_LONG_RESYNC

    for check_counter in range(min_counter, max_counter):
        if token_compute_signature(state.secret_key, token.cmd, token.payload.u32, check_counter) != token.signature:
            continue

        msg.cmd = token.cmd
        msg.payload.u32 = token.payload.u32
        msg.counter = check_counter

        if token_counter_unused(state, check_counter):
            state = token_state_update(state, msg)

        return msg, state

    return None, state

def token_record_counter(state, counter):
    word_idx = counter // 16 % len(state.token_counter_window)
    bit_idx = counter & 15

    if counter >= state.token_counter:
        old_beg = (state.token_counter - TOKEN_COUNTER_RESYNC) // 16 % len(state.token_counter_window)
        new_beg = (counter + 1 - TOKEN_COUNTER_RESYNC) // 16 % len(state.token_counter_window)

        for old_idx in range(old_beg, new_beg):
            state.token_counter_window[old_idx] = 0xFFFF

        state.token_counter = counter + 1

    state.token_counter_window[word_idx] &= ~(1 << bit_idx)
    
    return state

def token_state_update(state, msg):
    if msg.cmd == TokenCmd.token_cmd_set_counter:
        state = token_set_counter(state, msg.payload.counter)
    elif msg.cmd == TokenCmd.token_cmd_unlock_relative:
        state = token_record_counter(state, msg.counter)
    else:
        state = token_set_counter(state, msg.counter + 1)

    return state

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = TokenFlyUI()
    ui.show()
    sys.exit(app.exec_())
