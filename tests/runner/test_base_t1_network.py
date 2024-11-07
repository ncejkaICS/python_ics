import os
from subprocess import PIPE, Popen
import unittest
import ics

unittest.TestLoader.sortTestMethodsUsing = None


class BaseTests:
    """Base classes. These are isolated and won't be run/discovered. Used for inheritance"""

    class TestEthernet(unittest.TestCase):
        @classmethod
        def setUp(self):
            self.devices = ics.find_devices([ics.NEODEVICE_RADMOON2])
            for device in self.devices:
                ics.open_device(device)
                ics.load_default_settings(device)
                ics.close_device(device)

        @classmethod
        def tearDown(self):
            for device in self.devices:
                ics.open_device(device)
                ics.load_default_settings(device)
                ics.close_device(device)
        
        def _set_link_mode_setting(self, device, link_mode: int):
            """Set link mode: 0 = auto, 1 = master, 2 = slave"""
            ics.open_device(device)
            base_settings = ics.get_device_settings(device)
            base_settings.Settings.radmoon2.opEth1.ucConfigMode = link_mode
            ics.set_device_settings(device, base_settings)
            ics.close_device(device)

        def test_ethernet_moon2s(self):
            ethernet_exe_path = os.path.join(os.getcwd(), "tests\\runner\\BaseT1\\ethernet_test.exe")
            dev1_nic_ip = "192.168.69.10"
            dev2_nic_ip = "192.168.69.11"
            loop_count = 100
            bidirectional_traffic = True

            args = " ".join([
                ethernet_exe_path,
                dev1_nic_ip,
                dev2_nic_ip,
                str(loop_count),
                str(int(bidirectional_traffic)),
            ])

            # First test in auto mode (default)
            program = Popen(
                args,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
            )
            stdout_buffer, stderr_buffer = program.communicate()
            self.assertEqual(len(stderr_buffer), 0)
            self.assertEqual(program.returncode, 0, f"Returncode not 0: {program.returncode}")

            # Test with master/slave mode
            self._set_link_mode_setting(self.devices[0], 1)
            self._set_link_mode_setting(self.devices[1], 2)
            program = Popen(
                args,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
            )
            stdout_buffer, stderr_buffer = program.communicate()
            self.assertEqual(len(stderr_buffer), 0)
            self.assertEqual(program.returncode, 0, f"Returncode not 0: {program.returncode}")

            # Test with slave/master mode
            self._set_link_mode_setting(self.devices[0], 2)
            self._set_link_mode_setting(self.devices[1], 1)
            program = Popen(
                args,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
            )
            stdout_buffer, stderr_buffer = program.communicate()
            self.assertEqual(len(stderr_buffer), 0)
            self.assertEqual(program.returncode, 0, f"Returncode not 0: {program.returncode}")


class TestT1Ethernet(BaseTests.TestEthernet):
    @classmethod
    def setUpClass(cls):
        # moon2 eth1 = T1, eth2 = T
        pass


if __name__ == "__main__":
    unittest.main()
