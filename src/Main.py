import rpyc

class Connection(object):

    def __init__(self):
        self.conn = rpyc.connect("localhost", port=1)
        self.root = self.conn.root



if __name__ == "__main__":

    conn = Connection().conn