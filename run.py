from server.Server import Server
# from daemonize import Daemonize

pid = "/tmp/app.pid"


def main():
    server = Server()
    server.app()


if __name__ == "__main__":
    main()
    # daemon = Daemonize(app="notice", pid=pid, action=main, user="dima", group="dima")
    # daemon.start()
