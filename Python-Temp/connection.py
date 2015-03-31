import re


class Connection:
	
	def __init__(self, parent, address):
		
		self.parent = parent
		self.address = address
		
		self.input_buffer = b""
		self.ouput_buffer = b""
		self.should_close = False
		
		self.protocol = ""
		self.client_handshake = ""
		self.handshake = ""
		self.secret = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
		
	def on_recv_data(self, data):
		self.input_buffer += data
		
		print("Received %d bytes from %s" % \
			  (len(data), str(self.address)))
			  
		idx = self.input_buffer.find(b"\r\n\r\n")
						
		# Received request
		if idx >= 0:
			request_string = self.input_buffer[:idx + 4].decode()
			self.input_buffer = self.input_buffer[idx+4:]
							
			request_lines = request_string.split("\r\n")
			for line in request_lines:
				if "GET" in line or "POST" in line:
					request_line = line.split(" ")
					print(request_line)
				else:
					header = re.search("(.*):(.*)", line)
									
					if header is not None:
						print(header.group(1), header.group(2))
										
						# if this is a websocket header
						if "Sec-WebSocket" in header.group(1):
							if "Sec-WebSocket-Protocol" in header.group(1):
								self.protocol = header.group(2).strip().split(",")
								
							elif "Sec-WebSocket-Key" in header.group(1):
								self.client_handshake = header.group(2).strip()
								self.handshake = hashlib.sha1((self.client_handshake + self.secret).encode())
								print(self.handshake)
								
					self.should_close = True
