import unittest

from src.server.server import Server

server1:Server = Server(test=True)

class MyTestCase(unittest.TestCase):

    def test_get_soc(self):
        self.assertEqual(None, server1.get_soc())

    def test_get_port(self):
        self.assertEqual(5555, server1.get_port())

    def test_get_ip(self):
        self.assertEqual("0.0.0.0", server1.get_ip())

    def test_set_port(self):
        server1.set_port(122)
        self.assertEqual(5555, server1.get_port())
        server1.set_port(65536)
        self.assertEqual(5555, server1.get_port())
        server1.set_port(None)
        self.assertEqual(5555, server1.get_port())
        server1.set_port(7777)
        self.assertEqual(7777, server1.get_port())


    def test_set_ip(self):
        server1.set_ip("")
        self.assertEqual("0.0.0.0",  server1.get_ip())
        server1.set_ip(None)
        self.assertEqual("0.0.0.0",  server1.get_ip())
        server1.set_ip("0.0.0.0")
        self.assertEqual("0.0.0.0",  server1.get_ip())









if __name__ == '__main__':
    unittest.main()
