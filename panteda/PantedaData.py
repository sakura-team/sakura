from utils import *
from db import *

query = "select timestamp, cast(duree as float) from aplusix_brasil_2003logs where duree not like '%-%'"
DEBUG = False

class ServerPantedaDataOperator(ServerPantedaStepByStepOperator):
    OP_TYPE = "OWPantedaData"
    def __init__(self):
        self.cur_desc = DB_CONN.cursor()
        self.cur_main = DB_CONN.cursor()
        self.query_done = False
        
    def ensure_query_done(self):
        if not self.query_done:
            self.cur_main.execute(query)
            self.query_done = True
    
    def describe_outputs(self):
        if DEBUG: ecrire("Data description")
        self.cur_desc.execute(query + " limit 0")
        DATA_COLS = tuple( (r[0], OIDs[r[1]]) for r in self.cur_desc.description)
        return (DATA_COLS,)
    
    def get_output_len(self):
        if DEBUG: ecrire("Data len")
        self.ensure_query_done()
        return self.cur_main.rowcount
    
    def get_result(self, i):
        if DEBUG: ecrire("Data get_r")
        self.ensure_query_done()
        if i < self.cur_main.rowcount:
            self.cur_main.scroll(i, mode='absolute')
            return self.cur_main.fetchone()
        else:
            return None
