from p2p import *

x = Server(packet_class=packets.Msg_Packet)
x.start()
time.sleep(3)


msg = packets.Msg_Packet("Matt", "Yo")
while True:
	send(msg.json, peers=[5000])
	time.sleep(5)
	