from pymoo.core.problem import ElementwiseProblem

class FlowScheduling(ElementwiseProblem):

    def __init__(self, solution, est_obj_pymoo , **kwargs):
        """
        Flowshop scheduling problem.

        Parameters
        ----------
        processing_times : numpy.array
            Matrix where processing_time[i][j] is the processing time for job j on machine i.

        """

        n_jobs = len(solution)
        self.records = solution
        self.est_obj_pymoo = est_obj_pymoo
        super(FlowScheduling, self).__init__(
            n_var=n_jobs,
            n_obj=1,
            xl=0,
            xu=1,
            vtype=int,
            **kwargs
        )

    def Objfun(self, solution):
        dict_atrib_0 , dict_atrib_2 = self.est_obj_pymoo.dict_est_time(solution)

        objfun_value = dict_atrib_0["washing_time"] + dict_atrib_0["tardy"]*500 + dict_atrib_2["tardy"]*500

        return objfun_value

    def _evaluate(self, solution, out, *args, **kwargs):
        out["F"] = self.Objfun(solution)