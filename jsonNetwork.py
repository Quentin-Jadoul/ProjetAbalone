import socket as s
import json
import time

class NotAJSONObject(Exception):
	pass

class Timeout(Exception):
	pass

def sendJSON(socket, obj):
	message = json.dumps(obj)
	print("message:",message)
	if message[0] != '{':
		raise NotAJSONObject('sendJSON support only JSON Object Type')
	message = message.encode('utf8')
	print(message)
	total = 0
	while total < len(message):
		sent = socket.send(message[total:])
		total += sent

def receiveJSON(socket, timeout = 1):
	finished = False
	message = ''
	data = ''
	start = time.time()
	while not finished:
		message += socket.recv(4096).decode('utf8')
		if len(message) > 0 and message[0] != '{':
			raise NotAJSONObject('Received message is not a JSON Object')
		try:
			print('msj2',message)
			data = json.loads(message)
			print(data)
			finished = True
		except json.JSONDecodeError:
			if time.time() - start > timeout:
				raise Timeout()
	return data

def fetch(address, data, timeout=1):
	'''
		Request response from address. Data is included in the request
	'''
	print('fetch')
	socket = s.socket()
	socket.connect(address)
	print('data',data)
	print('addrress',address)
	sendJSON(socket, data)
	response = receiveJSON(socket, timeout)
	print(response)

	return response