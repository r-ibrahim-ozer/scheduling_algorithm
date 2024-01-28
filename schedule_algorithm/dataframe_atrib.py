from datetime import timedelta
import pandas as pd

class DataFrameAttributes():
    def __init__(self, df):
        self.df = df
        self.weights = df['Miktar'].tolist()
        self.color = df['Renk'].tolist()
        self.component_count = df['component_count'].tolist()
        self.length = len(df)
        self.disp_start_time = timedelta(seconds=0)
        self.disp_end_time = timedelta(seconds=0)
        self.mix_end_time = timedelta(seconds=0)
        self.pack_start_time = timedelta(seconds=0)
        self.pack_end_time = timedelta(seconds=0)
        self.df_len = len(df)
        self.tardy = 0