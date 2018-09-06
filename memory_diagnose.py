#  -*- coding: utf-8 -*-
#  import libraries
import json
import logging
import os
import sys
from datetime import datetime
from smbus import SMBus
sys.path.append('/home/deect')
sys.path.append('/home/deect/backbone_pack')
sys.path.append('/home/deect/validate')
from validate import memory
from backbone_pack import atmega_serial

try:
    smb = SMBus(1)
except:
    #logger = logging.getLogger()
    print("--> SMBus failed to start")

BLOCKSIZE = 16

CERTIFICATE_LOCATION = 2 * 128  # Page number
DBCERTIFICATE_LOCATION = 75 * 128
INDEX_LOCATION = 1 * 128


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def read_version():
    aString = memory.read_version()
    aJson = json.loads(aString)
    logger.info("Version info = \n" + json.dumps(aJson, indent=3))
    return

def read_template():
    bString = memory.read_template()
    bJson = json.loads(bString)
    logger.info("Matching template: \n" + json.dumps(bJson, indent=3))
    return

def read_electrode():
    x = 0
    serialnum, tagtype, datenum = memory.read_electrode(x)
    while serialnum!=0:
        logger.info(u'Electrode[{:d}]\tserial={:#02x}\ttype={}\tdate={:d}'.format(x, serialnum, tagtype, datenum))
        x += 1
        serialnum, tagtype, datenum = memory.read_electrode(x)
    return

def read_handle():
    x = 0
    serialnum, counter = memory.read_handle(x)
    while serialnum!=0:
        logger.info(u'Handle[{:d}]\tserial:\t{:#02x}\tcounter: {:d}'.format(x, serialnum, counter))
        x += 1
        serialnum, counter = memory.read_handle(x)

    return

def read_sys_serial():
    logger.info(u'System serial no: {:d}'.format(memory.read_system_serial()))
    return

def write_version():
    data = {}
    aString = raw_input("Version string: ")
    if not aString:
        exit()
    else:
        data["version"] = aString
    aString = raw_input("Date string YYYY-MM-DD: ")
    if not aString:
        exit()
    else:
        try:
            datetime.strptime(aString, "%Y-%m-%d")
            data["date"] = aString
        except ValueError:
            logger.info("Incorrect date")
            exit()

    writedown_Version_and_date(data, logger)
    return

def write_template():
    template = {}
    aString = raw_input("System serial no: ")
    systemSerialNumber = 999
    if aString.isdigit() and 4294967295 > int(aString) > 0:
        systemSerialNumber = int(aString)
    else:
        logger.error("Incorrect serial number, exiting")
        exit()

    template['sys'] = systemSerialNumber

    aString = raw_input("Country code [2]: ")
    if aString.islower() and len(aString) == 2:
        Cspec = aString
    else:
        Cspec = ""
    template['C'] = Cspec.upper()

    aString = raw_input("Region code [4]: ")
    if len(aString.decode("utf_8")) < 5:
        STspec = aString
    else:
        STspec = ""
    template['ST'] = STspec

    aString = raw_input("Organization code [10]: ")
    if aString and len(aString.decode("utf_8")) < 11:
        Ospec = aString
    else:
        Ospec = ""
    template['O'] = Ospec

    template_json = json.dumps(template)

    # Write temnplate to memory
    try:
        split_json = list(chunks(template_json.ljust(128, '>')[:128], BLOCKSIZE))
        no_of_chunks = len(split_json)
        for x in range(0, no_of_chunks):
            memory.write_block(memory.SERIAL_LOCATION + x * BLOCKSIZE, map(ord, split_json[x]))
        logger.info("Wrote template information to eeprom")
    except (ValueError, IOError):
        logger.info("Could not write version information to eeprom")
    else:
        template_info = memory.read_template()
        if template_info == template_json:
            logger.info("Verified written template info")
        else:
            logger.warning(template_info)
            logger.warning("Could not verify template info")
    return

def read_tagsignercertificate():
    read_certificate = ""
    dirname, filename = os.path.split(os.path.abspath(__file__))
    for x in range(0, 100):
        result = memory.read_block(CERTIFICATE_LOCATION + x * BLOCKSIZE, BLOCKSIZE)
        read_certificate = read_certificate + result
    if read_certificate.find("END CERTIFICATE-----") > 0:
        read_certificate = read_certificate[:1484 + 20]
    #logger.info(read_certificate)
    file_cert = open(os.path.join(dirname, 'tagsigner.cert.pem')).read().rstrip()
    if read_certificate == file_cert:
        print('Comparison OK')
    else:
        print('Comparison failed')
    return

def read_dbcertificate():
    read_certificate = ""
    dirname, filename = os.path.split(os.path.abspath(__file__))
    for x in range(0, 100):
        result = memory.read_block(DBCERTIFICATE_LOCATION + x * BLOCKSIZE, BLOCKSIZE)
        read_certificate = read_certificate + result
    if read_certificate.find("END CERTIFICATE-----") > 0:
        read_certificate = read_certificate[:1460 + 20]
    #logger.info(read_certificate)
    file_cert = open(os.path.join(dirname, 'usbdbexport.cert.pem')).read().rstrip()
    if read_certificate == file_cert:
        print('Comparison OK')
    else:
        print('Comparison failed')
    return

def write_tagsignercertificate():
    read_cert = ""
    try:
        dirname, filename = os.path.split(os.path.abspath(__file__))
        certfile = os.path.join(dirname, 'tagsigner.cert.pem')
        with open(certfile, 'r') as infile:
            cert_to_write = infile.read(2304)
    except IOError:
        logger.info("Could not read certificate from file, exiting")
        exit()
    try:
        split_cert = list(chunks(cert_to_write, BLOCKSIZE))
        no_of_chunks = len(split_cert)
        for x in range(0, no_of_chunks):
            memory.write_block(CERTIFICATE_LOCATION + x * BLOCKSIZE, map(ord, split_cert[x]))
        logger.info("Wrote signer certificate to eeprom")
    except IOError:
        # print 'Memory device not found at I2C address 0x{1:02x}'.format(CERTIFICATE_LOCATION))
        logger.info("Could not write signer certificate to eeprom")
    else:
        read_certificate = ""
        for x in range(0, no_of_chunks):
            result = memory.read_block(CERTIFICATE_LOCATION + x * BLOCKSIZE, BLOCKSIZE)
            read_certificate = read_certificate + result
        if read_certificate.find("END CERTIFICATE-----") > 0:
            read_certificate = read_certificate[:1484 + 20]

        if read_certificate == cert_to_write:
            logger.info("Verified written certificate")
    return

def write_dbexportusbcertificate():
    read_cert = ""
    try:
        dirname, filename = os.path.split(os.path.abspath(__file__))
        certfile = os.path.join(dirname, 'dbexport.cert.pem')
        with open(certfile, 'r') as infile:
            cert_to_write = infile.read(1664)
    except IOError:
        logger.info("Could not read db-certificate from file, exiting")
        exit()
    try:
        split_cert = list(chunks(cert_to_write, BLOCKSIZE))
        no_of_chunks = len(split_cert)
        for x in range(0, no_of_chunks):
            memory.write_block(DBCERTIFICATE_LOCATION+ x * BLOCKSIZE, map(ord, split_cert[x]))
        logger.info("Wrote db-backup certificate to eeprom")
    except IOError:
        # print 'Memory device not found at I2C address 0x{1:02x}'.format(CERTIFICATE_LOCATION))
        logger.info("Could not write db-backup certificate to eeprom")
    else:
        read_certificate = ""
        for x in range(0, no_of_chunks):
            result = memory.read_block(DBCERTIFICATE_LOCATION + x * BLOCKSIZE, BLOCKSIZE)
            read_certificate = read_certificate + result
        if read_certificate.find("END CERTIFICATE-----") > 0:
            read_certificate = read_certificate[:1460 + 20]

        if read_certificate == cert_to_write:
            logger.info("Verified written db-backup certificate")
    return

def clear_electrodes():
    # Empty indexes
    try:
        memory.write_electrode_index(0)
        logger.info("Wrote zero value to electrode index ptr")
    except ValueError:
        logger.info("Could not write index information to eeprom")
    else:
        # Read indexes
        electrode_index = memory.read_electrode_index()

    # Empty electrode and handle table
    try:
        limit = 50
        for x in range(0, limit):
            memory.write_electrode(x, 0, '--')
        logger.info("Cleared "+str(limit) + " electrode slots")
    except Exception as e:
        logger.info(repr(e))

    return

def clear_handles():
    # Empty indexes
    try:
        memory.write_handle_index(0)
        logger.info("Wrote zero value to handle index ptr")
    except ValueError:
        logger.info("Could not write index information to eeprom")
    else:
        # Read indexes
        handle_index = memory.read_handle_index()
    try:
        limit = 50
        for x in range(0, limit):
            memory.write_handle(x, 0, 0)
        logger.info("Cleared "+str(limit) + " handle slots")
    except Exception as e:
        logger.info(repr(e))
    return

def set_handle():
    return

def read_specific_handle():
    choice = int(raw_input("Index >>  "))
    serialnum, counter = memory.read_handle(choice)
    logger.info('Index: {}, serial #: {}, usages: {}'.format(choice, serialnum, counter))
    return

def set_specific_handle():
    index = int(raw_input("Index >>  "))
    serialnum, counter = memory.read_handle(index)
    usage = int(raw_input('usage count >> '))
    memory.write_handle(index, serialnum, usage)
    return

# Execute menu
def exec_menu(choice):
    os.system('clear')
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print "Invalid selection, please try again.\n"
            menu_actions['main_menu']()
    choice = raw_input("Continue?")
    back()


def back():
    menu_actions['main_menu']()

# Exit program
def exit():
    mySerial.lock_eeprom()

    sys.exit()

def main_menu():
    os.system('clear')

    print "Welcome,\n"
    print "Please choose the menu you want to start:"
    print "1. Read version info"
    print "2. Read matching template"
    print "3. Read electrode memory"
    print "4. Read handle memory"
    print "5. Read system serial no"
    print "6. Read tagsigner certificate"
    print "7. Read DB Export-USB certificate"
    print "--------------------------"
    print "a. Write version info"
    print "b. Write matching template"
    print "c. Copy tagsigner certificate to memory"
    print "d. Copy DB export-USB certificate to memory"
    print "e. Clear electrode memory"
    print "f. Clear handle memory"
    print "g. Read specific handle"
    print "h. Write specific handle"
    print "\n0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)

    return

menu_actions = {
    'main_menu': main_menu,
    '1': read_version,
    '2': read_template,
    '3': read_electrode,
    '4': read_handle,
    '5': read_sys_serial,
    '6': read_tagsignercertificate,
    '7': read_dbcertificate,
    'a': write_version,
    'b': write_template,
    'c': write_tagsignercertificate,
    'd': write_dbexportusbcertificate,
    'e': clear_electrodes,
    'f': clear_handles,
    'g': read_specific_handle,
    'h': set_specific_handle,
    '20': back,
    '0': exit,
}

def writedown_Version_and_date(data,logger):
    version_json = json.dumps(data)
    if len(version_json.decode("utf_8")) > 120:
        logger.error("Version object to large")
        exit()
    encoded = version_json.decode('utf_8')
    try:
        split_json = list(chunks(encoded.ljust(128, '>')[:128], BLOCKSIZE))
        # split_json = list(chunks(version_json, BLOCKSIZE))
        no_of_chunks = len(split_json)
        for x in range(0, no_of_chunks):
            memory.write_block(0 + x * BLOCKSIZE, map(ord, split_json[x]))
        logger.info("Wrote version information to eeprom")
    except ValueError:
        logger.info("Could not write version information to eeprom")
    else:
        version_info = memory.read_version()[1]
        if encoded == version_json:
            logger.info("Verified written version info")
        else:
            logger.info("Could not verify version info")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger()
    #print "Starting " + os.path.basename(__file__)
    mySerial = atmega_serial.AtmegaSerial()
    mySerial.unlock_eeprom()

    main_menu()
