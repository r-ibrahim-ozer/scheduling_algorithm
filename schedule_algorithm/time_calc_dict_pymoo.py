from datetime import timedelta
import numpy as np
import pandas as pd
from dict_atrib import DictAttributes

class Machines():
    def __init__(self,start_datetime, dict_0, dict_1):
        self.start_time = start_datetime
        self.time = start_datetime
        self.mix_time = timedelta(minutes=15)
        self.disp_setup_time = timedelta(minutes=2)
        self.bucket_capacity = 20
        self.washing_time_1 = 0
        self.washing_time_2 = 0
        # df_0 is the longer dataframe / df_1 is the shorter dataframe
        # if its change the code will be change back
        self.df_sort_changed = False
        if len(dict_1) <= len(dict_0):
            self.df_0 = DictAttributes(dict_0)
            self.df_1 = DictAttributes(dict_1)
        else:
            self.df_0 = DictAttributes(dict_1)
            self.df_1 = DictAttributes(dict_0)
            self.df_sort_changed = True
        
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
    def clean_pot_time_dict(self):
        self.pot_time_dict = {
            0: [self.time , self.time, self.time, self.time ],
            1: [self.time , self.time, self.time, self.time ],
            2: [self.time , self.time, self.time, self.time ],
            3: [self.time , self.time, self.time, self.time ]
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

   
    def calculate_delta(self, i, machine_no, pack_end_time):
        eks = ((self.df_dict[machine_no].dict[self.df_dict[machine_no].keys[i]]["kamyon/satis"] - pack_end_time).total_seconds() // -3600)
        if eks > 16:
            temp_tardy = (eks // 16) + 1
        elif eks <= 16 and eks >=0 :
            temp_tardy = 1
        else : 
            temp_tardy = 0
        self.df_dict[machine_no].tardy += temp_tardy
    
    def dict_est_time(self,solution):
        self.washing_time_1 = 0
        self.washing_time_2 = 0
        self.clean_pot_time_dict()
        self.df_0.disp_start_time = self.start_time
        self.df_1.disp_start_time = self.start_time
        self.df_0.makespan = 0
        self.df_1.makespan = 0
        self.df_0.tardy = 0
        self.df_1.tardy = 0


        # self.df_1.keys = solution_dict_1
        # solution = list(solution)
        # solution_dict_0 = solution[:len(self.df_0.dict)]
        # solution_dict_1 = solution[len(self.df_0.dict):]
            
        solution_dict_0 = []
        solution_dict_1 = []
        solution = list(solution)

        for i in solution:
            if i < self.df_0.df_len:
                solution_dict_0.append(i)
            else:
                solution_dict_1.append(i)

        self.df_1.keys = solution_dict_1
        self.df_0.keys = solution_dict_0

        # ----------machine_0[0] ---------
        kg_time_result_0 = self.disp_fillig_time(self.df_0.dict[self.df_0.keys[0]]["Miktar"],self.df_0.dict[self.df_0.keys[0]]["component_count"])
        self.df_0.disp_end_time = (self.df_0.disp_start_time + kg_time_result_0 + self.disp_setup_time)
        self.df_0.mix_end_time = self.df_0.disp_end_time + self.mix_time
        self.df_0.disp_start_time = self.df_0.disp_end_time

        self.df_0.pack_start_time = self.df_0.mix_end_time
        self.df_0.pack_end_time = (self.df_0.pack_start_time + self.bucket_filling_time(self.df_0.dict[self.df_0.keys[0]]["Miktar"]))
        self.df_0.pack_start_time = self.df_0.pack_end_time

        pot_number = self.df_0.dict[self.df_0.keys[0]]["Kazan"]
        self.pot_time_dict[pot_number][3] = self.df_0.pack_end_time

        self.calculate_delta(0,0,self.df_0.pack_end_time)

        # ----------machine_1[0] ---------
        kg_time_result_1 = self.disp_fillig_time(self.df_1.dict[self.df_1.keys[0]]["Miktar"],self.df_1.dict[self.df_1.keys[0]]["component_count"])       
        self.df_1.disp_end_time = (self.df_1.disp_start_time + kg_time_result_1 + self.disp_setup_time)
        self.df_1.mix_end_time = self.df_1.disp_end_time + self.mix_time
        self.df_1.disp_start_time = self.df_1.disp_end_time

        self.df_1.pack_start_time = self.df_1.mix_end_time
        self.df_1.pack_end_time = (self.df_1.pack_start_time + self.bucket_filling_time(self.df_1.dict[self.df_1.keys[0]]["Miktar"]))
        self.df_1.pack_start_time = self.df_1.pack_end_time

        pot_number = self.df_1.dict[self.df_1.keys[0]]["Kazan"]
        self.update_avaliable_pot_time(self.df_1.pack_end_time, pot_number)

        self.calculate_delta(0,1, self.df_1.pack_end_time)

        for i in range(1,self.df_0.df_len):
            # ----------machine_0[i] ---------

            pot_number = self.df_0.dict[self.df_0.keys[i]]["Kazan"]
            self.df_0.disp_start_time = max(self.df_0.disp_start_time, self.pot_time_dict[pot_number][0])

            kg_time_result = self.disp_fillig_time(self.df_0.dict[self.df_0.keys[i]]["Miktar"],self.df_0.dict[self.df_0.keys[i]]["component_count"])
            self.df_0.disp_end_time = (self.df_0.disp_start_time + kg_time_result + self.disp_setup_time)
            self.df_0.disp_start_time = self.df_0.disp_end_time
            self.df_0.mix_end_time = self.df_0.disp_end_time + self.mix_time
            
            # packaging_time_calculation
            washing_time = self.color_table[self.df_0.dict[self.df_0.keys[i-1]]["Renk"]][self.df_0.dict[self.df_0.keys[i]]["Renk"]]
            self.washing_time_1 += washing_time.total_seconds()

            temp_pack_start_time = max(self.df_0.pack_start_time, self.df_0.mix_end_time)
            self.df_0.pack_start_time = temp_pack_start_time
            self.df_0.pack_start_time = self.df_0.pack_start_time + washing_time + timedelta(minutes=1)
            self.df_0.pack_end_time = self.df_0.pack_end_time + self.bucket_filling_time(self.df_0.dict[self.df_0.keys[i]]["Miktar"])
            self.df_0.pack_start_time = self.df_0.pack_end_time

            self.update_avaliable_pot_time(self.df_0.pack_end_time, pot_number)
            self.calculate_delta(i,0, self.df_0.pack_end_time)

            if i < self.df_1.df_len:
                # ----------machine_1[i] ---------
                # kg_time_calculation
                pot_number = self.df_1.dict[self.df_1.keys[i]]["Kazan"]
                self.df_1.disp_start_time = max(self.df_1.disp_start_time, self.pot_time_dict[pot_number][0])

                kg_time_result = self.disp_fillig_time(self.df_1.dict[self.df_1.keys[i]]["Miktar"],self.df_1.dict[self.df_1.keys[i]]["component_count"])
                self.df_1.disp_end_time = (self.df_1.disp_start_time + kg_time_result + self.disp_setup_time)
                self.df_1.disp_start_time = self.df_1.disp_end_time
                self.df_1.mix_end_time = self.df_1.disp_end_time + self.mix_time
                
                # packaging_time_calculation
                washing_time = self.color_table[self.df_1.dict[self.df_1.keys[i-1]]["Renk"]][self.df_1.dict[self.df_1.keys[i]]["Renk"]]
                self.washing_time_2 += washing_time.total_seconds()

                temp_pack_start_time = max(self.df_1.pack_start_time, self.df_1.mix_end_time)
                self.df_1.pack_start_time = temp_pack_start_time
                self.df_1.pack_start_time = self.df_1.pack_start_time + washing_time + timedelta(minutes=2)
                self.df_1.pack_end_time = self.df_1.pack_end_time + self.bucket_filling_time(self.df_0.dict[self.df_0.keys[i]]["Miktar"])
                self.df_1.pack_start_time = self.df_1.pack_end_time

                self.update_avaliable_pot_time(self.df_1.pack_end_time, pot_number)
                self.calculate_delta(i,1, self.df_1.pack_end_time)
                self.start_time

        self.df_0.makespan = (self.df_0.pack_end_time - self.start_time).total_seconds()
        self.df_1.makespan = (self.df_1.pack_end_time - self.df_1.disp_start_time).total_seconds()

        if self.df_sort_changed:
            calc_dict_atrib_0 = {
                "dict": self.df_1.dict,
                "makespan": self.df_1.makespan,
                "tardy": self.df_1.tardy,
                "washing_time": self.washing_time_2
            }
            calc_dict_atrib_1 = {
                "dict": self.df_0.dict,
                "makespan": self.df_0.makespan,
                "tardy": self.df_0.tardy,
                "washing_time": self.washing_time_1
            }
        else:
            calc_dict_atrib_0 = {
                "dict": self.df_0.dict,
                "makespan": self.df_0.makespan,
                "tardy": self.df_0.tardy,
                "washing_time": self.washing_time_1
            }
            calc_dict_atrib_1 = {
                "dict": self.df_1.dict,
                "makespan": self.df_1.makespan,
                "tardy": self.df_1.tardy,
                "washing_time": self.washing_time_2
            }
        
        return calc_dict_atrib_0, calc_dict_atrib_1
    
