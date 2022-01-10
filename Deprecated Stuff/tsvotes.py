from threading import Thread, Event
from queue import Queue, Empty
import time
import os

SENTINEL = object()

def follow(thefile):
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line  # litteraly no idea how it work, just does

class PromptManager(Thread):



    def __init__(self, timeout):
        super().__init__()
        self.timeout = timeout
        self._in_queue = Queue()
        self._out_queue = Queue()
        self.prompter = Thread(target=self._prompter, daemon=True)
        self.start_time = None
        self._prompter_exit = Event()  # synchronization for shutdown
        self._echoed = Event()  # synchronization for terminal output


    def run(self):
        """Run in worker-thread. Start prompt-thread, fetch passed
        inputs from in_queue and check for timeout. Forward inputs for
        `_poll` in parent. If timeout occurs, enqueue SENTINEL to
        break the for-loop in `_poll()`.
        """
        self.start_time = time.time()
        self.prompter.start()

        while self.time_left > 0:
            try:
                txt = self._in_queue.get(timeout=self.time_left)
            except Empty:
                self._out_queue.put(SENTINEL)
            else:
                self._out_queue.put(txt)
        print("\nTime is out! Goodbye!") #put done(or !) next to ! and itll send on last breakout

        os._exit(0)
        self._prompter_exit.wait()

    @property
    def time_left(self):
        return self.timeout - (time.time() - self.start_time)

    def start(self):
        """Start manager-thread."""
        super().start()
        self._poll()

    def _prompter(self):
        """Prompting target function for execution in prompter-thread."""
        logfile = open(
            "C:/Users/Administrator/AppData/Roaming/TS3Client/chats/WmxNa0xndW9OMG9vRC9KZmxjZTNxR1dkbzRrPQ==/channel.txt", "r")
        loglines = follow(logfile)

        while self.time_left > 0:
            for line in loglines:
                self._in_queue.put(line)
                self._echoed.wait()  # prevent intermixed display
                self._echoed.clear()

        self._prompter_exit.set()

    def _poll(self):
        """Get forwarded inputs from the manager-thread executing `run()`
        and process them in the parent-thread.
        """
        for msg in iter(self._out_queue.get, SENTINEL):
            print(f'Someone said: {msg}')
            f = open("votes.txt", "a+")
            f.write(msg) #writes input to text file for later use
            f.close()
            self._echoed.set()
        # finalize
        self._echoed.set()
        self._prompter_exit.wait()
        self.join()


if __name__ == '__main__':
    print('GO')
    try:
        os.remove("votes.txt")
    except:
        f = open("votes.txt", "a+")
        f.close()
    pm = PromptManager(timeout=15)
    pm.start()


