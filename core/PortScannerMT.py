from __future__ import print_function
import socket
import sys
import threading
import Queue


class ScannerThread(threading.Thread):
    def __init__(self, inq, outq):
        threading.Thread.__init__(self)
        # queues for (host, port)
        self.setDaemon(True)
        self.inq = inq
        self.outq = outq
        self.killed = False

    def run(self):
        while not self.killed:
            host, port = self.inq.get()
            sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # connect to the given host:port
                sd.connect((host, port))
            except socket.error:
                # set the CLOSED flag
                self.outq.put((host, port, 'CLOSED'))
            else:
                self.outq.put((host, port, 'OPEN'))
                sd.close()


class Scanner:
    def __init__(self, from_port, to_port, host='localhost'):
        """
        Used for scanning ports
        @param from_port(int): Beginning to scan from this port
        @param to_port(int): Ending scan with this port
        @param host(string): Host address
        """
        self.from_port = from_port
        self.to_port = to_port
        self.host = host
        self.scanners = []
        self.resp = []

    def scan(self, search_for='opened',first_match=False, nthreads=1, send_fn=None):
        """
        @param search_for(string): Search for 'opened', 'closed' or 'all' ports
        @param first_match(bool): If True returns only first scan result and stoping scanning
        @param nthreads(int): Number of threads
        @param send_fn(function): Callback to send results data
        @return(list): list of tuples(host, port, status)
        """
        self.resp = []
        if self.from_port>self.to_port:
            print ("'from port' must be smaller than 'to port'")
            return
        toscan = Queue.Queue()
        scanned = Queue.Queue()

        self.scanners = [ScannerThread(toscan, scanned) for i in range(nthreads)]
        for scanner in self.scanners:
            scanner.start()

        hostports = [(self.host, port) for port in xrange(self.from_port, self.to_port+1)]
        for hostport in hostports:
            toscan.put(hostport)

        results = {}
        for host, port in hostports:
            while (host, port) not in results:
                nhost, nport, nstatus = scanned.get()
                results[(nhost, nport)] = nstatus
            status = results[(host, port)]
            value = (host, port, status)
            if status == 'OPEN' and search_for.lower() == 'opened':
                self.resp.append(value)
                if send_fn:
                    send_fn(value)
                if first_match:
                    return self._finish_scan()
                continue
            elif status == 'CLOSED' and search_for.lower() == 'closed':
                self.resp.append(value)
                if send_fn:
                    send_fn(value)
                if first_match:
                    return self._finish_scan()
            elif search_for.lower() == 'all':
                self.resp.append(value)
                if send_fn:
                    send_fn(value)
                if first_match:
                    return self._finish_scan()
        return self._finish_scan()

    def _finish_scan(self):
        for scanner in self.scanners:
            scanner.join(0.001)
            scanner.killed = True
        return self.resp

if __name__ == '__main__':
    callback = lambda x: print(x)
    scanner = Scanner(5000, 6000, "localhost")
    scanner.scan(search_for='closed', first_match=False, nthreads=100, send_fn=callback)
