import socket
import multiprocessing as mp
import time
import threading
import random
import numpy as np
import re
import string
import secrets
import hashlib

class P2PNode:
    def __init__(self, identifier, port, peer_addresses, size):
        self.identifier = identifier
        self.port = port
        self.peer_addresses = peer_addresses  
        self.connections = 0 
        self.N = size
        self.received_messages = np.zeros(size)
        self.ready = False
        self.round = 0
        self.acks = {i: np.zeros(size) for i in range(0,100)}
        self.ready_to_ack = [False for x in range(0,100)]
        self.num_commits = {i: 0 for i in range(0,100)}
        self.payload = []
        self.blockchain = ['0']
        self.current_payload = 0
        
    def give_payload(self):
        if len(self.payload)<(self.round//self.N)+1:
            self.payload.append(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64)))
        return self.payload[self.round//self.N]
        
    def enough_acks(self):
        #when having received more than 2/3*N messages from each other peer, the peer is ready to terminate
        acks = 0
        for i, v in enumerate(self.acks[self.round]):
            if i!=self.identifier:
                if v>0:
                    acks+=1
        return acks > (0.5 * self.N)
     
    def handle_client(self, conn, addr):
        print('Connected with', addr)
        while True:
            data = conn.recv(1024)
            if self.round % self.N == self.identifier:
                ## Peer is leader
                if "acknowledges" in data.decode():
                    match = re.search(r"Peer (\d+) acknowledges payload.", data.decode())
                    print(f"Server {self.identifier} receives ACK: {data.decode()}")
                    self.acks[self.round][int(match.group(1))] += 1
            else:
                if data.decode().startswith("Payload"):
                    self.current_payload = data.decode()
                    print(f"Server {self.identifier} receives payload: {data.decode()}")
                    self.ready_to_ack[self.round]=True
                elif data.decode().startswith("COMMIT"):
                    print(f"Server {self.identifier} receives COMMMIT: {data.decode()}")
                    #time.sleep(random.uniform(1.0, 3.0))
                    self.blockchain.append(hashlib.sha256((self.blockchain[self.round - 1] + self.current_payload).encode()).hexdigest())
                    self.round+=1
                
        
    def server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.port))
            s.listen()
            print(f"Server {self.identifier} listening on port {self.port}")
            
            # create separate connection with each peer
            for it in range(0,self.N-1):
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
                    time.sleep(random.uniform(0.2, 0.3))
                    if self.round % self.N == self.identifier:
                        # Peer is leader
                        time.sleep(random.uniform(0.2, 0.3))
                        payload = self.give_payload()
                        self.current_payload = payload
                        s.sendall(f"Payload Round {self.round}: {payload}".encode())  
                        
                        # wait until enough messages have been acknowledged
                        #while self.acks[self.round][0] < self.N / 2:
                        while not self.enough_acks():
                            time.sleep(random.uniform(0.2, 0.3))
                        
                        s.sendall(f"COMMIT round {self.round}".encode())
                        self.num_commits[self.round]+=1
            
                        if self.num_commits[self.round] >= self.N-1:    #increase round after last commit has been sent 
                            self.blockchain.append(hashlib.sha256((self.blockchain[self.round - 1] + self.current_payload).encode()).hexdigest())
                            self.round+=1  
                    else:
                        time.sleep(random.uniform(0.1, 0.2))
                        if self.ready_to_ack[self.round]:
                            # only acknowledge when ready to acknowledge
                            if self.round % self.N == server_id:
                                s.sendall(f"Peer {self.identifier} acknowledges payload.".encode())
                            #self.round+=1

                        
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
                client_thread = threading.Thread(target=self.client, args=(po, i))
                client_thread.start()
        
if __name__ == '__main__':
    K = 4
    
    starting_port = 1024
    peer_addresses = {}
    
    for i in range(0,K):
        peer_addresses[i] = starting_port+i
    
    print(peer_addresses)
    
    nodes = []
    for i in range(0,K):
        nodes.append(P2PNode(i, starting_port+i, peer_addresses, K))
    
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