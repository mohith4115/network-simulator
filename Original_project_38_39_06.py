import random
import threading
import time

def make_frames(sender_device,receiver_device,message): #frame making
    message = {'Data':message,'H2':[sender_device.address, receiver_device.address]}
    return message

    


def send_data(d1,message,ack_msg=False):
    print("Frame : {}".format(message))
    for i in d1.connected_to:
        i.chain_send(message,d1,ack_msg)

def swap_address(uwu):
    """Swaping Method"""
    uwu[0],uwu[1] = uwu[1],uwu[0]
    return uwu

def create_ack(message):
    message['Data'] = "ACK For Frame containing data '{}'".format(message['Data'])
    # message['H3'] = swap_address(message['H3'])
    message['H2'] = swap_address(message['H2'])
    return message

def create_mac_address():
    mac = [str(random.randint(0xB, 0x63)) for x in range(3)]
    return ("11:11:11:" + ":".join(mac))


class devices:

    def __init__(self, id, address, port='a', active=True):
        self.id = id
        self.address = address
        self.port = port
        self.active = active
        self.connected_to = []
        # self.arp_table = {}


    def make_inactive(self):
        self.active = False

    def make_active(self):
        self.active = True

    def chain_send(self, message, sender, ack_msg=False):
        if message["H2"][1] == self.address:
            print("Devive with MAC : {} Recieved Data From Source : {} ".format(message["H2"][1], message['H2'][0]))
            if not ack_msg:
                if random.randint(0,100) > 0:
                    print("Device {} : returning ACK ".format(self.id))
                    send_data(self, create_ack(message), True)
                else:
                    print("Device {} : ACK Lost!".format(self.id))
                    send_data(sender, message)
        else:
            print("Device {} : is not the reciver ".format(self.id))


class hub_device(devices):
    def __init__(self, id, port='a', active=True):
        self.id = id
        self.active = active
        self.connected_to = []
        self.port = port

    def chain_send(self, message, sender, ack_msg=False):
        for i in self.connected_to:
            if i == sender:
                continue
            i.chain_send(message, self, ack_msg)






class Bridge(devices):
    def __init__(self, id, address, ports=['a', 'b'], active=True):
        self.mac_table = {}
        self.mac_table[ports[0]] = []
        self.mac_table[ports[1]] = []
        self.ports = ports
        self.address = address
        self.id = id
        self.active = active
        self.connected_to = []

    def chain_send(self, message, sender, ack_msg=False):

        if message['H2'][0] not in self.mac_table[sender.port]:
            self.mac_table[sender.port].append(message['H2'][0])
        if message['H2'][1] in self.mac_table[sender.port]:
            return
        elif message['H2'][1] not in self.mac_table[sender.port]:
            # Send Message To Port
            for i in self.connected_to:
                if i.port != sender.port:
                    i.chain_send(message, self, ack_msg)


class Switch(Bridge):
    def __init__(self, id, address, ports=['a', 'b', 'c', 'd', 'e'], active=True):
        self.id = id
        self.mac_table = {}
        self.address = address
        self.ports = ports
        for i in ports:
            self.mac_table[i] = []
        self.connected_to = []
        self.active = active

    def chain_send(self, message, sender, ack_msg=False):
        if message['H2'][0] not in self.mac_table[sender.port]:
            self.mac_table[sender.port].append(message['H2'][0])


        if message['H2'][1] in self.mac_table[sender.port]:
            return
        else:
            forward_port = None
            for key in self.mac_table.keys():
                if message['H2'][1] in self.mac_table[key]:
                    forward_port = key
                    break
            if(forward_port is not None):
                for i in self.connected_to:
                    if i.port == forward_port:
                        # if type(i) == hub_device or :
                        i.chain_send(message,self,ack_msg)

            else:
                for i in self.connected_to:
                    if i.port != sender.port:
                        i.chain_send(message, self, ack_msg)





class Topology:

    def __init__(self):

        self.num_devices = 0
        self.num_hub_device = 0
        self.num_bridges = 0
        self.num_switches = 0
        self.num_routers = 0
        self.__devices = []
        self.td = 0
        self.connections = []

    def add_device_device(self, device):
        self.num_devices += 1
        self.__devices.append(device)
        self.td += 1
        self.connections.append([])

    def add_device_hub(self, hub):
        self.num_hub_device += 1
        self.__devices.append(hub)
        self.td += 1
        self.connections.append([])

    def add_device_bridge(self, bridge):
        self.num_bridges += 1
        self.__devices.append(bridge)
        self.td += 1
        self.connections.append([])

    def add_device_switch(self, swtich):
        self.num_switches += 1
        self.__devices.append(swtich)
        self.td += 1
        self.connections.append([])

    def check_valid_device(self, d1, d2):
        if d1 >= self.td or d2 >= self.td:
            raise Exception("No device with given id exists")

    def check_device_status(self, d1, d2):
        if not ((self.__devices[d1].active) and (self.__devices[d2].active)):
            raise Exception("Activate the device")

    def check_connection(self, d1, d2):
        for i in self.connections[d1]:
            if type(i) == hub_device:
                i.broadcast(d1, d2)
                break
        if self.__devices[d2] in self.connections[d1]:
            return
        else:
            raise Exception("these two devices are not connected")

    def make_connection_between(self, d1, d2, interface=-1):

        self.check_valid_device(d1, d2)
        self.connections[d1].append(self.__devices[d2])
        self.connections[d2].append(self.__devices[d1])
        self.__devices[d1].connected_to.append(self.__devices[d2])
        self.__devices[d2].connected_to.append(self.__devices[d1])

    def send_msg(self, sender_device, receiver_device, data):

        global token
        while token != sender_device.id:
            print("Device {} has the token".format(token))
            time.sleep(0.5)
        print("Device {} has the token.".format(sender_device.id))

        message = make_frames(sender_device, receiver_device, data)


        for i in sender_device.connected_to:
            if type(i) == Switch or type(i) == hub_device or type(i) == Bridge:
                return i.chain_send(message, sender_device)

    def stop_and_wait(self, sender_device, receiver_device, data):
        message = data.split()
        for msg in message:
            print(msg)
            self.send_msg(sender_device, receiver_device, msg)

    def make_active(self, number):
        self.__devices[number].active = True

    def make_inactive(self, number):
        self.__devices[number].active = False

token = 0
def get_token(num_devices):
    global token
    while True:
        time.sleep(0.5)
        token += 1
        if token == num_devices:
            token = -1


# DRIVER CODE ------>>



topology1 = Topology()

D0 = devices(topology1.td , create_mac_address(),0)
topology1.add_device_device(D0)  #0

D1 = devices(topology1.td,create_mac_address(),0)
topology1.add_device_device(D1)  #1


D2 = devices(topology1.td,create_mac_address(),1)
topology1.add_device_device(D2)  #2


D3 = devices(topology1.td,create_mac_address(),1)
topology1.add_device_device(D3)  #3


D4 = devices(topology1.td,create_mac_address(),2)
topology1.add_device_device(D4)  #4


D5 = devices(topology1.td,create_mac_address(),2)
topology1.add_device_device(D5)  #5

topology1.add_device_hub(hub_device(topology1.td, 0))  #6
topology1.add_device_hub(hub_device(topology1.td, 1))  #7
topology1.add_device_hub(hub_device(topology1.td, 2))  #8

S1 = Switch(topology1.td,create_mac_address(),[0,1,2])
topology1.add_device_switch(S1)   #9

token_gen = threading.Thread(target=get_token, args=(topology1.num_devices,))
token_gen.start()

#making connections betweeen the  devs
topology1.make_connection_between(7, 2)
topology1.make_connection_between(3, 7)
topology1.make_connection_between(1, 6)
topology1.make_connection_between(0, 6)
topology1.make_connection_between(4,8)
topology1.make_connection_between(5,8)

#switching the switch
topology1.make_connection_between(6,9)
topology1.make_connection_between(7,9)
topology1.make_connection_between(9,8)

topology1.stop_and_wait(D2,D4,"UwU OwO >w< wakuwak")





