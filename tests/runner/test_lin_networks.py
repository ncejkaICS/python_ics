# ruff: noqa: E501
import unittest
import time
import ics

unittest.TestLoader.sortTestMethodsUsing = None

HARDWARE_DELAY = 0.2  # delay between hardware operations
LIN_TX_COUNT = 2  # number of lin msgs to send

class BaseTests:
    """Base classes. These are isolated and won't be run/discovered. Used for inheritance"""

    class TestLIN(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.netid = None

        @classmethod
        def setUp(self):
            self.fire2 = ics.find_devices([ics.NEODEVICE_FIRE2])[0]
            self.fire3 = ics.find_devices([ics.NEODEVICE_FIRE3])[0]
            self.devices = [self.fire2, self.fire3]
            for device in self.devices:
                ics.open_device(device)
                ics.load_default_settings(device)
                time.sleep(HARDWARE_DELAY)

        @classmethod
        def tearDown(self):
            for device in self.devices:
                ics.close_device(device)
            del self.devices

        def _prepare_devices(self):
            for device in self.devices:
                # Clear any messages in the buffer
                _, _ = ics.get_messages(device, False, 1)
                _ = ics.get_error_messages(device)  # Documentation is wrong -- says it can take 3 args but only takes 1

        def _tx_rx_lin_devices(self, master_dev, slave_dev):
            self._prepare_devices()

            # master msg with no data
            master_msg = ics.SpyMessageJ1850()
            master_msg.Header = (0xC1,)
            master_msg.NetworkID = self.netid
            master_msg.NetworkID2 = self.netid >> 8
            master_msg.Data = ()
            master_msg.StatusBitField = ics.SPY_STATUS_LIN_MASTER

            # slave msg with data
            slave_msg = ics.SpyMessageJ1850()
            slave_msg.Header = (0xC1,)
            slave_msg.NetworkID = self.netid
            slave_msg.NetworkID2 = self.netid >> 8
            slave_msg.Data = tuple([x for x in range(8)])
            slave_msg.Protocol = ics.SPY_PROTOCOL_LIN
            checksum = 0
            for byte in slave_msg.Data + slave_msg.Header[1:3]:
                checksum += byte
                if checksum > 255:
                    checksum -= 255
            slave_msg.Data += ((~checksum & 0xFF),)

            # transmit slave msg first
            for _ in range(LIN_TX_COUNT):
                ics.transmit_messages(slave_dev, slave_msg)
                time.sleep(HARDWARE_DELAY)

            # transmit master msg
            for _ in range(LIN_TX_COUNT):
                ics.transmit_messages(master_dev, master_msg)
                time.sleep(HARDWARE_DELAY)

            # find slave msg
            rx_msgs, errors = ics.get_messages(slave_dev, False, 1)
            self.assertFalse(errors)
            self.assertTrue(len(rx_msgs) > 0, "Didnt find any lin messages")
            msg_found = False
            error_msg = ""
            tx_msg_netid = (slave_msg.NetworkID2 << 8) | slave_msg.NetworkID
            for rx_msg in rx_msgs:
                rx_msg_netid = (rx_msg.NetworkID2 << 8) | rx_msg.NetworkID
                # check netid
                if rx_msg_netid == tx_msg_netid:
                    if rx_msg.ArbIDOrHeader != 0:
                        rx_msg_header = int(hex(rx_msg.ArbIDOrHeader)[-2:], 16)
                    else:
                        error_msg = "Found msg header was 0"
                    # check header
                    if rx_msg_header == slave_msg.Header[0]:
                        # check data
                        if rx_msg.Data == slave_msg.Data[2:]:
                            msg_found = True
                            break
                        else:
                            error_msg = f"Data doesnt match: {rx_msg.Data} and {slave_msg.Data[2:]}"
                    else:
                        error_msg = f"Headers dont match: {rx_msg_header} and {slave_msg.Header[0]}"
                else:
                    error_msg = f"Netids dont match: {rx_msg_netid} and {tx_msg_netid}"
            
            self.assertTrue(msg_found, f"Failed to find matching slave message: {error_msg}")

            for device in self.devices:
                self.assertFalse(ics.get_error_messages(device))

        def test_fire2_master_tx(self):
            self._tx_rx_lin_devices(self.fire2, self.fire3)

        def test_fire3_master_tx(self):
            self._tx_rx_lin_devices(self.fire3, self.fire2)
        
        def test_bad_messages(self):
            self._prepare_devices()
            device = self.fire3
            bad_msg = ics.SpyMessageJ1850()
            with self.assertRaises(AttributeError):
                bad_msg.Header = "bad"
            
            with self.assertRaises(TypeError):
                bad_msg.NetworkID = "bad"
            
            # transmit "bad" msg and check error counts
            with self.assertRaises(ics.RuntimeError):
                ics.transmit_messages(device, "bad")
            errors = ics.get_last_api_error(device)
            self.assertGreater(len(errors), 0, "Error count didnt increment after bad message")
            _, errors = ics.get_messages(device, False, 1)
            self.assertGreater(errors, 0, "Error count didnt increment after bad message")
            
            # not sure why this fails when ran again...
            with self.assertRaises(ics.RuntimeError):
                ics.get_last_api_error(device)
            
            # get errors and check that count is cleared after
            errors = ics.get_error_messages(device)
            self.assertGreater(len(errors), 0)
            _, errors = ics.get_messages(device, False, 1)
            self.assertEqual(errors, 0, "Error count didnt reset after getting error messages")
            
            # try more data than 8 bytes -- doesnt cause error
            # bad_msg.Header = (0xC1,)
            # bad_msg.NetworkID = self.netid
            # bad_msg.NetworkID2 = self.netid >> 8
            # bad_msg.StatusBitField = ics.SPY_STATUS_LIN_MASTER
            # bad_msg.Data = tuple([x for x in range(32)])
            # bad_msg.Protocol = ics.SPY_PROTOCOL_LIN
            
            # send blank message and check other side
            # bad_msg = ics.SpyMessageJ1850()
            # ics.transmit_messages(device, bad_msg)
            
            
            # stuff1, stuff2 = ics.get_messages(device, False, 1)
            # stuff3 = ics.get_error_messages(device)
            # print(f"stuff1: {stuff1}")
            # print(f"stuff2: {stuff2}")
            # print(f"stuff3: {stuff3}")

class TestLIN1(BaseTests.TestLIN):
    @classmethod
    def setUpClass(cls):
        cls.netid = ics.NETID_LIN


# class TestLIN2(BaseTests.TestLIN):
#     @classmethod
#     def setUpClass(cls):
#         cls.netid = ics.NETID_LIN2


# class TestLIN3(BaseTests.TestLIN):
#     @classmethod
#     def setUpClass(cls):
#         cls.netid = ics.NETID_LIN3


# class TestLIN4(BaseTests.TestLIN):
#     @classmethod
#     def setUpClass(cls):
#         cls.netid = ics.NETID_LIN4


if __name__ == "__main__":
    unittest.main()
