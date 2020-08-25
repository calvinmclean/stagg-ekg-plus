from bluepy import btle
from bluepy.btle import BTLEInternalError, BTLEDisconnectError
from time import sleep

class StaggEKGDelegate(btle.DefaultDelegate):
    """
    Process notifications from Fellow StaggEKG.
    """
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.notifications = []

    def handleNotification(self, cHandle, data):
        if (
            (len(data) == 4) and
            (data[0] != 239 and data[1] != 221) and
            (int(data.hex(), base=16) != 0)
        ):
            self.notifications.append(data)
        self.notifications = self.notifications[-100:]

    def reset(self):
        self.notifications = []

class StaggEKG(btle.Peripheral):
    def __init__(self, mac):
        self.MAC = mac
        self.connect()
        self._get_temps()
        self._get_temps()

    def authenticate(self):
        if self.characteristic:
            self.characteristic.write(bytes.fromhex("efdd0b3031323334353637383930313233349a6d"), withResponse=False)

    def connect(self):
        attempts = 0
        while attempts < 10:
            try:
                super().__init__(self.MAC)
                break
            except (BTLEInternalError, BTLEDisconnectError) as e:
                attempts += 1
                print("Failed to connect... Attempt: %s Error: %s" % (attempts, e))
                print("Retrying in 5 seconds...")
                sleep(5)
        self.service = self.getServiceByUUID("00001820-0000-1000-8000-00805f9b34fb")
        self.characteristic = self.service.getCharacteristics()[0]
        # Authenticate
        self.authenticate()
        self.setDelegate(StaggEKGDelegate())
        self.connected = True

    def disconnect(self):
        self.connected = False
        super().disconnect()

    def set_temp(self, temp):
        if temp < 104 or temp > 212:
            raise ValueError("temp must be between 104 and 212")
        if not self.connected:
            self.connect()
        try:
            self.characteristic.write(bytes.fromhex("efdd0a0001{hex}{hex}01".format(hex=hex(temp)[2:])), withResponse=False)
        except (BTLEInternalError, BTLEDisconnectError) as e:
            print("Connection error! Reconnecting... %s" % e)
            self.connect()
            self.characteristic.write(bytes.fromhex("efdd0a0001{hex}{hex}01".format(hex=hex(temp)[2:])), withResponse=False)

    def _get_temps(self):
        self.writeCharacteristic(self.characteristic.valHandle + 1, b"\x01\x00")
        self.authenticate()
        if self.waitForNotifications(1.0):
            notifications = self.delegate.notifications
            # Find latest b"\xff\xff\xff\xff" to get two values before it
            try:
                i = len(notifications) - 1 - notifications[::-1].index(b"\xff\xff\xff\xff")
            except:
                i = 0
            if i > 2:
                return notifications[i - 2], notifications[i - 1]
            return 0, 0

    def get_current_temp(self):
        current_temp = 32
        try:
           current_temp =  self._get_temps()[0][0]
        except (BTLEInternalError, BTLEDisconnectError) as e:
            print("Connection error! Reconnecting... Error: %s" % e)
            self.connect()
            try:
                current_temp =  self._get_temps()[0][0]
            except TypeError as e:
                print("Using failback current temp... Error: %s" % e)
        except TypeError as e:
            print("Using failback current temp... Error: %s" % e)
        return current_temp

    def get_target_temp(self):
        target_temp = 212
        try:
            target_temp = self._get_temps()[1][0]
        except (BTLEInternalError, BTLEDisconnectError) as e:
            print("Connection error! Reconnecting... %s" % e)
            self.connect()
            try:
                target_temp = self._get_temps()[1][0]
            except TypeError as e:
                print("Setting default target temp... %s" % e)
        except TypeError as e:
            print("Setting default target temp... %s" % e)
        return target_temp

    def on(self):
        if not self.connected:
            self.connect()
        try:
            self.characteristic.write(bytes.fromhex("efdd0a0000010100"), withResponse=False)
        except (BTLEInternalError, BTLEDisconnectError) as e:
            print("Connection error! Reconnecting... %s" % e)
            self.connect()
            self.characteristic.write(bytes.fromhex("efdd0a0000010100"), withResponse=False)

    def off(self):
        if not self.connected:
            self.connect()
        try:
            self.characteristic.write(bytes.fromhex("efdd0a0400000400"), withResponse=False)
        except (BTLEInternalError, BTLEDisconnectError) as e:
            print("Connection error! Reconnecting... %s" % e)
            self.connect()
            self.characteristic.write(bytes.fromhex("efdd0a0400000400"), withResponse=False)
