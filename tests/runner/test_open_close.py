# ruff: noqa: E501
import unittest
import ics

unittest.TestLoader.sortTestMethodsUsing = None


class TestOpenClose(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.expected_dev_count = 5
        self.devices = ics.find_devices()

    @classmethod
    def setUp(self):
        pass

    @classmethod
    def tearDownClass(self):
        # For some reason tp_dealloc doesn't get called on
        # ics.NeoDevice when initialzed in setUpClass().
        # Lets force it here.
        del self.devices

    def _check_devices(self):
        devices = ics.find_devices()
        self.assertEqual(
            len(devices),
            self.expected_dev_count,
            f"Device check expected {self.expected_dev_count} devices, found {len(devices)}: {devices}...",
        )
    
    # look for each device type separately
    def test_find_fire2(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE2])
        self.assertTrue(len(devices) == 1)
        self.assertEqual(devices[0].DeviceType, ics.NEODEVICE_FIRE2)
    
    def test_find_fire3(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE3])
        self.assertTrue(len(devices) == 1)
        self.assertEqual(devices[0].DeviceType, ics.NEODEVICE_FIRE3)
    
    def test_find_moon2s(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_RADMOON2])
        self.assertTrue(len(devices) == 2)
        self.assertEqual(devices[0].DeviceType, ics.NEODEVICE_RADMOON2)
        self.assertEqual(devices[1].DeviceType, ics.NEODEVICE_RADMOON2)

    def test_find_vcan42(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_VCAN42])
        self.assertTrue(len(devices) == 1)
        self.assertEqual(devices[0].DeviceType, ics.NEODEVICE_VCAN42)

    # look for fire2 and one other device type
    def test_find_fire2_fire3(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE2, ics.NEODEVICE_FIRE3])
        self.assertTrue(len(devices) == 2)
    
    def test_find_fire2_vcan42(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE2, ics.NEODEVICE_VCAN42])
        self.assertTrue(len(devices) == 2)

    def test_find_fire2_moon2(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE2, ics.NEODEVICE_RADMOON2])
        self.assertTrue(len(devices) == 3)

    # look for fire3 and one other device type
    def test_find_fire3_moon2(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE3, ics.NEODEVICE_RADMOON2])
        self.assertTrue(len(devices) == 3)
    
    def test_find_fire3_vcan42(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE3, ics.NEODEVICE_VCAN42])
        self.assertTrue(len(devices) == 2)
    
    # look for moon2 and vcan42
    def test_find_moon2_vcan42(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_RADMOON2, ics.NEODEVICE_VCAN42])
        self.assertTrue(len(devices) == 3)
    
    # look for three device types
    def test_find_fire2_fire3_moon2(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE2, ics.NEODEVICE_FIRE3, ics.NEODEVICE_RADMOON2])  # no vcan42
        self.assertTrue(len(devices) == 4)
    
    def test_find_fire2_fire3_vcan42(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE2, ics.NEODEVICE_FIRE3, ics.NEODEVICE_VCAN42])  # no moon2
        self.assertTrue(len(devices) == 3)
    
    def test_find_fire2_moon2_vcan42(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE2, ics.NEODEVICE_RADMOON2, ics.NEODEVICE_VCAN42])  # no fire3
        self.assertTrue(len(devices) == 4)
    
    def test_find_fire3_moon2_vcan42(self):
        self._check_devices()
        devices = ics.find_devices([ics.NEODEVICE_FIRE3, ics.NEODEVICE_RADMOON2, ics.NEODEVICE_VCAN42])  # no fire2
        self.assertTrue(len(devices) == 4)
    
    # look for all four device types -- major bug that crashes python
    # def test_find_fire2_fire3_moon2_vcan42(self):
    #     self._check_devices()
    #     # Weird error here where ics.find_devices([...]) with all device types crashes python and going one by one sometimes fixes it
    #     # ics.find_devices([ics.NEODEVICE_FIRE2])
    #     # ics.find_devices([ics.NEODEVICE_FIRE2, ics.NEODEVICE_FIRE3])
    #     # ics.find_devices([ics.NEODEVICE_FIRE2, ics.NEODEVICE_FIRE3, ics.NEODEVICE_VCAN42])
    #     ics.find_devices([ics.NEODEVICE_FIRE2, ics.NEODEVICE_FIRE3, ics.NEODEVICE_VCAN42, ics.NEODEVICE_RADMOON2])
    #     # assigning output to variable does sometimes help or hurt too
    #     devices = ics.find_devices([ics.NEODEVICE_FIRE2, ics.NEODEVICE_FIRE3, ics.NEODEVICE_VCAN42, ics.NEODEVICE_RADMOON2])

    def test_number_of_clients(self):
        self._check_devices()
        for dev in self.devices:
            # skip 2nd moon2
            if dev.serial_number != ics.find_devices([dev.DeviceType])[0].serial_number:
                continue
            self.assertEqual(
                ics.find_devices([dev.DeviceType])[0].NumberOfClients,
                0,
                f"Device {dev} not at 0 NumberOfClients before opening",
            )
            self.assertEqual(dev.MaxAllowedClients, 1)
            d = ics.open_device(dev)
            try:
                self.assertEqual(dev, d)
                # must search again to see number of clients actually increment
                self.assertEqual(
                    ics.find_devices([dev.DeviceType])[0].NumberOfClients,
                    1,
                    f"Device {dev} failed to increment NumberOfClients after opening",
                )
                self.assertEqual(dev.MaxAllowedClients, 1)

                self.assertEqual(
                    ics.find_devices([d.DeviceType])[0].NumberOfClients,
                    1,
                    f"Device {d} failed to increment NumberOfClients after opening",
                )
                self.assertEqual(d.MaxAllowedClients, 1)
            finally:
                ics.close_device(d)
                self.assertEqual(
                    ics.find_devices([dev.DeviceType])[0].NumberOfClients,
                    0,
                    f"Device {dev} failed to decrement NumberOfClients after opening",
                )
                self.assertEqual(
                    ics.find_devices([d.DeviceType])[0].NumberOfClients,
                    0,
                    f"Device {d} failed to decrement NumberOfClients after opening",
                )

            # Now try with NeoDevice functions
            try:
                dev.open()
                self.assertEqual(
                    ics.find_devices([dev.DeviceType])[0].NumberOfClients,
                    1,
                    f"Device {dev} failed to increment NumberOfClients after opening",
                )
            finally:
                dev.close()
                self.assertEqual(
                    ics.find_devices([dev.DeviceType])[0].NumberOfClients,
                    0,
                    f"Device {dev} failed to decrement NumberOfClients after opening",
                )

    def test_open_close_by_serial(self):
        self._check_devices()
        for dev in self.devices:
            d = ics.open_device(dev.SerialNumber)
            self.assertEqual(d.SerialNumber, dev.SerialNumber)
            ics.close_device(d)

    def test_open_close_first_found(self):
        self._check_devices()
        first_devices = []
        for _ in range(self.expected_dev_count):
            try:
                d = ics.open_device()
                first_devices.append(d)
            except ics.RuntimeError as ex:
                raise RuntimeError(
                    f"Failed to open first found device on iteration {len(first_devices)}: {ex}"
                )
        self.assertEqual(self.expected_dev_count, len(first_devices))
        # Close by API
        for device in first_devices:
            ics.close_device(device)

    def test_open_close_5_times(self):
        self._check_devices()
        for dev in self.devices:
            for x in range(5):
                try:
                    ics.open_device(dev)
                    error_count = ics.close_device(dev)
                    self.assertEqual(
                        error_count,
                        0,
                        f"Error count was not 0 on {dev} iteration {x}...",
                    )
                except Exception as ex:
                    print(f"Failed at iteration {x} {dev}: {ex}...")
                    raise ex

                # Now try with NeoDevice functions
                try:
                    dev.open()
                    error_count = dev.close()
                    self.assertEqual(
                        error_count,
                        0,
                        f"Error count was not 0 on {dev} iteration {x}...",
                    )
                except Exception as ex:
                    print(f"Failed at iteration {x} {dev}: {ex}...")
                    raise ex

    def test_auto_close(self):
        self._check_devices()
        devices = ics.find_devices()
        for dev in devices:
            ics.open_device(dev)
        del devices
        devices = ics.find_devices()
        for dev in devices:
            ics.open_device(dev)
            ics.close_device(dev)
        del devices

    def test_can_only_open_once(self):
        self._check_devices()
        for dev in self.devices:
            ics.open_device(dev)
            with self.assertRaises(SystemError):
                ics.open_device(dev)
            with self.assertRaises(SystemError):
                dev.open()
            ics.close_device(dev)


if __name__ == "__main__":
    unittest.main()
