"""
Author: <Joseane Maria da Silva>
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket
import threading
import sqlite3
import os
import platform
import datetime


# TODO: Print Python version and OS name (Step iii)
print("Python Version:", platform.python_version())
print("Operating System:", os.uname().sysname)


# TODO: Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}

# TODO: Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"
class NetworkTool:
    def __init__(self, target):
        self.__target = target
    
    @property
    def target(self):
        return self.__target
    
    @target.setter
    def target(self, target):
        if not target:
            print("Error: Target cannot be empty")
            raise Exception("Empty Target")
        self.__target = target

    def __del__(self):
        print("NetworkTool instance destroyed")


# Q3: What is the benefit of using @property and @target.setter?
# TODO: Your 2-4 sentence answer here... (Part 2, Q3)
# The use of @property and @target.setters permits access to hidden, or private attributes, making them possible to be accessed or managed. It allows for adding more complex code into the getter/setter, such as validation or queries.


# Q1: How does PortScanner reuse code from NetworkTool?
# TODO: Your 2-4 sentence answer here... (Part 2, Q1)
# Defining a parent class, NetworkTool, allows to implement a constructor, property getters and setters to be inherited by child classes, PortScanner. This approach of defining the properties in a parent class helps to avoid code repetition in the child class. 



# TODO: Create the PortScanner child class that inherits from NetworkTool (Step vi)
# - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
# - Destructor: print "PortScanner instance destroyed", call super().__del__()
class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
    
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print("PortScanner instance destroyed")
        super.__del__()


    def scan_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            status = "Open" if result == 0 else "Closed"
            service_name = common_ports.get(port, "Unknown")
            
            with self.lock:
                self.scan_results.append((port, status, service_name))

        except socket.error as error:
            print(f"Error scanning port {port}: {error.message}")
        finally:
            sock.close()


    def get_open_ports(self):
        return [result for result in self.scan_results if result[1] == "Open"]
    
    def scan_range(self, start_port, end_port):
        threads = []
        for port in range(start_port, end_port+1):
            t = threading.Thread(self.scan_port, arg=(port,))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

# - scan_port(self, port):
#     Q4: What would happen without try-except here?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q4)
#
#     - try-except with socket operations
#     - Create socket, set timeout, connect_ex
#     - Determine Open/Closed status
#     - Look up service name from common_ports (use "Unknown" if not found)
#     - Acquire lock, append (port, status, service_name) tuple, release lock
#     - Close socket in finally block
#     - Catch socket.error, print error message
#
# - get_open_ports(self):
#     - Use list comprehension to return only "Open" results
#
#     Q2: Why do we use threading instead of scanning one port at a time?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q2)
#
# - scan_range(self, start_port, end_port):
#     - Create threads list
#     - Create Thread for each port targeting scan_port
#     - Start all threads (one loop)
#     - Join all threads (separate loop)


# TODO: Create save_results(target, results) function (Step vii)
# - Connect to scan_history.db
# - CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
# - INSERT each result with datetime.datetime.now()
# - Commit, close
# - Wrap in try-except for sqlite3.Error

def save_results(target, results):
    try:
        connection = sqlite3.connect("scan_history.db")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS scan_history(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       target TEXT,
                       port INTEGER,
                       status TEXT,
                       service TEXT,
                       scan_date TEXT )""")
        
        for result in results:
            cursor.execute("INSERT INTO scan_history (target, port, status, service, scan_date) VALUES(?,?,?,?,?)", (target, result[0], result[1], result[2], str(datetime.datetime.now())))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()


# TODO: Create load_past_scans() function (Step viii)
# - Connect to scan_history.db
# - SELECT all from scans
# - Print each row in readable format
# - Handle missing table/db: print "No past scans found."
# - Close connection
# "[2026-03-15 14:30:00] 127.0.0.1 : Port 22 (SSH) - Open"
def load_past_scans():
    connection = sqlite3.connect("scan_history.db")
    cursor = connection.cursor()
    cursor.execute(
        "SELECT target, port, status, service, scan_date FROM scan_history"
    )
    scans = cursor.fetchall()
    for row in scans:
        print(f"[{row[4]}] {row[0]} : Port {row[1]} ({row[3]}) - {row[2]}")

    if len(scans) == 0:
        print("No past scan found.")
    connection.close()
    
# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    pass
    # TODO: Get user input with try-except (Step ix)
    # - Target IP (default "127.0.0.1" if empty)
    # - Start port (1-1024)
    # - End port (1-1024, >= start port)
    # - Catch ValueError: "Invalid input. Please enter a valid integer."
    # - Range check: "Port must be between 1 and 1024."
        

    # TODO: After valid input (Step x)
    # - Create PortScanner object
    # - Print "Scanning {target} from port {start} to {end}..."
    # - Call scan_range()
    # - Call get_open_ports() and print results
    # - Print total open ports found
    # - Call save_results()
    # - Ask "Would you like to see past scan history? (yes/no): "
    # - If "yes", call load_past_scans()




# Q5: New Feature Proposal
# TODO: Your 2-3 sentence description here... (Part 2, Q5)
# Diagram: See diagram_studentID.png in the repository root
