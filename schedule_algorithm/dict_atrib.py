from datetime import timedelta

class DictAttributes():
    def __init__(self, dict):
        self.dict = dict
        self.keys = list(dict.keys())
        self.disp_start_time = timedelta(seconds=0)
        self.disp_end_time = timedelta(seconds=0)
        self.mix_end_time = timedelta(seconds=0)
        self.pack_start_time = timedelta(seconds=0)
        self.pack_end_time = timedelta(seconds=0)
        self.df_len = len(dict)
        self.tardy = 0
        self.makespan = 0