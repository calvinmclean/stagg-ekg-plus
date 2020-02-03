from bluepy import btle

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
        super().__init__(self.MAC)
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
        return self._get_temps()[0][0]

    def get_target_temp(self):
        return self._get_temps()[1][0]

    def on(self):
        if not self.connected:
            self.connect()
        self.characteristic.write(bytes.fromhex("efdd0a0000010100"), withResponse=False)

    def off(self):
        if not self.connected:
            self.connect()
        self.characteristic.write(bytes.fromhex("efdd0a0400000400"), withResponse=False)

# gatttool -b 00:1C:97:18:7B:04 -I
# > connect
# > char-write-cmd 0x000d efdd0b3031323334353637383930313
# > char-write-cmd 0x000d efdd0a0000010100
# > char-write-cmd 0x000d efdd0a0400000400

# Subscribing:
# char-write-req 0x000e 0100
# char-write-cmd 0x000d efdd0b3031323334353637383930313233349a6d
# stagg.writeCharacteristic(14, b"\x01\x00")
# stagg.authenticate()
