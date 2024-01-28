from datetime import timedelta
import numpy as np
import random
import pandas as pd
from dataframe_atrib import DataFrameAttributes

class Machines():
    def __init__(self,start_datetime, df_0, df_1):
        self.time = start_datetime
        self.mix_time = timedelta(minutes=15)
        self.disp_setup_time = timedelta(minutes=2)
        self.bucket_capacity = 20
        # df_0 is the longer dataframe / df_1 is the shorter dataframe
        # if its change the code will be change back
        self.df_sort_changed = False

        self.df_0 = DataFrameAttributes(df_0)
        self.df_1 = DataFrameAttributes(df_1)

        
        self.df_0.disp_start_time = start_datetime
        self.df_1.disp_start_time = start_datetime

        self.df_dict = {
            0 : self.df_0,
            1 : self.df_1
        }

        self.pot_time_dict = {
            0: [self.time , self.time, self.time, self.time ],
            1: [self.time , self.time, self.time, self.time ],
            2: [self.time , self.time, self.time, self.time ],
            3: [self.time , self.time, self.time, self.time ]
        }

        self.avg_of_bucket_fnsh_time = timedelta(seconds=52)
        self.color_table = {
                    "sari": {
                        "sari": timedelta(seconds=26),
                        "turuncu": timedelta(minutes=1, seconds=9),
                        "kirmizi": timedelta(minutes=1, seconds=9),
                        "mor": timedelta(minutes=1, seconds=9),
                        "mavi": timedelta(minutes=2, seconds=4),
                        "yesil": timedelta(minutes=1, seconds=9),
                        "kahverengi": timedelta(minutes=1, seconds=9),
                        "siyah": timedelta(minutes=1, seconds=9)
                    },
                    "turuncu": {
                        "sari": timedelta(minutes=6, seconds=58),
                        "turuncu": timedelta(seconds=38),
                        "kirmizi": timedelta(minutes=1, seconds=9),
                        "mor": timedelta(minutes=1, seconds=9),
                        "mavi": timedelta(minutes=1, seconds=9),
                        "yesil": timedelta(minutes=1, seconds=9),
                        "kahverengi": timedelta(minutes=1, seconds=9),
                        "siyah": timedelta(minutes=1, seconds=9)
                    },
                    "kirmizi": {
                        "sari": timedelta(minutes=6, seconds=58),
                        "turuncu": timedelta(minutes=6, seconds=58),
                        "kirmizi": timedelta(minutes=1, seconds=31),
                        "mor": timedelta(minutes=1, seconds=9),
                        "mavi": timedelta(minutes=2, seconds=2),
                        "yesil": timedelta(minutes=1, seconds=9),
                        "kahverengi": timedelta(minutes=1, seconds=9),
                        "siyah": timedelta(minutes=1, seconds=9)
                    },
                    "mor": {
                        "sari": timedelta(minutes=6, seconds=58),
                        "turuncu": timedelta(minutes=6, seconds=58),
                        "kirmizi": timedelta(minutes=6, seconds=58),
                        "mor": timedelta(seconds=38),
                        "mavi": timedelta(seconds=40),
                        "yesil": timedelta(minutes=1, seconds=9),
                        "kahverengi": timedelta(minutes=1, seconds=9),
                        "siyah": timedelta(minutes=1, seconds=9)
                    },
                    "mavi": {
                        "sari": timedelta(minutes=11, seconds=21),
                        "turuncu": timedelta(minutes=6, seconds=58),
                        "kirmizi": timedelta(minutes=6, seconds=58),
                        "mor": timedelta(minutes=6, seconds=58),
                        "mavi": timedelta(seconds=41),
                        "yesil": timedelta(minutes=1, seconds=9),
                        "kahverengi": timedelta(minutes=1, seconds=9),
                        "siyah": timedelta(seconds=58)
                    },
                    "yesil": {
                        "sari": timedelta(minutes=6, seconds=58),
                        "turuncu": timedelta(minutes=6, seconds=58),
                        "kirmizi": timedelta(minutes=6, seconds=58),
                        "mor": timedelta(minutes=6, seconds=58),
                        "mavi": timedelta(minutes=6, seconds=58),
                        "yesil": timedelta(seconds=38),
                        "kahverengi": timedelta(minutes=1, seconds=9),
                        "siyah": timedelta(minutes=1, seconds=9)
                    },
                    "kahverengi": {
                        "sari": timedelta(minutes=6, seconds=58),
                        "turuncu": timedelta(minutes=6, seconds=58),
                        "kirmizi": timedelta(minutes=6, seconds=58),
                        "mor": timedelta(minutes=6, seconds=58),
                        "mavi": timedelta(minutes=6, seconds=58),
                        "yesil": timedelta(minutes=6, seconds=58),
                        "kahverengi": timedelta(seconds=38),
                        "siyah": timedelta(minutes=1, seconds=9)
                    },
                    "siyah": {
                        "sari": timedelta(minutes=6, seconds=58),
                        "turuncu": timedelta(minutes=6, seconds=58),
                        "kirmizi": timedelta(minutes=6, seconds=58),
                        "mor": timedelta(minutes=9, seconds=20),
                        "mavi": timedelta(minutes=6, seconds=58),
                        "yesil": timedelta(minutes=7, seconds=12),
                        "kahverengi": timedelta(minutes=6, seconds=58),
                        "siyah": timedelta(seconds=30)
                    }
                }
        
    def bucket_filling_time(self , weight):
        packaging_time = self.avg_of_bucket_fnsh_time * (weight // self.bucket_capacity)
        return packaging_time
    
    def disp_fillig_time(self, weight, additive_count):
        if 20 <= weight <= 99:
            kg_time_result = timedelta(minutes=5, seconds=58) if additive_count <= 4 else timedelta(minutes=11, seconds=3)
        elif 100 <= weight <= 480:
            kg_time_result = timedelta(minutes=8, seconds=6) if additive_count <= 4 else timedelta(minutes=22, seconds=30)
        else :
            kg_time_result = timedelta(minutes=17, seconds=21) if additive_count <= 4 else timedelta(minutes=23, seconds=52)
            
        return kg_time_result

    def update_avaliable_pot_time(self, avb_time, pot_number):
        self.pot_time_dict[pot_number].pop(0)
        self.pot_time_dict[pot_number].insert(3, avb_time)

    def calculate_delta(self, i, machine_no):
        eks = ((self.df_dict[machine_no].df.at[i,"kamyon/satis"] - self.df_dict[machine_no].df.at[i,"pack_end_time"]).total_seconds() // -3600)
        if eks > 16:
            temp_tardy = (eks // 16) + 1
        elif eks <= 16 and eks >=0 :
            temp_tardy = 1
        else : 
            temp_tardy = 0
        self.df_dict[machine_no].tardy += temp_tardy
        self.df_dict[machine_no].df.at[i,"delta"] = temp_tardy


    def create_nan_columns(self, machine_no):
        self.df_dict[machine_no].df.reset_index(drop=True)
        self.df_dict[machine_no].df["disp_start_time"] = pd.NaT
        self.df_dict[machine_no].df["disp_delta"] = np.nan
        self.df_dict[machine_no].df["disp_end_time"] = pd.NaT
        self.df_dict[machine_no].df["pack_wait"] = np.nan
        self.df_dict[machine_no].df["washing_time"] = timedelta(minutes=0).total_seconds() / 60
        self.df_dict[machine_no].df["pack_start_time"] = pd.NaT
        self.df_dict[machine_no].df["pack_delta"] = timedelta(minutes=0).total_seconds() / 60
        self.df_dict[machine_no].df["pack_end_time"] = pd.NaT
        self.df_dict[machine_no].df["idle_pack_time"] = timedelta(minutes=0).total_seconds() / 60
        self.df_dict[machine_no].df["delta"] = np.nan
    
    def calc_df_columns(self):
        self.create_nan_columns(0)
        self.create_nan_columns(1)

        # ----------machine_0[0] ---------
        kg_time_result_0 = self.disp_fillig_time(self.df_0.weights[0], self.df_0.component_count[0])        
        self.df_0.disp_end_time = pd.to_datetime((self.df_0.disp_start_time + kg_time_result_0), format="%d.%m.%Y %H:%M:%S")
        self.df_0.mix_end_time = self.df_0.disp_end_time + self.mix_time
        self.df_0.df.at[0, "disp_end_time"] = self.df_0.mix_end_time
        self.df_0.df.at[0,"disp_start_time"] = self.df_0.disp_start_time
        self.df_0.df.at[0,"disp_delta"] = kg_time_result_0.total_seconds() / 60
        self.df_0.disp_start_time = self.df_0.disp_end_time


        self.df_0.pack_start_time = self.df_0.mix_end_time
        self.df_0.df.at[0,"pack_wait"] = (self.df_0.pack_start_time - self.df_0.mix_end_time).total_seconds() / 60
        self.df_0.df.at[0,"pack_start_time"] = self.df_0.pack_start_time
        self.df_0.df.at[0,"pack_delta"] = (self.bucket_filling_time(self.df_0.weights[0])).total_seconds() / 60
        self.df_0.pack_end_time = pd.to_datetime((self.df_0.pack_start_time + self.bucket_filling_time(self.df_0.weights[0])), format="%d.%m.%Y %H:%M:%S", errors="coerce")
        self.df_0.df.at[0,"pack_end_time"] = self.df_0.pack_end_time
        self.df_0.pack_start_time = self.df_0.pack_end_time

        pot_number = self.df_0.df.at[0,"Kazan"]
        self.pot_time_dict[pot_number][3] = self.df_0.pack_end_time

        self.calculate_delta(0,0)

        # ----------machine_1[0] ---------
        kg_time_result_1 = self.disp_fillig_time(self.df_1.weights[0], self.df_1.component_count[0])        
        self.df_1.disp_end_time = pd.to_datetime((self.df_1.disp_start_time + kg_time_result_1), format="%d.%m.%Y %H:%M:%S")
        self.df_1.mix_end_time = self.df_1.disp_end_time + self.mix_time
        self.df_1.df.at[0,"disp_end_time"] = self.df_1.mix_end_time
        self.df_1.df.at[0,"disp_start_time"] = self.df_1.disp_start_time
        self.df_1.df.at[0,"disp_delta"] = kg_time_result_1.total_seconds() / 60
        self.df_1.disp_start_time = self.df_1.disp_end_time

        self.df_1.pack_start_time = self.df_1.mix_end_time
        self.df_1.df.at[0,"pack_wait"] = (self.df_1.pack_start_time - self.df_1.mix_end_time).total_seconds() / 60
        self.df_1.df.at[0,"pack_start_time"] = self.df_1.pack_start_time
        self.df_1.df.at[0,"pack_delta"] = (self.bucket_filling_time(self.df_1.weights[0])).total_seconds() / 60
        self.df_1.pack_end_time = pd.to_datetime((self.df_1.pack_start_time + self.bucket_filling_time(self.df_1.weights[0])), format="%d.%m.%Y %H:%M:%S", errors="coerce")
        self.df_1.df.at[0,"pack_end_time"] = self.df_1.pack_end_time
        self.df_1.pack_start_time = self.df_1.pack_end_time

        pot_number = self.df_1.df.at[0,"Kazan"]
        self.update_avaliable_pot_time(self.df_1.pack_end_time, pot_number)

        self.calculate_delta(0,1)

        for i in range(1,self.df_0.df_len):
            # ----------machine_0[i] ---------
            # kg_time_calculation
            pot_number = self.df_0.df.at[i,"Kazan"]
            self.df_0.disp_start_time = max(self.df_0.disp_start_time, self.pot_time_dict[pot_number][0])

            kg_time_result = self.disp_fillig_time(self.df_0.weights[i], self.df_0.component_count[i])
            self.df_0.disp_end_time = pd.to_datetime((self.df_0.disp_start_time + kg_time_result), format="%d.%m.%Y %H:%M:%S")
            self.df_0.df.at[i,"disp_start_time"] = self.df_0.disp_start_time
            self.df_0.disp_start_time = self.df_0.disp_end_time
            self.df_0.mix_end_time = self.df_0.disp_end_time + self.mix_time
            self.df_0.df.at[i,"disp_end_time"] = self.df_0.mix_end_time
            self.df_0.df.at[i,"disp_delta"] = kg_time_result.total_seconds() / 60
            
            # packaging_time_calculation
            washing_time = self.color_table[self.df_0.df["Renk"][i-1]][self.df_0.df["Renk"][i]]
            temp_pack_start_time = max(self.df_0.pack_start_time, self.df_0.mix_end_time)
            self.df_0.df.at[i,"pack_start_time"] = temp_pack_start_time
            self.df_0.df.at[i,"pack_wait"] = (self.df_0.pack_start_time - self.df_0.mix_end_time).total_seconds() / 60
            self.df_0.df.at[i,"idle_pack_time"] = (temp_pack_start_time - self.df_0.pack_start_time).total_seconds() / 60
            self.df_0.pack_start_time = pd.to_datetime(temp_pack_start_time, format="%d.%m.%Y %H:%M:%S", errors="coerce")
            self.df_0.df.at[i,"washing_time"] = (washing_time + timedelta(minutes=2)).total_seconds() / 60
            self.df_0.df.at[i,"pack_delta"] = (self.bucket_filling_time(self.df_0.weights[i])).total_seconds() / 60
            self.df_0.pack_end_time = pd.to_datetime(self.df_0.pack_start_time + self.bucket_filling_time(self.df_0.weights[i]) + washing_time + timedelta(minutes=3), format="%d.%m.%Y %H:%M:%S", errors="coerce")
            self.df_0.df.at[i,"pack_end_time"] = self.df_0.pack_end_time
            self.df_0.pack_start_time = self.df_0.pack_end_time

            self.update_avaliable_pot_time(self.df_0.pack_end_time, pot_number)
            self.calculate_delta(i,0)

            if i < self.df_1.df_len:
                # ----------machine_1[i] ---------
                # kg_time_calculation
                pot_number = self.df_1.df.at[i,"Kazan"]
                self.df_1.disp_start_time = max(self.df_1.disp_start_time, self.pot_time_dict[pot_number][0])

                kg_time_result = self.disp_fillig_time(self.df_1.weights[i], self.df_1.component_count[i])
                self.df_1.disp_end_time = pd.to_datetime((self.df_1.disp_start_time + kg_time_result), format="%d.%m.%Y %H:%M:%S")
                self.df_1.df.at[i,"disp_start_time"] = self.df_1.disp_start_time
                self.df_1.disp_start_time = self.df_1.disp_end_time
                self.df_1.mix_end_time = self.df_1.disp_end_time + self.mix_time
                self.df_1.df.at[i,"disp_end_time"] = self.df_1.mix_end_time
                self.df_1.df.at[i,"disp_delta"] = kg_time_result.total_seconds() / 60
                
                # packaging_time_calculation
                washing_time = self.color_table[self.df_1.df["Renk"][i-1]][self.df_1.df["Renk"][i]]
                temp_pack_start_time = max(self.df_1.pack_start_time, self.df_1.mix_end_time)
                self.df_1.df.at[i,"pack_start_time"] = temp_pack_start_time
                self.df_1.df.at[i,"pack_wait"] = (self.df_1.pack_start_time - self.df_1.mix_end_time).total_seconds() / 60
                self.df_1.df.at[i,"idle_pack_time"] = (temp_pack_start_time - self.df_1.pack_start_time).total_seconds() / 60
                self.df_1.pack_start_time = temp_pack_start_time
                self.df_1.df.at[i,"washing_time"] =(washing_time + timedelta(minutes=2)).total_seconds() / 60
                self.df_1.pack_start_time = pd.to_datetime(self.df_1.pack_start_time , format="%d.%m.%Y %H:%M:%S", errors="coerce")
                self.df_1.df.at[i,"pack_delta"] = (self.bucket_filling_time(self.df_1.weights[i])).total_seconds() / 60
                self.df_1.pack_end_time = pd.to_datetime(self.df_1.pack_start_time + self.bucket_filling_time(self.df_1.weights[i])+ washing_time + timedelta(minutes=3), format="%d.%m.%Y %H:%M:%S", errors="coerce")
                self.df_1.df.at[i,"pack_end_time"] = self.df_1.pack_end_time
                self.df_1.pack_start_time = self.df_1.pack_end_time

                self.update_avaliable_pot_time(self.df_1.pack_end_time, pot_number)
                self.calculate_delta(i,1)

        calc_df_0, calc_df_1 = (self.df_1.df, self.df_0.df) if self.df_sort_changed else (self.df_0.df, self.df_1.df)
        
        return calc_df_0, calc_df_1
    
    def est_time(self):

        # ----------machine_0[0] ---------
        kg_time_result_0 = self.disp_fillig_time(self.df_0.weights[0], self.df_0.component_count[0])        
        self.df_0.disp_end_time = pd.to_datetime((self.df_0.disp_start_time + kg_time_result_0), format="%d.%m.%Y %H:%M:%S")
        self.df_0.mix_end_time = self.df_0.disp_end_time + self.mix_time
        self.df_0.disp_start_time = self.df_0.disp_end_time

        self.df_0.pack_start_time = self.df_0.mix_end_time
        self.df_0.pack_end_time = pd.to_datetime((self.df_0.pack_start_time + self.bucket_filling_time(self.df_0.weights[0])), format="%d.%m.%Y %H:%M:%S", errors="coerce")
        self.df_0.pack_start_time = self.df_0.pack_end_time

        # self.df_0.df["idle_pack_time"].iloc[0] = timedelta(minutes=0)

        pot_number = self.df_0.df["Kazan"].iloc[0]
        self.pot_time_dict[pot_number][3] = self.df_0.pack_end_time

        # self.calculate_delta(0,0)

        # ----------machine_1[0] ---------
        kg_time_result_1 = self.disp_fillig_time(self.df_1.weights[0], self.df_1.component_count[0])        
        self.df_1.disp_end_time = pd.to_datetime((self.df_1.disp_start_time + kg_time_result_1), format="%d.%m.%Y %H:%M:%S")
        self.df_1.mix_end_time = self.df_1.disp_end_time + self.mix_time
        self.df_1.disp_start_time = self.df_1.disp_end_time

        self.df_1.pack_start_time = self.df_1.mix_end_time
        self.df_1.pack_end_time = pd.to_datetime((self.df_1.pack_start_time + self.bucket_filling_time(self.df_1.weights[0])), format="%d.%m.%Y %H:%M:%S", errors="coerce")
        self.df_1.pack_start_time = self.df_1.pack_end_time
        # self.df_1.df["idle_pack_time"].iloc[0] = timedelta(minutes=0)

        pot_number = self.df_1.df["Kazan"].iloc[0]
        self.update_avaliable_pot_time(self.df_1.pack_end_time, pot_number)

        # self.calculate_delta(0,1)

        for i in range(1,self.df_0.df_len):
            # ----------machine_0[i] ---------
            # kg_time_calculation
            pot_number = self.df_0.df["Kazan"].iloc[i]
            self.df_0.disp_start_time = max(self.df_0.disp_start_time, self.pot_time_dict[pot_number][0])

            kg_time_result = self.disp_fillig_time(self.df_0.weights[i],self.df_0.component_count[i])
            self.df_0.disp_end_time = pd.to_datetime((self.df_0.disp_start_time + kg_time_result), format="%d.%m.%Y %H:%M:%S")
            self.df_0.disp_start_time = self.df_0.disp_end_time
            self.df_0.mix_end_time = self.df_0.disp_end_time + self.mix_time
            
            # packaging_time_calculation
            washing_time = self.color_table[self.df_0.df["Renk"][i-1]][self.df_0.df["Renk"][i]]
            temp_pack_start_time = max(self.df_0.pack_start_time, self.df_0.mix_end_time)
            # self.df_0.df["idle_pack_time"].iloc[i] = temp_pack_start_time - self.df_0.pack_start_time
            self.df_0.pack_start_time = temp_pack_start_time
            self.df_0.pack_start_time = pd.to_datetime(self.df_0.pack_start_time + washing_time + timedelta(minutes=3), format="%d.%m.%Y %H:%M:%S", errors="coerce")
            self.df_0.pack_end_time = pd.to_datetime(self.df_0.pack_end_time + self.bucket_filling_time(self.df_0.weights[i]), format="%d.%m.%Y %H:%M:%S", errors="coerce")
            self.df_0.pack_start_time = self.df_0.pack_end_time

            self.update_avaliable_pot_time(self.df_0.pack_end_time, pot_number)
            # self.calculate_delta(i,0)

            if i <= self.df_1.df_len:
                # ----------machine_1[i] ---------
                # kg_time_calculation
                pot_number = self.df_1.df["Kazan"].iloc[i]
                self.df_1.disp_start_time = max(self.df_1.disp_start_time, self.pot_time_dict[pot_number][0])

                kg_time_result = self.disp_fillig_time(self.df_1.weights[i],self.df_1.component_count[i])
                self.df_1.disp_end_time = pd.to_datetime((self.df_1.disp_start_time + kg_time_result), format="%d.%m.%Y %H:%M:%S")
                self.df_1.disp_start_time = self.df_1.disp_end_time
                self.df_1.mix_end_time = self.df_1.disp_end_time + self.mix_time
                
                # packaging_time_calculation
                washing_time = self.color_table[self.df_1.df["Renk"][i-1]][self.df_1.df["Renk"][i]]
                temp_pack_start_time = max(self.df_1.pack_start_time, self.df_1.mix_end_time)
                # self.df_1.df["idle_pack_time"].iloc[i] = temp_pack_start_time - self.df_1.pack_start_time
                self.df_1.pack_start_time = temp_pack_start_time
                self.df_1.pack_start_time = pd.to_datetime(self.df_1.pack_start_time + washing_time + timedelta(minutes=3), format="%d.%m.%Y %H:%M:%S", errors="coerce")
                self.df_1.pack_end_time = pd.to_datetime(self.df_1.pack_end_time + self.bucket_filling_time(self.df_1.weights[i]), format="%d.%m.%Y %H:%M:%S", errors="coerce")
                self.df_1.pack_start_time = self.df_1.pack_end_time

                self.update_avaliable_pot_time(self.df_1.pack_end_time, pot_number)
                # self.calculate_delta(i,1)

        calc_df_0, calc_df_1 = (self.df_1.df, self.df_0.df) if self.df_sort_changed else (self.df_0.df, self.df_1.df)
        
        return calc_df_0, calc_df_1