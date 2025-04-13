import threading
import time
import random

NUM_TELLERS = 3
NUM_CUSTOMERS = 50

# Semaphores and Locks
bank_open = threading.Event()
safe_sem = threading.Semaphore(2)
manager_sem = threading.Semaphore(1)
door_sem = threading.Semaphore(2)

# Queue management
queue_lock = threading.Lock()
ready_tellers = []
waiting_customers = []

# Communication dicts
customer_semaphores = {}
teller_semaphores = {}
customer_transactions = {}

print_lock = threading.Lock()
def log(msg):
    with print_lock:
        print(msg)

class Teller(threading.Thread):
    def __init__(self, tid):
        super().__init__()
        self.tid = tid
        self.serving = None

    def run(self):
        log(f"Teller {self.tid} []: ready to serve")
        bank_open.wait()

        while True:
            with queue_lock:
                if len(waiting_customers) == 0:
                    ready_tellers.append(self)
                    log(f"Teller {self.tid} []: waiting for a customer")

            cust_sem = threading.Semaphore(0)
            teller_semaphores[self.tid] = cust_sem
            cust_sem.acquire()

            customer = self.serving
            if customer is None:
                break

            log(f"Teller {self.tid} [Customer {customer}]: serving a customer")
            log(f"Teller {self.tid} [Customer {customer}]: asks for transaction")

            cust_ready = customer_semaphores[customer]
            cust_ready.release()
            cust_ready.acquire()

            transaction = customer_transactions[customer]
            log(f"Teller {self.tid} [Customer {customer}]: handling {transaction} transaction")

            if transaction == "withdrawal":
                log(f"Teller {self.tid} [Customer {customer}]: going to the manager")
                manager_sem.acquire()
                log(f"Teller {self.tid} [Customer {customer}]: getting manager's permission")
                time.sleep(random.uniform(0.005, 0.03))
                manager_sem.release()

            log(f"Teller {self.tid} [Customer {customer}]: going to safe")
            safe_sem.acquire()
            log(f"Teller {self.tid} [Customer {customer}]: enter safe")
            time.sleep(random.uniform(0.01, 0.05))
            safe_sem.release()

            log(f"Teller {self.tid} [Customer {customer}]: leaving safe")
            log(f"Teller {self.tid} [Customer {customer}]: finishes {transaction} transaction.")
            log(f"Teller {self.tid} [Customer {customer}]: wait for customer to leave.")

            cust_ready.release()
            cust_ready.acquire()

            self.serving = None

        log(f"Teller {self.tid} []: leaving for the day")

class Customer(threading.Thread):
    def __init__(self, cid):
        super().__init__()
        self.cid = cid
        self.transaction = random.choice(["deposit", "withdrawal"])

    def run(self):
        log(f"Customer {self.cid} []: wants to perform a {self.transaction} transaction")
        time.sleep(random.uniform(0, 0.1))

        door_sem.acquire()
        log(f"Customer {self.cid} []: going to bank.")
        log(f"Customer {self.cid} []: entering bank.")
        log(f"Customer {self.cid} []: getting in line.")

        selected_teller = None
        while selected_teller is None:
            with queue_lock:
                if ready_tellers:
                    selected_teller = ready_tellers.pop(0)
                    selected_teller.serving = self.cid

        log(f"Customer {self.cid} []: selecting a teller.")
        log(f"Customer {self.cid} [Teller {selected_teller.tid}]: selects teller")
        log(f"Customer {self.cid} [Teller {selected_teller.tid}] introduces itself")

        customer_semaphores[self.cid] = threading.Semaphore(0)
        customer_transactions[self.cid] = self.transaction

        teller_semaphores[selected_teller.tid].release()

        customer_semaphores[self.cid].acquire()
        log(f"Customer {self.cid} [Teller {selected_teller.tid}]: asks for {self.transaction} transaction")
        customer_semaphores[self.cid].release()

        customer_semaphores[self.cid].acquire()
        log(f"Customer {self.cid} [Teller {selected_teller.tid}]: leaves teller")
        log(f"Customer {self.cid} []: goes to door")
        log(f"Customer {self.cid} []: leaves the bank")
        customer_semaphores[self.cid].release()
        door_sem.release()

if __name__ == '__main__':
    tellers = [Teller(i) for i in range(NUM_TELLERS)]
    customers = [Customer(i) for i in range(NUM_CUSTOMERS)]

    for t in tellers:
        t.start()

    bank_open.set()

    for c in customers:
        c.start()

    for c in customers:
        c.join()

    for t in tellers:
        t.serving = None
        teller_semaphores[t.tid].release()

    for t in tellers:
        t.join()

    log("The bank closes for the day.")
