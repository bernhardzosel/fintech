import secrets
import string
import hashlib
import pickle
import numpy as np
import time

def create_payload(size):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(size))


def create_hash(obj):
    serialized_obj = pickle.dumps(obj)
    return hashlib.sha256(serialized_obj).hexdigest()

class Block:
    def __init__(self, i, payload, p) -> None:
        self.i = i
        self.payload = payload
        self.nonce = 0
        self.p = p
        self.h = None
    
    def set_hash(self, K):
        while True:
            current_hash = create_hash([self.i, self.payload, self.nonce, self.p])
            if current_hash.startswith("0"*K):
                self.h = current_hash
                break
            self.nonce += 1


for K in [4,5]:
    blocks = []
    sha_calls = []

    blocks.append(Block(0, create_payload(size=64), 0))

    start_time = time.time()
    for i in range(1, 1000):
        previous_block = blocks[i-1]
        new_block = Block(i, create_payload(size=64), previous_block.h)
        new_block.set_hash(K)
        blocks.append(new_block)
        sha_calls.append(new_block.nonce+1)
    print(f"Elapsed time for K={K}: {time.time()-start_time:.2f} seconds")

    print(f"Aggregate number of SHA-256 calls: {np.sum(sha_calls)}")
    print(f"Average number of SHA-256 calls: {np.mean(sha_calls):.2f}")
    print(f"Max number of SHA-256 calls: {np.max(sha_calls)}")
    print(f"Min number of SHA-256 calls: {np.min(sha_calls)}")



    #for b in blocks[0:10]:
    #    print(f"{b.i}: nonce={b.nonce}, hash={b.h}, previous={b.p}")