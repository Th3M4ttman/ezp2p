import socket
import json
import threading
import time
from . import packets
from . import portforwardlib


class Address():
	def __init__(self, host: str = "localhost", port:int = 5000):
		self.host = host
		self.port = port
	
	def __str__(self):
		return f"{self.host}:{self.port}"
	def __repr__(self):
		return str(self)
		
class Server(threading.Thread):
	def __init__(self, port: int = 5000, encoding = "utf-8", encryption = "AES", forward = True, packet_class = packets.Packet):
		threading.Thread.__init__(self, name="Server", daemon=True)
		if forward:
			portforwardlib.forwardPort(port, port, None, None, True, "tcp", 0, None, True)
			portforwardlib.forwardPort(port, port, None, None, False,  "tcp", 0, None, True)
		self.address = Address("0.0.0.0", port)
		self.listening = False
		self.stop = False
		self.verbose = True
		self.encoding = encoding
		self.encryption = encryption
		self.packet_class = packet_class
	
	def listen(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(("0.0.0.0", self.address.port))
		sock.listen(10)
		self.listening = True
		print(self)
		while not self.stop:
			connection, client_address = sock.accept()
			try:
				full_message = b""
				while not self.stop:
					data = connection.recv(16)
					full_message += data
					if not data: break
			finally:
				recieved_packet = self.packet_class(data_string=full_message)
				if self.verbose:
					print(f"Recieved: {recieved_packet}")
				self.process_data(recieved_packet)
				connection.shutdown(2)
				connection.close()
 
	def run(self):
		self.listen()
		
	def process_data(self, data):
		print(f"Processed {data}")
		
	def __str__(self):
		listening = "Listening" if self.listening else "Not Listening"
		return f"{listening} on {self.address}"

def send(data, peers, encoding="utf-8", encryption = None, max_retries = 3):
	peer_list = []
	if type(peers) in (list, tuple):
		for peer in peers:
			if type(peer) == str:
				if peer.isnumeric():
					peer_list.append(Address(port=int(peer)))
					continue
				try:
					h, p = peer.split(":")
					peer_list.append(Address(host=h, port=int(p)))
					continue
				except Exception:
					continue
			elif type(peer) == int:
				peer_list.append(Address(port=peer))
			elif type(peer) == Address:
				peer_list.append(peer)
				
			else:
				print(f"{type(peer)} not in accepted types (str, int, Address)")
	elif type(peers) == int:
		peer_list = [Address(port=peers)]
	elif type(peers) == str:
		try:
			h, p = peer.split(":")
			peer_list = [Address(host=h, port=int(p))]
		except IndexError as e:
			raise e
	else:
		raise TypeError("Peers must be of type list/tuple/str/int")
	print("Sending", data, "to", peer_list, "encoding:", encoding, "encryption", encryption)
	
	data = bytes(data, encoding=encoding)
	
	for peer in peer_list:
		host = peer.host
		port = peer.port
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		retries = 0
		while retries < max_retries:
			try:
				s.connect((host, port))
				s.sendall(data)
				s.shutdown(2)
				s.close()
				break
			except Exception as e:
				print(e)
				print(f"Couldn't Connect to {host}:{port}, retrying...")
				retries += 1
