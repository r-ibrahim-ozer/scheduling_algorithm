import pandas as pd
from itertools import combinations
from time_calc_dict import Machines

class TabuSearch():
    def __init__(self, start_time, dict_1, dict_2, seed, tabu_tenure, Penalization_weight):
        self.start_time = start_time
        self.seed = seed
        self.tabu_tenure = tabu_tenure
        self.Penalization_weight = Penalization_weight

        self.est_obj = Machines(self.start_time, dict_1, dict_2)

        self.instance_dict = {0: self.est_obj.df_0, 
                              1: self.est_obj.df_1}
        
        self.initial_solution_1 = self.est_obj.df_0.keys
        self.initial_solution_2 = self.est_obj.df_1.keys


    def get_tabuestructure(self, dict_numb):
        dict = {}
        for swap in combinations(self.instance_dict[dict_numb].keys, 2):
            dict[swap] = {'tabu_time': 0, 'MoveValue': 0, 'freq': 0, 'Penalized_MV': 0}
        return dict

    def Objfun(self, solution_1, solution_2):

        # add span time from machines()
        # buraya keyler geldi burdan sonra yeniden bir dict oluşturup onu döndür
        dict_atrib_0 , dict_atrib_2 = self.est_obj.dict_est_time(solution_1, solution_2)

        objfun_value = dict_atrib_0["washing_time"]+ dict_atrib_2["washing_time"]+ dict_atrib_0["tardy"]*500 + dict_atrib_2["tardy"]*500

        return objfun_value

    def SwapMove(self, solution, i, j):

        solution = solution.copy()
        element = solution.pop(j)
        solution.insert(i+1, element)

        return solution

    def TSearch(self):

        tenure = self.tabu_tenure
        tabu_structure_1 = self.get_tabuestructure(0)
        tabu_structure_2 = self.get_tabuestructure(1)

        best_solution_1 = self.initial_solution_1
        best_solution_2 = self.initial_solution_2

        best_objvalue = self.Objfun(best_solution_1, best_solution_2)

        current_solution_1 = self.initial_solution_1
        current_solution_2 = self.initial_solution_2
        # should arrange
        current_objvalue = self.Objfun(best_solution_1, best_solution_2)

        # print("#" * 30, "Short-term memory TS with Tabu Tenure: {}\nInitial Solution: {}, Initial Objvalue: {}".format(
            # tenure, current_solution_1, current_objvalue), "#" * 30, sep='\n\n')
        iter = 1
        Terminate = 0

        while Terminate < 100 and iter < 250:
            # print('\n\n### iter {}###  Current_Objvalue: {}, Best_Objvalue: {}'.format(iter, current_objvalue,
                                                                                    # best_objvalue))
            # Searching the whole neighborhood of the current solution:

            #-------------------dict1 for-------------------
            for move in tabu_structure_1:
                candidate_solution_1 = self.SwapMove(current_solution_1, move[0], move[1])
                candidate_objvalue = self.Objfun(candidate_solution_1, best_solution_2)
                tabu_structure_1[move]['MoveValue'] = candidate_objvalue
                # Penalized objValue by simply adding freq to Objvalue (minimization):
                tabu_structure_1[move]['Penalized_MV'] = candidate_objvalue + (tabu_structure_1[move]['freq'] *
                                                                             self.Penalization_weight)

            # Admissible move
            #-------------------dict1 while-------------------
            while True:
                # select the move with the lowest Penalized ObjValue in the neighborhood (minimization)
                best_move_1 = min(tabu_structure_1, key =lambda x: tabu_structure_1[x]['Penalized_MV'])
                MoveValue_1 = tabu_structure_1[best_move_1]["MoveValue"]
                tabu_time_1 = tabu_structure_1[best_move_1]["tabu_time"]
                # Penalized_MV = tabu_structure[best_move]["Penalized_MV"]
                # Not Tabu
                if tabu_time_1 < iter:
                    # make the move
                    current_solution_1 = self.SwapMove(current_solution_1, best_move_1[0], best_move_1[1])
                    current_objvalue = self.Objfun(current_solution_1, best_solution_2)
                    # Best Improving move
                    if MoveValue_1 < best_objvalue:
                        best_solution_1 = current_solution_1
                        best_objvalue = current_objvalue
                        # print("   best_move: {}, Objvalue: {} => Best Improving => Admissible".format(best_move_1,
                        #                                                                               current_objvalue))
                        Terminate = 0
                    else:
                        # print("   ##Termination: {}## best_move: {}, Objvalue: {} => Least non-improving => "
                        #       "Admissible".format(Terminate,best_move_1,
                        #                                                                                    current_objvalue))
                        Terminate += 1
                    # update tabu_time for the move and freq count
                    tabu_structure_1[best_move_1]['tabu_time'] = iter + tenure
                    tabu_structure_1[best_move_1]['freq'] += 1
                    iter += 1
                    break
                # If tabu
                else:
                    # Aspiration
                    if MoveValue_1 < best_objvalue:
                        # make the move
                        current_solution_1 = self.SwapMove(current_solution_1, best_move_1[0], best_move_1[1])
                        current_objvalue = self.Objfun(current_solution_1, best_solution_2)
                        best_solution_1 = current_solution_1
                        best_objvalue = current_objvalue
                        # print("   best_move: {}, Objvalue: {} => Aspiration => Admissible".format(best_move_1,
                        #                                                                           current_objvalue))
                        tabu_structure_1[best_move_1]['freq'] += 1
                        Terminate = 0
                        iter += 1
                        break
                    else:
                        tabu_structure_1[best_move_1]['Penalized_MV'] = float('inf')
                        # print("   best_move: {}, Objvalue: {} => Tabu => Inadmissible".format(best_move_1,
                        #                                                                       current_objvalue))
                        continue

            #-------------------dict2 for-------------------
            for move in tabu_structure_2:
                candidate_solution_2 = self.SwapMove(current_solution_2, move[0], move[1])
                candidate_objvalue = self.Objfun(best_solution_1, candidate_solution_2)
                tabu_structure_2[move]['MoveValue'] = candidate_objvalue
                # Penalized objValue by simply adding freq to Objvalue (minimization):
                tabu_structure_2[move]['Penalized_MV'] = candidate_objvalue + (tabu_structure_2[move]['freq'] *
                                                                             self.Penalization_weight)
            
            # Admissible move
            #-------------------dict2 while-------------------
            while True:
                # select the move with the lowest Penalized ObjValue in the neighborhood (minimization)
                best_move_2 = min(tabu_structure_2, key =lambda x: tabu_structure_2[x]['Penalized_MV'])
                MoveValue_2 = tabu_structure_2[best_move_2]["MoveValue"]
                tabu_time_2 = tabu_structure_2[best_move_2]["tabu_time"]
                # Penalized_MV = tabu_structure[best_move]["Penalized_MV"]
                # Not Tabu
                if tabu_time_2 < iter:
                    # make the move
                    current_solution_2 = self.SwapMove(current_solution_2, best_move_2[0], best_move_2[1])
                    current_objvalue = self.Objfun(best_solution_1, current_solution_2)
                    # Best Improving move
                    if MoveValue_2 < best_objvalue:
                        best_solution_2 = current_solution_2
                        best_objvalue = current_objvalue
                        # print("   best_move: {}, Objvalue: {} => Best Improving => Admissible".format(best_move_2,
                        #                                                                               current_objvalue))
                        Terminate = 0
                    else:
                        # print("   ##Termination: {}## best_move: {}, Objvalue: {} => Least non-improving => "
                        #       "Admissible".format(Terminate,best_move_2,
                                                                                                        #    current_objvalue))
                        Terminate += 1
                    # update tabu_time for the move and freq count
                    tabu_structure_2[best_move_2]['tabu_time'] = iter + tenure
                    tabu_structure_2[best_move_2]['freq'] += 1
                    iter += 1
                    break
                # If tabu
                else:
                    # Aspiration
                    if MoveValue_2 < best_objvalue:
                        # make the move
                        current_solution_2 = self.SwapMove(current_solution_2, best_move_2[0], best_move_2[1])
                        current_objvalue = self.Objfun(best_solution_1, current_solution_2)
                        best_solution_2 = current_solution_2
                        best_objvalue = current_objvalue
                        # print("   best_move: {}, Objvalue: {} => Aspiration => Admissible".format(best_move_2,
                        #                                                                           current_objvalue))
                        tabu_structure_2[best_move_2]['freq'] += 1
                        Terminate = 0
                        iter += 1
                        break
                    else:
                        tabu_structure_2[best_move_2]['Penalized_MV'] = float('inf')
                        # print("   best_move: {}, Objvalue: {} => Tabu => Inadmissible".format(best_move_2,
                                                                                            #   current_objvalue))
                        continue
            
        # print('#'*50 , "Performed iterations: {}".format(iter), "Best found Solution: {} , Objvalue: {}".format(best_solution_1,best_objvalue), sep="\n")
        # print('#'*50 , "Performed iterations: {}".format(iter), "Best found Solution: {} , Objvalue: {}".format(best_solution_2,best_objvalue), sep="\n")
        return best_solution_1, best_solution_2, best_objvalue
    
