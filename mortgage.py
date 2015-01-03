import sympy
from sympy import Symbol, symbols, lambdify, simplify
from enum import Enum

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
        self._p = Symbol('payment', real=True)
        self._k = Symbol('k', integer=True)

        self._rate_conversion = (1 + self._i/2.0)**(2.0/self._m) - 1

        self._present_value = loan*(1+self._j)**self._k
        self._present_value += self._p*(1-(1+self._j)**self._k)/self._j

        self._accrued_interest = loan*((1+self._j)**self._k-1)
        self._accrued_interest += self._p*(self._k-((1+self._j)**self._k - 1)/self._j)

        self._accrued_capital = self._k * self._p - self._accrued_interest

    def payment(self):
        if self.modality == Modality.accelerated_weekly:
            return self.loan / self.annuity()

    def annuity(self):
        if self.modality == Modality.accelerated_weekly:
            j = self._rate_conversion.subs({self._i:self._interest, self._m:12})
            annuity = (1-(1 + j)**(-self.term * 12))/j
            return annuity * 4

    def interest(self, k):
        params = [self._k, self._j, self._p]
        expr = lambdify(params, self._present_value, "numpy")
        j = self._rate_conversion.subs({self._i:self._interest, self._m:52})
        p = self.payment()
        return expr(k-1, j, p) * j

    def capital(self, k):
        return self.payment() - self.interest(k)

    def accrued_interest(self, k):
        params = [self._k, self._j, self._p]
        expr = lambdify(params, self._accrued_interest, "numpy")
        j = self._rate_conversion.subs({self._i:self._interest, self._m:52})
        p = self.payment()
        return expr(k, j, p)

    def accrued_capital(self, k):
        params = [self._k, self._j, self._p]
        expr = lambdify(params, self._accrued_capital, "numpy")
        j = self._rate_conversion.subs({self._i:self._interest, self._m:52})
        p = self.payment()
        return expr(k, j, p)
