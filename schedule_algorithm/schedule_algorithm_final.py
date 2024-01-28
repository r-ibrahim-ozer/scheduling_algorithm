import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from time_calc_dataframe import Machines as mc
from time_calc_dict import Machines

from time_calc_dict_pymoo import Machines as mc_pymoo
from pymoo_algortihms import FlowScheduling
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.termination.default import DefaultSingleObjectiveTermination

# İşlem başlangıç zamanının kaydedilmesi. algoritmanın çalışma süresini ölçmek için kullanılıyor.
pros_start_time = datetime.now()

# Sipariş numarası ve sap numarası uzunlukları
siparis_no_digits = 3
sap_no_digits = 5

# Sipariş başlıkları

# İşlem başlangıç zamanının kaydedilmesi. algoritmanın çalışma süresini ölçmek için kullanılıyor.
start_time = datetime.strptime('02.11.2023 08:00:01', '%m.%d.%Y %H:%M:%S')

# Renkleri, grupları ve kazanları
product_color_names = ["sari", "turuncu", "kirmizi", "yesil", "mavi", "mor", "kahverengi", "siyah"] # sipariş renk
product_groups_names = ["sari", "kirmizi", "kirmizi", "mavi","mavi", "mavi", "siyah", "siyah"] # karşılık gelen kazan isimleri
product_groups_pot = [0, 1, 1, 2, 2, 2, 3, 3]

next_pot = [1,2,3,0]

kamyon_zamani_hours = ["11", "20", "21", "22"] #kamyonların hareket edebileceğü saat dilimleri

# Sipariş miktarları
kilo=[80,160,720,750] #siparişler için belirlenmiş kilo değerleri. şimdiki durumda bir hesaplamada kullanılmıyor.
# kilo ileriki aşamalarda kullanılacak.

product_groups_pots = {
    "sari": 0,
    "turuncu": 1,
    "kirmizi": 1,
    "yesil": 2,
    "mavi": 2,
    "mor": 2,
    "kahverengi": 3,
    "siyah": 3,
}

past_color = {
    "sari": False,
    "turuncu": False,
    "kirmizi": "turuncu",
    "yesil": False,
    "mavi": "yesil",
    "mor": "mavi",
    "kahverengi": False,
    "siyah": "kahverengi",
}


# rastegle bir tarih aralığı oluşturan fonksiyon
def random_datetime(start_date, end_date):
    return start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))


# similasyon için sipariş matrisi oluşturan fonksiyon
def generate_order_matrix(num_orders):
    order_matrix = []
    starting_siparis_no = 1

    for _ in range(num_orders):
        np.random.seed(_)
        # Sipariş numarası ve sap numarası oluşturuluyor
        siparis_no = starting_siparis_no
        starting_siparis_no += 1
        sap_no = str(random.randint(1, 99999)).zfill(sap_no_digits)
        tanım = str(random.randint(1, 99999)).zfill(sap_no_digits)
        urt_ist = "OPAL" if _<=20 else "ZÜMRÜT"
        # Diğer parametreler rastgele seçiliyor

        product_color = np.random.choice(product_color_names)
        product_group = product_groups_pot[product_color_names.index(product_color)]
        component_count = np.random.randint(1, 21)
        sap_bitis_zamani = start_time + timedelta(random.randint(-3,-1))
        miktar=random.choice(kilo)

        kamyon_zamani = (sap_bitis_zamani + timedelta(hours=int(np.random.choice(kamyon_zamani_hours))))
        satis_istek_zamani = (sap_bitis_zamani + timedelta(hours=np.random.randint(10, 20)))
        istenen_zaman = min(kamyon_zamani, satis_istek_zamani)  if np.random.choice([True,False,False, False]) else pd.NaT
        # Oluşturulan siparişi matrise ekleme
        order_matrix.append([siparis_no, sap_no,tanım,urt_ist, miktar,product_color , product_group,component_count, sap_bitis_zamani, istenen_zaman])

    return order_matrix

# similasyon için sipariş sayısı 50 sipariş belirlendi.
num_orders = 40

baslik = ["İş emri,Malzeme No,Tanım,Ürt. İst.,Miktar,Renk,Kazan,component_count,sap zamanı,kamyon/satis"]
# sipariş oluşturma fonksiyonu çağırıldı


df = generate_order_matrix(num_orders)
df = pd.DataFrame(df, columns=baslik[0].split(","))

df_opal = df[df['Ürt. İst.'] == 'OPAL']
df_zumrut = df[df['Ürt. İst.'] == 'ZÜMRÜT']

def process_and_sort_df(df):
    tmp_df = df.copy()
    # başlangıç çözümü için sıralama yapıldı.
    tmp_df.sort_values(by=["sap zamanı"], inplace=True)
    tmp_df.sort_values(by=["kamyon/satis"], inplace=True)

    return tmp_df

df_opal = process_and_sort_df(df_opal).reset_index(drop=True)
df_zumrut = process_and_sort_df(df_zumrut).reset_index(drop=True)
dflen_0 = len(df_opal)
dflen_1 = len(df_zumrut)

dict_1=df_opal.to_dict('index')
dict_2=df_zumrut.to_dict('index')

# dict_1


est_obj = Machines(start_time, dict_1, dict_2)

initial_solution_1 = list(dict_1.keys())
initial_solution_2 = list(dict_2.keys())

calc_dict_atrib_0, calc_dict_atrib_1 = est_obj.dict_est_time(initial_solution_1, initial_solution_2)

# initial
df_0 = calc_dict_atrib_0["dict"]
df_1 = calc_dict_atrib_1["dict"]
df_0_makespan = calc_dict_atrib_0["makespan"]
df_1_makespan = calc_dict_atrib_1["makespan"]
df_0_tardy = calc_dict_atrib_0["tardy"]
df_1_tardy = calc_dict_atrib_1["tardy"]

initial_total_tardy = df_0_tardy + df_1_tardy
initial_total_makespan = df_0_makespan + df_1_makespan

best_total_tardy = initial_total_tardy
best_total_makespan = initial_total_makespan

swap_count = 0
swap_count_s = 0

algorithm_start_time = datetime.now()

#----------Our huristic başlangıç----------#
#------sıralama algoritması başlangıcı------#
for current_order_index in range(est_obj.df_0.df_len):

    current_product_group = est_obj.df_0.dict[est_obj.df_0.keys[current_order_index]]["Kazan"]

    for target_order_index in range(current_order_index + 1, est_obj.df_0.df_len):

        if est_obj.df_0.dict[est_obj.df_0.keys[target_order_index]]["Kazan"] == current_product_group:
            
            candidate_solution_1 = est_obj.df_0.keys.copy()
            # Remove the element at target_order_index
            element = candidate_solution_1.pop(target_order_index)
            # Insert the element next to current_order_index
            candidate_solution_1.insert(current_order_index + 1, element)
            # Yeni düzenlemeyi kontrol et ve kabul et
            cand_att_0, cand_att_1 = est_obj.dict_est_time(candidate_solution_1, est_obj.df_1.keys)

            candidate_tardy = cand_att_0["tardy"] + cand_att_1["tardy"]
            candidate_makespan = cand_att_0["makespan"] + cand_att_1["makespan"]

            if candidate_tardy <= best_total_tardy:
                if (candidate_makespan - initial_total_makespan <= 7200 ):
                    est_obj.df_0.keys = candidate_solution_1
                    best_total_makespan = candidate_makespan
                    best_total_tardy = candidate_tardy
                    swap_count += 1
                    break 
                else:
                    
                    for next_target_order_index in range(current_order_index+1,est_obj.df_0.df_len):

                        if est_obj.df_0.dict[est_obj.df_0.keys[next_target_order_index]]["Kazan"] == next_pot[current_product_group]:

                            candidate_solution_1 = est_obj.df_0.keys.copy()
                            # Remove the element at target_order_index
                            element = candidate_solution_1.pop(target_order_index)
                            # Insert the element next to current_order_index
                            candidate_solution_1.insert(current_order_index + 1, element)
                            # Yeni düzenlemeyi kontrol et ve kabul et
                            cand_att_0, cand_att_1 = est_obj.dict_est_time(candidate_solution_1, est_obj.df_1.keys)

                            candidate_tardy = cand_att_0["tardy"] + cand_att_1["tardy"]
                            candidate_makespan = cand_att_0["makespan"] + cand_att_1["makespan"]
                            if candidate_tardy <= best_total_tardy and (candidate_makespan - initial_total_makespan <= 7200):
                                est_obj.df_0.keys = candidate_solution_1
                                best_total_makespan = candidate_makespan
                                best_total_tardy = candidate_tardy
                                swap_count += 1
                                break


for current_order_index in range(est_obj.df_1.df_len):

    current_product_group = est_obj.df_1.dict[est_obj.df_1.keys[current_order_index]]["Kazan"]

    for target_order_index in range(current_order_index + 1, est_obj.df_1.df_len):
        if est_obj.df_1.dict[est_obj.df_1.keys[target_order_index]]["Kazan"] == current_product_group:
            
            candidate_solution_2 = est_obj.df_1.keys.copy()
            # Remove the element at target_order_index
            element = candidate_solution_2.pop(target_order_index)
            # Insert the element next to current_order_index
            candidate_solution_2.insert(current_order_index + 1, element)
            
            # Yeni düzenlemeyi kontrol et ve kabul et
            cand_att_0, cand_att_1 = est_obj.dict_est_time(est_obj.df_0.keys, candidate_solution_2)

            candidate_tardy = cand_att_0["tardy"] + cand_att_1["tardy"]
            candidate_makespan = cand_att_0["makespan"] + cand_att_1["makespan"]

            if candidate_tardy <= best_total_tardy:
                if (candidate_makespan - initial_total_makespan <= 3600):
                    est_obj.df_1.keys = candidate_solution_2
                    best_total_makespan = candidate_makespan
                    best_total_tardy = candidate_tardy
                    swap_count += 1
                    break 
                else:
                    
                    for next_target_order_index in range(current_order_index+1,est_obj.df_1.df_len):

                        if est_obj.df_1.dict[est_obj.df_1.keys[next_target_order_index]]["Kazan"] == next_pot[current_product_group]:

                            candidate_solution_2 = est_obj.df_1.keys.copy()
                            # Remove the element at target_order_index
                            element = candidate_solution_2.pop(target_order_index)
                            # Insert the element next to current_order_index
                            candidate_solution_2.insert(current_order_index + 1, element)
                            # Yeni düzenlemeyi kontrol et ve kabul et
                            cand_att_0, cand_att_1 = est_obj.dict_est_time(est_obj.df_0.keys, candidate_solution_2)

                            candidate_tardy = cand_att_0["tardy"] + cand_att_1["tardy"]
                            candidate_makespan = cand_att_0["makespan"] + cand_att_1["makespan"]
                            if candidate_tardy <= best_total_tardy and (candidate_makespan - initial_total_makespan <= 7000):
                                est_obj.df_1.keys = candidate_solution_2
                                best_total_makespan = candidate_makespan
                                best_total_tardy = candidate_tardy
                                swap_count += 1
                                break

def sort_by_color(dict_no,best_total_tardy=best_total_tardy,best_total_makespan=best_total_makespan,swap_count=swap_count):
    if dict_no == 0:
        solution_list = est_obj.df_0.keys
    else:
        solution_list = est_obj.df_1.keys
    for current_order_index in range(est_obj.df_dict[dict_no].df_len-1):

        current_product_group = est_obj.df_dict[dict_no].dict[solution_list[current_order_index]]["Kazan"]
        current_color_group = est_obj.df_dict[dict_no].dict[solution_list[current_order_index]]["Renk"]
        past_color_group = past_color[current_color_group]

        for target_order_index in range(current_order_index + 1, est_obj.df_dict[dict_no].df_len):
            target_product_group = est_obj.df_dict[dict_no].dict[solution_list[target_order_index]]["Kazan"]
            if target_product_group == current_product_group and past_color_group == est_obj.df_dict[dict_no].dict[solution_list[target_order_index]]["Renk"]:
                if dict_no == 0:
                    candidate_solution_1 = est_obj.df_0.keys.copy()
                else:
                    candidate_solution_1 = est_obj.df_1.keys.copy()                   
                
                # Remove the element at target_order_index
                element = candidate_solution_1.pop(target_order_index)
                # Insert the element next to current_order_index
                candidate_solution_1.insert(current_order_index + 1, element)
                # Yeni düzenlemeyi kontrol et ve kabul et
                if dict_no == 0:
                    cand_att_0, cand_att_1 = est_obj.dict_est_time(candidate_solution_1, est_obj.df_1.keys)
                else:
                    cand_att_0, cand_att_1 = est_obj.dict_est_time(est_obj.df_0.keys, candidate_solution_1)

                candidate_tardy = cand_att_0["tardy"] + cand_att_1["tardy"]
                candidate_makespan = cand_att_0["makespan"] + cand_att_1["makespan"]

                if candidate_tardy <= best_total_tardy:
                    if (candidate_makespan - initial_total_makespan <= 5000 ):
                        if dict_no == 0:
                            est_obj.df_0.keys = candidate_solution_1
                        else:
                            est_obj.df_1.keys = candidate_solution_1
                        best_total_makespan = candidate_makespan
                        best_total_tardy = candidate_tardy
                        swap_count += 1
                        break 
            elif target_product_group != current_product_group: break
        return est_obj.df_0.keys, est_obj.df_1.keys, best_total_tardy, best_total_makespan, swap_count

#--------sort by color--------#
est_obj.df_0.keys, est_obj.df_1.keys, best_total_tardy, best_total_makespan, swap_count = sort_by_color(0)
est_obj.df_0.keys, est_obj.df_1.keys, best_total_tardy, best_total_makespan, swap_count = sort_by_color(1)
#--------sort by color--------#

#--------swap same color--------#
def swap_same_colors(dict_no,best_total_tardy=best_total_tardy,best_total_makespan=best_total_makespan,swap_count=swap_count):
    if dict_no == 0:
        solution_list = est_obj.df_0.keys
    else:
        solution_list = est_obj.df_1.keys

    for current_order_index in range(est_obj.df_dict[dict_no].df_len-1):

        current_color_group = est_obj.df_dict[dict_no].dict[solution_list[current_order_index]]["Renk"]

        for target_order_index in range(current_order_index + 1, est_obj.df_dict[dict_no].df_len):

            target_color_group = est_obj.df_dict[dict_no].dict[solution_list[target_order_index]]["Renk"]
            if target_color_group == current_color_group:
                if dict_no == 0:
                    candidate_solution_1 = est_obj.df_0.keys.copy()
                else:
                    candidate_solution_1 = est_obj.df_1.keys.copy()                   
                
                # Remove the element at target_order_index
                candidate_solution_1[current_order_index], candidate_solution_1[target_order_index] = candidate_solution_1[target_order_index], candidate_solution_1[current_order_index]
                # Yeni düzenlemeyi kontrol et ve kabul et
                if dict_no == 0:
                    cand_att_0, cand_att_1 = est_obj.dict_est_time(candidate_solution_1, est_obj.df_1.keys)
                else:
                    cand_att_0, cand_att_1 = est_obj.dict_est_time(est_obj.df_0.keys, candidate_solution_1)

                candidate_tardy = cand_att_0["tardy"] + cand_att_1["tardy"]
                candidate_makespan = cand_att_0["makespan"] + cand_att_1["makespan"]

                if candidate_tardy <= best_total_tardy:
                    if (candidate_makespan <= best_total_makespan):
                        if dict_no == 0:
                            est_obj.df_0.keys = candidate_solution_1
                        else:
                            est_obj.df_1.keys = candidate_solution_1

                        best_total_makespan = candidate_makespan
                        best_total_tardy = candidate_tardy
                        swap_count += 1
                        break 
            else: break
    return est_obj.df_0.keys, est_obj.df_1.keys, best_total_tardy, best_total_makespan, swap_count
    

#--------swap same color--------#
est_obj.df_0.keys, est_obj.df_1.keys, best_total_tardy, best_total_makespan, swap_count = swap_same_colors(0)
est_obj.df_0.keys, est_obj.df_1.keys, best_total_tardy, best_total_makespan, swap_count = swap_same_colors(1)
#--------swap same color--------#

f_att_0, f_att_1 = est_obj.dict_est_time(est_obj.df_0.keys, est_obj.df_1.keys)
res_my_hur = f_att_0["washing_time"]+ f_att_1["washing_time"]  +  f_att_0["tardy"]*500 + f_att_1["tardy"]*500
makespan_my_hur = f_att_0["makespan"]+ f_att_1["makespan"]
tardy_my_hur = f_att_0["tardy"]+ f_att_1["tardy"]

my_hur_time = datetime.now() - algorithm_start_time
print(my_hur_time)

#----------Our huristic son----------#







#----------datframe func----------#
def dataframe_process(mc_obj):
    final_df, final_df_2 = mc_obj.calc_df_columns()
    final_df.reset_index(drop=True, inplace=True)
    final_df_2.reset_index(drop=True, inplace=True)
    return final_df, final_df_2
#----------datframe func----------#


#-------My hur -----------
dict_1_solution = {i: est_obj.df_0.dict[i] for i in est_obj.df_0.keys}
dict_2_solution = {i: est_obj.df_1.dict[i] for i in est_obj.df_1.keys}
df_0 = pd.DataFrame.from_dict(dict_1_solution, orient='index').reset_index(drop=True)
df_1 = pd.DataFrame.from_dict(dict_2_solution, orient='index').reset_index(drop=True)

mc_obj = mc(start_time, df_0, df_1)
final_df, final_df_2 = dataframe_process(mc_obj)
#-------My hur -----------

#--------TS--------#
from TS_longMemmory import TabuSearch as ts
est_obj.df_0.keys, est_obj.df_1.keys = initial_solution_1, initial_solution_2
ts_obj = ts(start_time, est_obj.df_0.dict, est_obj.df_1.dict, seed=2012, tabu_tenure=6, Penalization_weight=0.8)
best_solution_1, best_solution_2, best_objvalue = ts_obj.TSearch()

ts_solution_1 = {i: est_obj.df_0.dict[i] for i in best_solution_1}
ts_solution_2 = {i: est_obj.df_1.dict[i] for i in best_solution_2}
ts_df_0 = pd.DataFrame.from_dict(ts_solution_1, orient='index').reset_index(drop=True)
ts_df_1 = pd.DataFrame.from_dict(ts_solution_2, orient='index').reset_index(drop=True)

mc_ts_obj = mc(start_time, ts_df_0, ts_df_1)
ts_final_df, ts_final_df_2 = dataframe_process(mc_ts_obj)

f_att_ts_0, f_att_ts_1 = est_obj.dict_est_time(best_solution_1, best_solution_2)
res_ts = f_att_ts_0["washing_time"]+ f_att_ts_1["washing_time"]  +  f_att_ts_0["tardy"]*500 + f_att_ts_1["tardy"]*500
makespan_ts = f_att_ts_0["makespan"]+ f_att_ts_1["makespan"]
tardy_ts = f_att_ts_0["tardy"]+ f_att_ts_1["tardy"]

ts_time = datetime.now() - algorithm_start_time - my_hur_time
print(ts_time)
#--------TS--------#


dict_1 = {}
dict_2 = {}
sayac=0
for i in range(dflen_0):
    dict_1.update({sayac: df_opal.iloc[i].to_dict()})
    sayac+=1
for i in range(dflen_1):
    dict_2.update({sayac: df_zumrut.iloc[i].to_dict()})
    sayac+=1

#--------GA--------
est_obj_pymoo = mc_pymoo(start_time, dict_1, dict_2)
solution = initial_solution_1
solution.extend(initial_solution_2)

problem = FlowScheduling(solution,est_obj_pymoo)
algorithm = GA(
    pop_size=320,
    eliminate_duplicates=True,
    sampling=PermutationRandomSampling(),
    mutation=InversionMutation(),
    crossover=OrderCrossover()
)

termination = DefaultSingleObjectiveTermination(period=50, n_max_gen=10000)

res = minimize(
    problem,
    algorithm,
    termination,
    seed=1
)

solution = list(res.X)
df_len = est_obj_pymoo.df_0.df_len

best_solution_0 = [i for i in solution if i < df_len]
best_solution_1 = [i for i in solution if i >= df_len]

dict_1_solution = {i: est_obj_pymoo.df_0.dict[i] for i in best_solution_0}
dict_2_solution = {i: est_obj_pymoo.df_1.dict[i] for i in best_solution_1}
ga_df_0 = pd.DataFrame.from_dict(dict_1_solution, orient='index').reset_index(drop=True)
ga_df_1 = pd.DataFrame.from_dict(dict_2_solution, orient='index').reset_index(drop=True)

mc_ga_obj = mc(start_time, df_0, df_1)
ga_final_df, ga_final_df_2 = dataframe_process(mc_ga_obj)

f_att_ga_0, f_att_ga_1 = est_obj_pymoo.dict_est_time(solution)
res_ga = f_att_ga_0["washing_time"]+ f_att_ga_1["washing_time"]  +  f_att_ga_0["tardy"]*500 + f_att_ga_1["tardy"]*500
makespan_ga = f_att_ga_0["makespan"]+ f_att_ga_1["makespan"]
tardy_ga = f_att_ga_0["tardy"]+ f_att_ga_1["tardy"]

ga_time = datetime.now() - algorithm_start_time - ts_time 
print(ga_time)

#--------GA--------#

#------sonuçları kaydetme------#
analysis_df = []
analysis_df.append(res_my_hur)
analysis_df.append(res_ts)
analysis_df.append(res_ga)

times = []
times.append(my_hur_time)
times.append(ts_time)
times.append(ga_time)

makespan_df = []
makespan_df.append(makespan_my_hur)
makespan_df.append(makespan_ts)
makespan_df.append(makespan_ga)


tardy_df = []
tardy_df.append(tardy_my_hur)
tardy_df.append(tardy_ts)
tardy_df.append(tardy_ga)
#------sonuçları kaydetme------#

#------gantt chart oluşturma------#
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def create_table(df):
    tmp_df = df.copy()
    tmp_df['disp_start_time'] = tmp_df['disp_start_time'].apply(lambda x: x.strftime('%d.%m %H:%M'))
    tmp_df['disp_end_time'] = tmp_df['disp_end_time'].apply(lambda x: x.strftime('%d.%m %H:%M'))
    tmp_df['pack_start_time'] = tmp_df['pack_start_time'].apply(lambda x: x.strftime('%d.%m %H:%M'))
    tmp_df['pack_end_time'] = tmp_df['pack_end_time'].apply(lambda x: x.strftime('%d.%m %H:%M'))
    for i in range(len(tmp_df['kamyon/satis'])):
        try:
            tmp_df.at[i,'kamyon/satis'] = tmp_df.at[i,'kamyon/satis'].strftime('%d.%m %H:%M')
        except ValueError: pass
    tmp_df = tmp_df[['İş emri', 'Malzeme No','Renk','Ürt. İst.', 'Miktar', 'disp_start_time', 'disp_end_time', 'pack_start_time', 'pack_end_time', 'kamyon/satis','delta']]
    tmp_df.columns = ['İş emri', 'Malzeme No', 'Renk','İst.', 'Miktar', 'Disp. Baş.', 'Disp. Bit.', 'Paket. Baş.', 'Paket. Bit.', 'İstek Zamanı', 'Delta']

    table = go.Table(
        columnwidth = [70,65,120,35,35,100,100,100,100,100,30],
        header_values=tmp_df.columns,
        cells_values=[tmp_df[k].tolist() for k in tmp_df.columns],
    )


    return table


def create_gannt(df,dflen):
    gantt_data = []

    for i in range(dflen):
        gantt_data.append({
            'Görev': f'{df["İş emri"].iloc[i]}',
            'Başlangıç': df['disp_start_time'].iloc[i],
            'Bitiş': df['disp_end_time'].iloc[i],
            'Resource': 'dispenser'
        })
        gantt_data.append({
            'Görev': f'{df["İş emri"].iloc[i]}',
            'Başlangıç': df['disp_end_time'].iloc[i],
            'Bitiş': df['pack_start_time'].iloc[i],
            'Resource': 'Bekleme Alanı'
        })
        gantt_data.append({
            'Görev': f'{df["İş emri"].iloc[i]}',
            'Başlangıç': df['pack_start_time'].iloc[i],
            'Bitiş': df['pack_end_time'].iloc[i],
            'Resource': 'Paketleme'
        })
    gantt_df = pd.DataFrame(gantt_data)
    return gantt_df

def create_out(df,dflen):
    table = create_table(df)
    gantt_df = create_gannt(df,dflen)
    
    fig = make_subplots(
    rows=2, cols=1,
    specs=[[{"type": "table"}], [{"type": "bar"}]]
    )
    fig.add_trace(
    table,
    row=1, col=1
    )

    fig_gantt = px.timeline(gantt_df.sort_values(by='Başlangıç'), x_start='Başlangıç', x_end='Bitiş', y='Görev', color="Resource")
    fig_gantt.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up
    fig_gantt.layout.xaxis.domain = None
    fig_gantt.layout.yaxis.domain = None

    # add the traces to make_subplots
    for trace in fig_gantt.data:
        fig.add_trace(trace, row=2, col=1)

    fig.update_layout(fig_gantt.layout)

    fig.show()


def create_out(df,dflen):
    table = create_table(df)
    gantt_df = create_gannt(df,dflen)
    
    fig = make_subplots(
    rows=1, cols=1,
    specs=[[{"type": "bar"}]]
    )

    fig_gantt = px.timeline(gantt_df.sort_values(by='Başlangıç'), x_start='Başlangıç', x_end='Bitiş', y='Görev', color="Resource")
    fig_gantt.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up
    fig_gantt.layout.xaxis.domain = None
    fig_gantt.layout.yaxis.domain = None

    # add the traces to make_subplots
    for trace in fig_gantt.data:
        fig.add_trace(trace)

    fig.update_layout(fig_gantt.layout)

    fig.show()


#-------My hur -----------
create_out(final_df,len(df_0))
create_out(final_df_2,len(df_1))
#--------TS--------#
create_out(ts_final_df,len(ts_df_0))
create_out(ts_final_df_2,len(ts_df_1))
#--------GA--------#
create_out(ga_final_df,len(ga_df_0))
create_out(ga_final_df_2,len(ga_df_1))

#------gantt chart oluşturma------#
#------Result------# 
print("*"*50)

print("*"*50)
print(analysis_df)
print("*"*50)
print(times)
print("*"*50)
print(makespan_df)
print("*"*50)
print(tardy_df)

