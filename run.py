#!/usr/bin/python

import sys

from lib.daemon import Daemon
from server.Server import Server


class ServerDaemon(Daemon):
    def run(self):
        server = Server()
        server.app()


if __name__ == "__main__":
    daemon = ServerDaemon('/tmp/python-notice-daemon.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.is_running()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
