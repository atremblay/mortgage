import sympy
from sympy import Symbol, symbols, lambdify, simplify, log
from enum import Enum
import numpy as np
import ggplot
from ggplot import aes, geom_point
import pandas as pd
import math

class Modality(Enum):
    montly = 1
    weekly = 2
    accelerated_weekly = 3

class Mortgage(object):
    """docstring for Mortgage"""
    def __init__(self, interest, term, loan, modality):
        super(Mortgage, self).__init__()

        self._interest = interest
        self.term = term
        self.loan = loan
        self.modality = modality

        self._i, self._m, self._j = symbols('i m j', real=True)
        self._R = Symbol('R', real=True)
        self._k = Symbol('k', integer=True)

        self._rate_conversion = (1 + self._i/2.0)**(2.0/self._m) - 1

        self._present_value = loan*(1+self._j)**self._k
        self._present_value += self._R*(1-(1+self._j)**self._k)/self._j
        self._present_value = self._present_value

        self._accrued_interest = loan*((1+self._j)**self._k-1)
        self._accrued_interest += self._R*(self._k-((1+self._j)**self._k - 1)/self._j)
        self._accrued_interest = self._accrued_interest

        self._accrued_capital = self._k * self._R - self._accrued_interest
        self._accrued_capital = self._accrued_capital

        self._equilibrium = log(-self._R/(2*(self._j * loan - self._R)))/\
        log(1+self._j)

    def payment(self):
        if self.modality == Modality.accelerated_weekly:
            return self.loan / self.annuity()

    def annuity(self):
        if self.modality == Modality.accelerated_weekly:
            j = self._rate_conversion.subs({self._i:self._interest, self._m:12})
            annuity = (1-(1 + j)**(-self.term * 12))/j
            return annuity * 4

    def interest(self, k):
        j = self._rate_conversion.subs({self._i:self._interest, self._m:52})
        return self.present_value(k-1) * j

    def present_value(self, k):
        params = [self._k, self._j, self._R]
        expr = lambdify(params, self._present_value, "numpy")
        j = self._rate_conversion.subs({self._i:self._interest, self._m:52})
        R = self.payment()
        pv = expr(k, j, R)
        if pv < 0:
            return 0
        return pv

    def capital(self, k):
        p = self.payment()
        capital = p - self.interest(k)
        pv = self.present_value(k)
        if capital > pv:
            return pv
        return p - self.interest(k)

    def accrued_interest(self, k):
        params = [self._k, self._j, self._R]
        expr = lambdify(params, self._accrued_interest, "numpy")
        j = self._rate_conversion.subs({self._i:self._interest, self._m:52})
        p = self.payment()
        return expr(k, j, p)

    def accrued_capital(self, k):
        params = [self._k, self._j, self._R]
        expr = lambdify(params, self._accrued_capital, "numpy")
        j = self._rate_conversion.subs({self._i:self._interest, self._m:52})
        p = self.payment()
        return expr(k, j, p)

    def equilibrium(self):
        params = [self._j, self._R]
        expr = lambdify(params, self._equilibrium, "math")
        j = self._rate_conversion.subs({self._i:self._interest, self._m:52})
        R = self.payment()
        return expr(j, R) + 1

    def table(self):
        i = 0
        if self.modality == Modality.accelerated_weekly:
            modality = 52
        table = [[self.present_value(k), self.capital(k), self.interest(k)] for k in range(self.term * modality)]
        # capital = [self.capital(k) for k in range(self.term * modality)]
        # interest = [self.interest(k) for k in range(self.term * modality)]

        table = np.array(table)
        return table[table[:,0] > 0]

    def plot(self):
        table = self.table()
        df = pd.DataFrame(table, columns=['pv','capital','interest'])
        data = pd.melt(df.reset_index(),
            id_vars='index',
            value_vars=['capital','interest'],
            value_name='amount')
        return ggplot.ggplot(data,
            aes(x='index',y='amount', color='variable')) +\
        geom_point(size=1) + ggplot.geom_vline(aes(xintercept=self._equilibrium()), color='black')
