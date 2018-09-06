#!/usr/bin/env python
import datetime
import os
import sys 
import subprocess
import hashlib
import logging
import shutil
sys.path.append('/home/deect')
from logging.handlers import RotatingFileHandler
from backbone import Backbone

MAX_SIZE = 5* 1024 * 1024
LOG_PATH = "/home/deect/usbbackup/backup.log"

logger = logging.getLogger("backupshutdown")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler=RotatingFileHandler(LOG_PATH, maxBytes=MAX_SIZE, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)

class dbBackup:
    def __init__(self):
        self.pubKey = '/home/deect/tmpsec/usbdbexport_public_key.pem'
        self.dbPath=  '/home/deect/data'
        self.backUPPath =  '/home/deect/usbbackup/'
        self.ramLocation = '/home/deect/tmpsec/'
        self.backbone=Backbone()
        self.result = self.backbone.getHwId()
        self.machineID = self.result[3]
        self.keyOK = False
	self.backupExists = False
        self.dbFile = False
    def readKey(self):
        # Try to open cert file
        if not os.path.isfile(self.pubKey):
            logger.debug("Error Loading Public Key")
            return
        else:
            self.keyOK = True

    '''def filemd5(self,filename, block_size=2 ** 20):
        f = open(filename)
        md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
        f.close()
        return md5.digest()'''

    def encryptAndCopy(self):#Check and Find DB file Location
        for file in os.listdir(self.dbPath):
            if file.endswith(".db"):
                dbFile = os.path.join(self.dbPath, file)
                self.dbFile = True
            else:
                logger.error("No Database File found")
                return
        for File in os.listdir(self.backUPPath):
            if File.endswith(".db"):
               self.backupFile = os.path.join(self.backUPPath,File)
               self.backupExists = True
            else:
		pass
                #logging.info("NO previous backup found in USB")
                #logging.debug("NO Existing Backup File")
        self.encryptedFile = self.ramLocation + 'DBencypt_' +str(self.machineID) +"-"+ datetime.date.today().strftime("%B-%d-%Y") + '.db'
        encryptCommand = 'openssl smime -encrypt -binary -aes-256-cbc -outform DER -in ' \
                         + dbFile \
                         + ' -out ' \
                         + self.encryptedFile \
                         + " " \
                         +self.pubKey
        os.system(encryptCommand)
        if self.backupExists is True:
            os.remove(self.backupFile)
	    logger.info("Replaced with new Database")
        shutil.copy(self.encryptedFile,self.backUPPath)

        '''if self.backup is False:
            #print("New backup Created")
            #Make a new back-up copy
            shutil.copy2(self.encryptedFile,self.backUPPath)
        else: #Find checksum for two files and copy on diff
            md5temp = self.filemd5(self.encryptedFile)
            md5back = self.filemd5(self.backupFile)
            if md5back != md5temp:
                os.remove(self.backupFile)
                shutil.copy(self.encryptedFile,self.backUPPath)
            else:
                pass'''

if __name__ == "__main__":
    BackUP = dbBackup()
    BackUP.readKey()
    if BackUP.keyOK is True:
        BackUP.encryptAndCopy()
