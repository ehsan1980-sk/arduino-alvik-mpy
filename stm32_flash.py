from time import sleep_ms
from machine import Pin, UART

STM32_INIT = b'\x7F'
STM32_NACK = b'\x1F'
STM32_ACK = b'\x79'

# STM32 COMMANDS
STM32_GET = b'\x00'
STM32_GET_VERSION = b'\x01'
STM32_GET_ID = b'\x02'
STM32_READ = b'\x11'
STM32_GO = b'\x21'
STM32_WRITE = b'\x31'
STM32_ERASE = b'\x43'

STM32_ADDRESS = bytes.fromhex('08000000')  # [b'\x08',b'\x00',b'\x00',b'\x00']

# UART SETTINGS
_UART_ID = 1
_TX_PIN = 43
_RX_PIN = 44
_BAUDRATE = 115200
_BITS = 8
_PARITY = 0
_STOP = 1

readAddress = bytearray(STM32_ADDRESS)
writeAddress = bytearray(STM32_ADDRESS)

uart = UART(_UART_ID, baudrate=_BAUDRATE, bits=_BITS, parity=_PARITY, stop=_STOP, tx=_TX_PIN,
            rx=_RX_PIN)  # parity 0 equals to Even, 1 to Odd


def STM32_startCommunication() -> bytes:
    """
    Starts communication with STM32 sending just 0x7F. Blocking
    :return:
    """
    uart.write(STM32_INIT)
    return _STM32_waitForAnswer()


def _STM32_waitForAnswer() -> bytes:
    """
    Blocking wait
    :return: returns ACK or NACK
    """

    while True:
        res = uart.read(1)
        if res == STM32_ACK or res == STM32_NACK:
            break
        else:
            sleep_ms(10)

    return res


def STM32_sendCommand(cmd: bytes):
    """
    Sends a command and its complement according to AN3155
    :param cmd: the command byte
    :return:
    """
    _cmd = bytes([cmd[0] ^ 0xFF])
    uart.write(cmd)
    uart.write(_cmd)


def STM32_readResponse() -> [bytearray, int]:
    """
    Blocking read to get the STM32 response to command, according to AN3155
    :return: returns a response bytearray dropping leading and trailing ACKs. returns -1 if NACK
    """
    out = bytearray(0)

    acks = 0
    while True:
        b = uart.read(1)
        if b is None:
            continue
        if b == STM32_NACK:
            return -1
        elif b == STM32_ACK:
            if acks == 1:
                break
            else:
                acks = acks + 1
                continue
        out.append(b[0])

    return out


def STM32_get() -> bytearray:
    """
    GET Command according to AN3155
    :return: returns a bytearray containing bootloader version (1 byte) and available commands
    """
    STM32_sendCommand(STM32_GET)
    res = STM32_readResponse()
    if res == -1:
        print("GET: STM32 responded with NACK")
        return bytearray(0)
    return res[1:]


def STM32_getID() -> bytearray:
    """
    GET ID Command according to AN3155
    :return: returns device ID (2 bytes)
    """
    STM32_sendCommand(STM32_GET_ID)
    res = STM32_readResponse()
    if res == -1:
        print("GET_ID: STM32 responded with NACK")
        return bytearray(0)
    return res[1:]


def STM32_getVER() -> bytearray:
    """
    GET ID Command according to AN3155
    :return: returns bootloader version (3 bytes)
    """
    STM32_sendCommand(STM32_GET_VERSION)
    res = STM32_readResponse()
    if res == -1:
        print("GET VER: STM32 responded with NACK")
        return bytearray(0)
    return res


def _STM32_readMode() -> bytes:
    """
    Enters read memory mode. Blocking
    :return: returns ACK or NACK
    """
    STM32_sendCommand(STM32_READ)
    return _STM32_waitForAnswer()


def _STM32_writeMode() -> bytes:
    """
    Enters write memory mode. Blocking
    :return: returns ACK or NACK
    """
    STM32_sendCommand(STM32_WRITE)
    return _STM32_waitForAnswer()


def _STM32_sendAddress(address: bytes) -> bytes:
    """
    Sends the start address of read/write operations. Blocking
    :param address:
    :return:
    """
    assert len(address) == 4

    checksum = address[0] ^ address[1] ^ address[2] ^ address[3]
    uart.write(address)
    uart.write(bytes([checksum]))

    return _STM32_waitForAnswer()


def _incrementAddress(address: bytearray):
    """
    Incremets address by one page (256 bytes)
    :param address:
    :return:
    """

    address[2] = address[2] + 1
    if address[2] == 0:
        address[1] = address[1] + 1
        if address[1] == 0:
            address[0] = address[0] + 1


def _STM32_readPage() -> bytearray:
    """
    Reads a 256 bytes data page from STM32. Returns a 256 bytearray. Blocking
    :return: page bytearray
    """

    STM32_sendCommand(b'\xFF')
    res = _STM32_waitForAnswer()
    if res != STM32_ACK:
        print("READ PAGE: Cannot read STM32")
        return bytearray(0)
    out = bytearray(0)
    i = 0
    while i < 256:
        b = uart.read(1)
        if b is None:
            continue
        out.append(b[0])
        i = i+1
    return out


def _STM32_flashPage(data: bytearray) -> bytes:
    """
    Sends a 256 bytes data page to STM32. Blocking
    :param data:
    :return:
    """

    assert len(data) == 256

    uart.write(b'\xff')     # page length
    checksum = 0xff         # starting checksum = page length

    for d in data:
        uart.write(d)
        checksum = checksum ^ d

    uart.write(bytes([checksum]))

    return _STM32_waitForAnswer()
