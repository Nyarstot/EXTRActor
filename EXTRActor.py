'''
This program is based on the original commerical based product created by RNGeusEX.
The program is not related to the original author and can't be used for commercial purposes.
(including extracted content). So use it for research purposes only ;)

author: https://github.com/nyarstot
original product: https://the-end-of-time.itch.io/goodbye-eternity
'''

import os
import sys
import string
import zlib

from struct import pack
from struct import unpack
from random import choice
from itertools import cycle

from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog


_R = '.extra'
_L = 'cipher'
_K = 'compress'
_G = 'rb'
_F = 'utf-8'
_E = b''
_D = False
_B = True
_A = None

old_config_archives = _A
archives            = []
lower_map           = {}
archive_handlers    = []


class YVANeusEX:

    '''
    This class provides tools to make easier the creation of the .urmomgay file format.\n
    Names for this class, and file format courtesy of RNGeusEX
    '''

    indexkey='YVANeusEX_mode'
    cipherkey=b"DES QU'Y A UN SPOT A LA TELE, QUI ME PARLE D'UN CANARD, J'Y VAIS!"

    def __init__(self, filename, filepath, key=_A, cipher=_D, compress=_D, zlib_level=-1):

        '''
        Prepares a new file entry for a YVANeusEX archive file.
        `filename` is the name of the file
        `key` is the cipher key that will be used (cipher is a simple XOR)
        `cipher` is a bool indicating whether to activate ciphering or not
        `compress` is a bool indicating whether to activate compression or not
        `zlib_level` is the compression ratio to use for zlib.compress()
        '''

        self.name=filename
        self.path=filepath
        self.key=key
        self.cipher=cipher
        self.size = 0
        
        with open(filepath, _G) as file:
            self.content=self.encrypt(self.compress(bytearray(file.read()),compress,zlib_level),self.key,self.cipher)
            self.size=len(self.content)

    @staticmethod
    def utf_to_bytes(utf):

        '''
        Converts a UTF-8 string to a bytes-type object for data processing
        '''

        return bytearray(utf, _F)

    @staticmethod
    def bytes_to_utf(bytes):

        '''
        Converts a bytes-type object to a UTF-8 string
        '''

        return bytes.decode(_F)
    
    @staticmethod
    def get_random_key(length=64):

        '''
        Generates and returns a pseudo-random key of specified `length`
        It will be used for ciphering, but since it is stored inside of the archive, no need for true randomness
        '''

        return ''.join((choice(string.ascii_letters+string.digits+string.punctuation)for _ in range(length)))
    
    @classmethod
    def checksum(cls, content):

        '''
        Returns the adler32 checksum for `content`
        '''

        return zlib.adler32(bytes(content))&4294967295
    
    @classmethod
    def compress(cls, content, compress=_D, level=-1):

        '''
        Compresses the `content` with the zlib `level` indicated if the `compress` bool says to do so
        '''

        if sys.version_info.major < 3 and compress:
            return bytearray(zlib.compress(bytes(content),level))
        if compress:
            return zlib.compress(content,level)

        return content
    
    @classmethod
    def decompress(cls, content, compress=_D):

        '''
        Decompresses the `content` if the `compress` bool says to do so
        '''

        if sys.version_info.major < 3 and compress:
            return bytearray(zlib.decompress(bytes(content)))
        if compress:
            return zlib.decompress(content)

        return content
    
    @classmethod
    def encrypt(cls,content,key,cipher=_D,cipherkeylength=5):

        '''
        Ciphers the `content` using a xor with itself and the `key` if the `cipher` bool says to do so
        This was a b*tch to make :)
        '''

        if cipher:
            k=cycle(key);keylen=len(key);content=bytearray(content)
            if len(content) >= (2 * keylen * cipherkeylength):
                ciphercontent = content[:keylen*cipherkeylength],content[-keylen*cipherkeylength:]
                content = content[keylen*cipherkeylength:-keylen*cipherkeylength]
            else:
                ciphercontent = content,_E
                content = _E
            return bytearray((b^next(k)for b in ciphercontent[0]))+bytearray(content)+bytearray((b^next(k)for b in ciphercontent[1]))
        
        return content
    
    def get_index(self):
        
        '''
        Returns the index line ready for being put into the archive, to allow for fast lookup of data
        '''

        index=self.utf_to_bytes('{name}\x00{size:x}\x00{checksum:x}'.format(name=self.name, size=self.size, checksum=self.checksum(self.content)))
        return pack('>H',len(index))+self.encrypt(index,self.key,self.cipher)

class EXTRActor(QWidget):

    def __init__(self, parent=None) -> None:
        super(QWidget, self).__init__(parent=parent)
        majorVersion = 0
        minorVersion = 7
        patchVersion = 9

        self.setWindowTitle(f"YVANeusEX archive extractor [{majorVersion}.{minorVersion}.{patchVersion}]")
        self.setFixedSize(500, 120)

        self.__init_ui()

    def __init_ui(self) -> None:

        base_layout = QVBoxLayout()
        open_ctrls_layout = QHBoxLayout()
        extract_ctrls_layout = QHBoxLayout()

        open_label = QLabel("Open file: ")
        self.open_line = QLineEdit()
        open_dialog_button = QPushButton("Browse archive")

        open_ctrls_layout.addWidget(open_label)
        open_ctrls_layout.addWidget(self.open_line)
        open_ctrls_layout.addWidget(open_dialog_button)

        extract_label = QLabel("Extract to: ")
        self.extract_line = QLineEdit()
        extract_dialog_button = QPushButton("Browse directory")

        extract_ctrls_layout.addWidget(extract_label)
        extract_ctrls_layout.addWidget(self.extract_line)
        extract_ctrls_layout.addWidget(extract_dialog_button)

        self.extract_button = QPushButton("Extract...")

        base_layout.addLayout(open_ctrls_layout)
        base_layout.addLayout(extract_ctrls_layout)
        base_layout.addWidget(self.extract_button)
        self.setLayout(base_layout)

        open_dialog_button.clicked.connect(self.__open_filedialog)
        extract_dialog_button.clicked.connect(self.__open_extractdialog)
        self.extract_button.clicked.connect(self.__extract_button_signal)

    def __open_filedialog(self):
        fdialog = QFileDialog.getOpenFileName(self, "Open archive", "./")
        self.open_line.setText(fdialog[0])

    def __open_extractdialog(self):
        fdialog = QFileDialog.getExistingDirectory(self, "Open archive", "./")
        self.extract_line.setText(fdialog)

    def __extract_button_signal(self):
        self.__extract_archive(self.open_line.text(), self.extract_line.text())
        self.extract_button.setText("DONE!")

    def __extract_archive(self, inputFile, extractDir) -> bool:

        archive = open(inputFile, "rb")
        
        if not os.path.exists(extractDir):
            os.makedirs(extractDir)

        metaline    = archive.readline()
        mode        = metaline[6:7]
        compress    = bool(ord(mode)&1)
        cipher      = bool(ord(mode)&2)
        checksum    = bool(ord(mode)&4)
        key         = YVANeusEX.bytes_to_utf(metaline[7:-1])
        index       = {}
        filelist    = []

        index_length    = None
        data_offset     = None

        try:
            while _B:
                index_length = unpack('>H', archive.read(2))[0]

                if index_length == 0:
                    data_offset = archive.tell()
                    break

                current_line = YVANeusEX.bytes_to_utf(YVANeusEX.encrypt(bytearray(archive.read(index_length)),key,cipher))
                filename, size, crc = current_line.split('\x00');size,crc=map(lambda x:int(x,16),(size,crc))
                index[filename] = size,crc
                filelist.append(filename)

        except ValueError:
            raise ValueError("Archive is corrupted")
        
        for file in filelist:
            current_offset = data_offset
            file_size = index[file][0]

            if checksum:
                archive.seek(current_offset)
                if index[file][1] != YVANeusEX.checksum(archive.read(file_size)):
                    raise ValueError('Content is corrupted')
            
            data_offset += file_size
            index[file] = [(current_offset, file_size, _E)]

            if not os.path.exists(os.path.dirname(os.path.join(extractDir,file))):
                os.makedirs(os.path.dirname(os.path.join(extractDir,file)))

            decodeFile = open(os.path.join(extractDir, file), "wb")
            archive.seek(current_offset)
            data = YVANeusEX.decompress(YVANeusEX.encrypt(bytearray(archive.read(file_size)), key, cipher), compress)
            decodeFile.write(data)
            decodeFile.close()

        index[YVANeusEX.indexkey] = {'key':key,_K:compress,_L:cipher,'checksum':checksum}
        return index


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = EXTRActor()
    gui.show()
    app.exec_()