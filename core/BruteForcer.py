#!/usr/bin/python

import sys
import os.path
from threading import RLock, Thread

RESOURCE_DIR = "./"


class BruteForcer:
    """
        Class includes a generic threaded brute forcer logic
    """

    def __init__(self):
        self.maxthreads = 5
        self.wordlist = os.path.join(RESOURCE_DIR, "passwords.txt")
        self.wordlist_lock = RLock()
        self.successful_guess = None    # the word that won
        return

    @staticmethod
    def log(host=None, message=""):
        """
            Logger
        """
        if not host:
            host = "127.0.0.1"  # FIXME

        message = "(%s) %s" % (host, message)
        sys.stdout.write("[*] " + str(message) + "\n")

    def get_next_word(self):
        """
        Get the next word in wordlist, we lock since readline may not be atomic.
        This code could go into some sort of auxiliary object that is more abstract later.

        It returns False when it is out of words.
        """

        #if a thread found one, it will set successful_guess
        if self.successful_guess:
            #so we pretend we are done.
            return False

        self.wordlist_lock.acquire()
        try:
            next_word = self.wordlistfd.readline().strip()
        except EOFError:
            self.wordlist_lock.release()
            return False
        self.wordlist_lock.release()
        return next_word

    def brute_loop(self):
        """
        Override this with your connect/check loop.
        Don't forget to check for self.HALT!
        """
        self.log("Stub brute_loop called")
        return

    def run(self):
        if self.wordlist:
            self.wordlistfd = file(self.wordlist, "r")
        mythreads = []

        if self.maxthreads <= 0:
            self.log("Invalid maxthreads value recieved: %d" % self.maxthreads)
            return 0

        self.log("Starting %d threads to brute force with" % self.maxthreads)
        for i in xrange(0, self.maxthreads):
            """
                Start up a new thread for each run. These will call get_next_word as applicable.
            """
            t = Thread(target=self.brute_loop())
            t.setDaemon(True)
            t.start()
            mythreads += [t]

        for a_thread in mythreads:
            a_thread.join()
            self.log("Thread finished")

        if self.successful_guess:
            self.log("Found successful word: %s" % self.successful_guess)
            return 1

        self.log("Exhausted brute force attempts - did not find successful word")
        return 0
