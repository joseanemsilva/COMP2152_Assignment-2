"""
Author: <Joseane Maria da Silva>
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

import socket
import threading
import sqlite3
import os
import platform
import datetime

# Python version and OS name
print("Python Version:", platform.python_version())
print("Operating System:", os.uname().sysname)


# Common_ports dictionary
# The dictionary stores a port number key and its corresponding service name as value.
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

# NetworkTool parent class
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
    """
    The use of @property and @target.setters permits access to hidden, or private attributes, making them possible to be accessed or managed. It allows for adding more complex code into the getter/setter, such as validation or queries.
    """

# Q1: How does PortScanner reuse code from NetworkTool?
    """
    Defining a parent class, NetworkTool, allows to implement a constructor, property getters and setters to be inherited by child classes, PortScanner. This approach of defining the properties in a parent class helps to avoid code repetition in the child class.
    PortScanner uses the super().__init__(target) to initialize the the target property.
    """

# PortScanner child class that inherits from NetworkTool
class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
    
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print("PortScanner instance destroyed")
        super.__del__()

# Q4: What would happen without try-except here?
    """
    If the target can not be resolved, connect_ex would throw a socket.gaierror exception, which would stop execution and leave the socket open.
    """
    def scan_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            status = "Open" if result == 0 else "Closed"
            service_name = common_ports.get(port, "Unknown")
            
            with self.lock:
                self.scan_results.append((port, status, service_name))

        except socket.error as e:
            print(f"Error scanning port {port}: {e.message}")
        finally:
            sock.close()

# Method to get open ports
    def get_open_ports(self):
        return [result for result in self.scan_results if result[1] == "Open"]


# Q2: Why do we use threading instead of scanning one port at a time?
    """
    Threads allows to execute tasks in parallel. Considering that If we had 1024 ports and would executed one at a time, it would be slower.
    """
# Method to scan the range
    def scan_range(self, start_port, end_port):
        threads = []
        for port in range(start_port, end_port+1):
            t = threading.Thread(self.scan_port, arg=(port,))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

# Save results in a sqlite db.
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


# Load past scans saved on sqlite db
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
    try:
        target = input("Enter an IP address: ")
        start_port = int(input("Enter a start port number between 1 to 1024: "))
        end_port = int(input("Enter an ending port number between 1 to 1024, greater than start port: "))
    except ValueError:
        print("Invalid input. Please enter a valid integer.")


    # TODO: After valid input (Step x)
    # - Create PortScanner object
    # - Print "Scanning {target} from port {start} to {end}..."
    # - Call scan_range()
    # - Call get_open_ports() and print results
    # - Print total open ports found
    # - Call save_results()
    # - Ask "Would you like to see past scan history? (yes/no): "
    # - If "yes", call load_past_scans()

    obg = PortScanner(target)
    print(f"Scanning {target} from {start_port} to {end_port}...")

    obg.scan_range(start_port, end_port)
    total = 0
    for port in obg.get_open_ports():
        print(f"Port {port}: Open ({port})")
        total +1
    print("--------\nTotal open ports found:", str(total))

    save_results(target)


# Q5: New Feature Proposal
# TODO: Your 2-3 sentence description here... (Part 2, Q5)
# Diagram: See diagram_studentID.png in the repository root
