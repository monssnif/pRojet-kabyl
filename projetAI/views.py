from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from aima3.logic import *


class ProcessAPIView(APIView):
    def post(self, request):
        res = request.data.get('reserve', '')
        dbud = request.data.get('dailybud', '')
        dinc = request.data.get('dailyinc', '')
        remd = request.data.get('remainingDays', '')

        def money_factor():
            if dbud != 0 and remd != 0:
                return (res + (dinc * remd)) / (dbud * remd)
            else:
                return 2

        def Reserve_State(x, y):
            if x / y < 166:
                return "Relatively_Low"
            elif 166 <= x / y < 250:
                return "Sufficiante"
            else:
                return "Relatively_high"

        def state(monf):
            if monf == 0:
                return "Broke"
            elif 0 < monf <= 1:
                return "Unstable"
            elif 1 < monf <= 1.5:
                return "Stable"
            else:
                return "Rich"

        S = state(money_factor())
        RS = Reserve_State(res, remd)
        BCF1 = FolKB()
        BCF1.tell(expr("State(Unstable)"))
        BCF1.tell(expr("State(Broke)"))
        BCF1.tell(expr("State(Stable)"))
        BCF1.tell(expr("State(Rich)"))
        BCF1.tell(expr("Reserve(Relatively_Low)"))
        BCF1.tell(expr("Reserve(Sufficiante)"))
        BCF1.tell(expr("Reserve(Relatively_high)"))
        BCF1.tell(expr("Decision(Broke,Relatively_Low,Find_an_income_source_plus_lower_the_amount_spent_daily)"))
        BCF1.tell(expr("Decision(Broke,Sufficiante,Find_an_income_source_plus_lower_the_amount_spent_daily)"))
        BCF1.tell(expr("Decision(Broke,Relatively_high,Find_an_income_source_plus_lower_the_amount_spent_daily)"))
        BCF1.tell(expr("Decision(Unstable,Relatively_Low,Find_a_better_income_source)"))
        BCF1.tell(expr("Decision(Unstable,Sufficiante,The_daily_income_is_slightly_unsufficiante_relative_to_the_amount_spent_daily_try_to_increase_it)"))
        BCF1.tell(expr("Decision(Unstable,Relatively_high,The_Problem_here_is_the_amount_spent_daily_it_needs_to_be_lowered_a_bit)"))
        BCF1.tell(expr("Decision(Stable,Relatively_Low,You_can_increase_the_amount_spent_daily)"))
        BCF1.tell(expr("Decision(Stable,Sufficiante,Keep_things_running_as_they_are_try_to_never_past_through_your_current_daily_amount)"))
        BCF1.tell(expr("Decision(Stable,Relatively_high,Suggested_that_you_slightly_lower_the_budget_to_keep_things_stable_in_the_long_run)"))
        BCF1.tell(expr("Decision(Rich,Sufficiante,You_can_increase_the_amount_spent_daily)"))
        BCF1.tell(expr("Decision(Rich,Relatively_Low,You_can_increase_the_amount_spent_daily)"))
        BCF1.tell(expr("Decision(Rich,Relatively_high,You_can_greatly_increase_the_amount_spent_daily)"))
        BCF1.tell(expr("State(e) & Reserve(b) & Decision(e,b,d)==>Result(e,b,d)"))

        BCF1.clauses

        response = fol_fc_ask(BCF1, expr("Result(x,y,z)"))

        if response:
            for l in list(response):
                if str(l[x]) == S and str(l[y]) == RS:
                    text = "Your state is : " + S + "  Your reserve is : " + RS + "  We suggest : " + str(l[z])
                    new_text = text.replace("_", " ")
                    return Response({'message': new_text}, status=status.HTTP_200_OK)
        else:
            return Response({'message': "Unable to determine financial state."}, status=status.HTTP_400_BAD_REQUEST)