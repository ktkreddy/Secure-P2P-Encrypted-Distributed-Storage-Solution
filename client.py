import sys
import Pyro4 as pyro

sys.excepthook = pyro.util.excepthook


class Client:
    def __init__(self):
        self.MASTER_IP = "10.200.5.26"
        self.MASTER_PORT = 9096
        self.MYIP = "10.200.151.152"
        self.MYPORT = 9097
        self.master_server = None
        self.master_server_prefix = "master.server"
        self.peer_sever_prefix = "peer.server"

    def get_remote_object(self, ip, prefix_text):
        objs = []
        with pyro.locateNS(host=ip) as ns:
            for obj, obj_uri in ns.list(prefix=prefix_text).items():
                print("found ", prefix_text, obj)
                objs.append(pyro.Proxy(obj_uri))
        return objs[0]

    def create(self, name):
        peer_ips = self.master_server.create(name, self.MYIP)
        for peer_ip in peer_ips:
            peer = self.get_remote_object(peer_ip, self.peer_sever_prefix)
            peer.create(name)
        print("Successfully created the file")

    def read(self, name):
        res = self.master_server.read(name, self.MYIP)
        if res == "file doesn't exist" or \
                res == "you do not have read permission":
            print(res)
            return

        peer = self.get_remote_object(res, self.peer_sever_prefix)
        res = peer.read(name, self.MYIP)
        if res == "file doesn't exist":
            print(res)
            return res

        print("Below is the file data for", name)
        print(res)

    def write(self, name, data):
        res = self.master_server.write(name, self.MYIP)
        if res == "file doesn't exist" or \
                res == "you do not have write permission":
            print(res)
            return
        for peer_ip in res:
            peer = self.get_remote_object(peer_ip, self.peer_sever_prefix)
            peer.write(name, data)

        print("Successfully written to the", name)

    def delete(self, name):
        res = self.master_server.delete(name, self.MYIP)
        if res == "file doesn't exist" or \
                res == "you do not have delete/restore permission":
            print(res)
            return
        print("File successfully deleted")

    def restore(self, name):
        res = self.master_server.restore(name, self.MYIP)
        if res == "file doesn't exist" or \
                res == "you do not have delete/restore permission":
            print(res)
            return
        print("File successfully restored")

    def start(self):
        self.master_server = self.get_remote_object(self.MASTER_IP, self.master_server_prefix)
        username = input("Enter your username")
        password = input("Enter your password")
        if self.master_server.validate_user(username, password):
            print("Successfully authorized", username)
        else:
            print(username, " is not authorized")
            exit(0)
        # if self.master_server.register(self.MYIP):
        #     print(username, "Successfully register with", self.MYIP)

        while True:
            choice = input("Enter your Choice:\n1.create 2.read 3.write\n4.delete 5.restore 0.exit")
            if choice == "create":
                name = input("Enter name of the file to be created")
                self.create(name)
            elif choice == "read":
                name = input("Enter name of the file to be read")
                self.read(name)
            elif choice == "write":
                name = input("Enter name of the file to be write")
                data = input("Enter data to be entered into the file")
                self.write(name, data)
            elif choice == "delete":
                name = input("Enter name of the file to be write")
                self.delete(name)
            elif choice == "restore":
                name = input("Enter name of the file to be write")
                self.restore(name)
            elif choice == "exit":
                print("exiting out of file distributed system")
                exit(0)


if __name__ == "_main_":
    client = Client()
    client.start()