from jnius import autoclass, JavaException

class AndroidBluetoothClass:
    def __init__(self, update_status):
        self.update_status = update_status
        self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        self.BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
        self.UUID = autoclass('java.util.UUID')
        self.BufferReader = autoclass('java.io.BufferedReader')
        self.InputStream = autoclass('java.io.InputStreamReader')
        self.ConnectionEstablished = False
        self.socket = None

    def getAndroidBluetoothSocket(self, DeviceName):
        try:
            paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
            for device in paired_devices:
                if device.getName() == DeviceName:
                    self.socket = device.createRfcommSocketToServiceRecord(
                        self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                    self.ReceiveData = self.BufferReader(self.InputStream(self.socket.getInputStream()))
                    self.SendData = self.socket.getOutputStream()
                    self.socket.connect()
                    self.ConnectionEstablished = True
                    self.update_status('Bluetooth Connection successful')
        except JavaException as e:
            self.update_status(f'Failed to connect: {e}')
        return self.ConnectionEstablished

    def BluetoothSend(self, Message, *args):
        if self.ConnectionEstablished:
            try:
                self.SendData.write(Message)
                self.update_status('Message sent successfully')
            except JavaException as e:
                self.update_status(f'Failed to send message: {e}')
        else:
            self.update_status('Bluetooth device not connected')

    def BluetoothReceive(self, *args):
        DataStream = ''
        if self.ConnectionEstablished:
            try:
                DataStream = str(self.ReceiveData.readLine())
                self.update_status('Data received: ' + DataStream)
            except Exception as e:
                self.update_status(f'Failed to receive data: {e}')
        return DataStream

    def close(self):
        if self.socket:
            try:
                self.socket.close()
                self.update_status('Bluetooth socket closed successfully')
            except JavaException as e:
                self.update_status(f'Failed to close socket: {e}')