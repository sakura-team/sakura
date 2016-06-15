import rpyc

class PantedaConnection:
    
    instance = None
    
    def connect(self):
        #self.server_conn = rpyc.connect("reglet.local", 12345)
        self.server_conn = rpyc.connect("localhost", 12345)
        self.server = self.server_conn.root
        
    @staticmethod
    def get():
        if PantedaConnection.instance == None:
            PantedaConnection.instance = PantedaConnection()
            PantedaConnection.instance.connect()
        return PantedaConnection.instance.server
