#!/usr/bin/python3

def communicate(dest, cmd, payload = []):
	msg = [dest, cmd]
	msg.append(len(payload)/256)
	msg.append(len(payload)%256)
	msg = msg + payload
	message_to_send = ''
	cs = 0
	for i in msg:
		message_to_send += chr(i)
		cs += i
	message_to_send += chr((0x100 - (cs % 0x100)) & 0xFF)
	# send the message to MBTemp
	return("%s" %message_to_send) 