import random
import time


# A) Basic operations


def mod_inverse(a, n):
    try:
        return pow(a, -1, n)
    except ValueError:
        # Inverse does not exist if a and n are not coprime
        return None
    
for a in [64, 128]: #256, 1024, 4096]:
    start_time = time.time() 
    n = (2**a)-1
    k = 10000
    X = [random.randint(0, n) for _ in range(k)]
    
    # Addition
    s = time.time()
    for i in range(0, len(X)-1):
        X[i]+X[i+1] % n
    print(f"\t +: {time.time() - s} seconds")
        
    # Multiplication
    s = time.time()
    for i in range(0, len(X)-1):
        X[i]*X[i+1] % n
    print(f"\t *: {time.time() - s} seconds")

    #Inverse
    s = time.time()
    inverses = []
    for i in range(0, len(X)):
        inverses.append(mod_inverse(X[i], n))
    print(f"\t 1: {time.time() - s} seconds")
    
    #Division
    s = time.time()
    for i in range(0, len(X)-1):
        if inverses[i+1]!=None:
            (X[i] * inverses[i+1]) % n
    print(f"\t /: {time.time() - s} seconds")

    end_time = time.time() 
    print(f"a={a} => {end_time - start_time} seconds")


# B) Primality testing using the Miller Rabin test

def miller_rabin(n, k):

    # Implementation uses the Miller-Rabin Primality Test
    # The optimal number of rounds for this test is 40
    # See http://stackoverflow.com/questions/6325576/how-many-iterations-of-rabin-miller-should-i-use-for-cryptographic-safe-primes
    # for justification

    # If number is even, it's a composite number

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

for a in [64, 128, 256, 1024, 4096]:
    start_time = time.time() 
    n = (2**a)-1
    count = 0
    i = 0
    while count<5:
        i += 1
        x = random.randint(0,n)
        if miller_rabin(x,5):
            count += 1
            #print("found a prime!")
    print(i)
    end_time = time.time() 
    print(f"a={a} => {end_time - start_time} seconds")
            
        
    