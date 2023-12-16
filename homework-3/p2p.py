import socket
import multiprocessing as mp
import time
import threading
import random
import numpy as np
import re

class P2PNode:
    def __init__(self, identifier, port, peer_addresses, size):
        self.identifier = identifier
        self.port = port
        self.peer_addresses = peer_addresses  
        self.connections = 0 
        self.N = size
        self.received_messages = np.zeros(size)
        self.ready = False
        
    def ready_to_terminate(self):
        #when having received more than 2/3*N messages from each other peer, the peer is ready to terminate
        rdy = True
        for i, v in enumerate(self.received_messages):
            if (i+1)!=self.identifier:
                rdy = rdy and (v > (2/3) * self.N)
        return rdy
     
    def handle_client(self, conn, addr):
        print('Connected with', addr)
        while True:
            if self.ready_to_terminate():
                break
            data = conn.recv(1024)
            if not data:
                break
            if data.decode()=="TERMINATE":
                self.ready = True
                break
            print(f"Server {self.identifier}: {data.decode()}")
            if bool(re.fullmatch(r"Peer \d+ is connected with \d+ other nodes", data.decode())):
                match = re.search(r"Peer (\d+) is connected with \d+ other nodes", data.decode())
                self.received_messages[int(match.group(1)) - 1] += 1
        print(f"{self.identifier} is shutted down!!!")
        conn.close()
        
    def server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.port))
            s.listen()
            print(f"Server {self.identifier} listening on port {self.port}")
            
            # create separate connection with each peer
            for it in range(1,self.N):
                conn, addr = s.accept()
                client_thread = threading.Thread(target=self.handle_client, args= (conn, addr))
                client_thread.start()

    def client(self, port, server_id):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(('localhost', port))
                self.connections += 1
                s.sendall(f"Connection Established to Peer {self.identifier}".encode())
                while True:                    
                    time.sleep(random.uniform(2.0, 3.0))
                    if self.ready_to_terminate() or self.ready:
                        s.sendall(f"TERMINATE".encode())
                        break
                    if self.connections > (self.N/2):
                        s.sendall(f"Peer {self.identifier} is connected with {self.connections} other nodes".encode())
            except ConnectionRefusedError:
                print(f"Could not connect to peer on port {port}")
            except BrokenPipeError:
                print(f"{self.identifier} can't send message.")
            finally:
                s.close()
        
    def run(self):
        server_thread = threading.Thread(target=self.server)
        server_thread.start()
        
        time.sleep(1)
        for i, po in self.peer_addresses.items():
            if i!=self.identifier:
                print(f"{self.identifier}:try to connect with {i}")
                client_thread = threading.Thread(target=self.client, args=(po, i))
                client_thread.start()
        
if __name__ == '__main__':
    K = 10
    
    starting_port = 1030
    peer_addresses = {}
    
    for i in range(1,K+1):
        peer_addresses[i] = starting_port+(i-1)
    
    print(peer_addresses)
    
    nodes = []
    for i in range(1,K+1):
        nodes.append(P2PNode(i, starting_port+(i-1), peer_addresses, K))
    
    processes = []
    for node in nodes:
        processes.append(mp.Process(target=node.run))
    
    for p in processes:
        p.start()
        
    for p in processes:
        p.join()
        
    
    # peer_addresses = {1:1027, 2:1028, 3:1029}
    # node1 = P2PNode(1, 1027, peer_addresses, 3)
    # node2 = P2PNode(2, 1028, peer_addresses, 3)
    # node3 = P2PNode(3, 1029, peer_addresses, 3)
    
    # p1 = mp.Process(target=node1.run)
    # p2 = mp.Process(target=node2.run)
    # p3 = mp.Process(target=node3.run)
    
    # p1.start()
    # p2.start()
    # p3.start()
    
    # p1.join()
    # p2.join()
    # p3.join()