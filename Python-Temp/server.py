import socket
import select
import time
import errno
import re
from connection import Connection

class WebSocketServer(object):
	
	CHUNK_SIZE = 1024
	
	def __init__(self, server_hostname, server_port):
		
		self.server_address = (server_hostname, server_port)
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setblocking(False)
		
		self.connections = {}
		self.input_list = [self.server_socket]
		self.output_list = []
		
		self.running = False
		
	def start(self):
	
		self.server_socket.bind(self.server_address)
		self.server_socket.listen(5)
		
		running = True
		while running:
			(read, write, error) = select.select(self.input_list, self.output_list, self.input_list)
			
			for sock in read:
				# New connection
				if sock is self.server_socket:
					(client_socket, client_address) = self.server_socket.accept()
					print("Accepted %s." % str(client_address))
					self.input_list.append(client_socket)
					client_socket.setblocking(False)
					self.connections[client_socket] = Connection(self, client_address)
				# Data received
				else:
					if sock not in self.output_list:
						self.output_list.append(sock)
					
					try:
						recv_data = sock.recv(WebSocketServer.CHUNK_SIZE)
					except socket.error as ex:
						error = ex.args[0]
						
						if error == errno.EAGAIN or error == errno.EWOULDBLOCK:
							continue
						else:
							print("Error receiving from %s: %s" % 	
							      (self.connections[sock], ex.args[1]))
					else:
						if len(recv_data) == 0:
							self.close(sock)
							
						self.connections[sock].on_recv_data(recv_data)
							   
			for sock in write:
				conn = self.connections[sock]
				if len(conn.output_buffer) < 1:
					if conn.should_close:
						self.close(sock)
				else:
					try:
						sent = sock.send(conn.output_buffer[:WebSocketServer.CHUNK_SIZE])
					except IOError as ex:
						print("Error while sending to %s" % str(conn[0]))
					else:
						print("Sent %d bytes to %s: %s" % (sent, str(conn[0]), data[:sent].decode()))
						conn.output_buffer = conn.output_buffer[sent:]			
							   
			for sock in error:
				self.close(sock)

	def close(self, sock):
		print("Closing %s", self.connections[sock][0])
		if sock in self.input_list:
			self.input_list.remove(sock)
		if sock in self.output_list:
			self.output_list.remove(sock)
		if sock in self.connections.keys():
			del self.connections[sock]
					
		sock.close()
				
				
				
				
server = WebSocketServer("localhost", 80)
server.start()
