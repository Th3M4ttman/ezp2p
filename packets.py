import json
import datetime

class Packet():
	def __init__(self, data: dict = {}, packet_type: str = "Packet", data_string = ""):
		self.data = {"packet_type": packet_type}
		for key, item in data.items():
			self.data[key] = item
		try:
			for key, item in json.loads(data_string).items():
				self.data[key] = item
		except:
			pass
	
	@property
	def json(self):
		return json.dumps(self.data)
	
	def __str__(self):
		return f"{json.dumps(self.data, indent=4)}"
		

class Msg_Packet(Packet):
	def __init__(self, name = "", content = "", **kwargs):
		data = {"name": name,
					"content": content,
					"timestamp": str(datetime.datetime.now())}
		super().__init__(data=data, packet_type="Msg_Packet", **kwargs)
	

