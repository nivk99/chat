import unittest

from src.client.client import Client

client1: Client = Client(test=True)

class MyTestCase(unittest.TestCase):

    def test_get_soc(self):
        self.assertEqual(None,client1.get_soc())

    def test_get_name(self):
        self.assertEqual("", client1.get_name())

    def test_get_port(self):
        self.assertEqual(5555, client1.get_port())

    def test_get_ip(self):
        self.assertEqual("127.0.0.1", client1.get_ip())

    def test_set_name(self):
        client1.set_name("")
        self.assertEqual("", client1.get_name())
        client1.set_name(None)
        self.assertEqual("", client1.get_name())
        client1.set_name("test")
        self.assertEqual("test", client1.get_name())

    def test_set_ip(self):
        client1.set_ip("")
        self.assertEqual("127.0.0.1", client1.get_ip())
        client1.set_ip(None)
        self.assertEqual("127.0.0.1", client1.get_ip())
        client1.set_ip("0.0.0.0")
        self.assertEqual("0.0.0.0", client1.get_ip())

    def test_set_port(self):
        client1.set_port(122)
        self.assertEqual(5555, client1.get_port())
        client1.set_port(65536)
        self.assertEqual(5555, client1.get_port())
        client1.set_port(None)
        self.assertEqual(5555, client1.get_port())
        client1.set_port(7777)
        self.assertEqual(7777, client1.get_port())

















if __name__ == '__main__':
    unittest.main()
