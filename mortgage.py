import sympy
from sympy import Symbol, lambdify, simplify
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

        self.payment, self.j = self.set_up()
        self.k = Symbol('k', integer=True)
        self._present_value = simplify(loan*(1+self.j)**self.k + self.payment*(1-(1+self.j)**self.k)/self.j)
        self._accrued_interest = simplify(loan*((1+self.j)**self.k-1) + self.payment*(self.k-((1+self.j)**self.k - 1)/self.j))
        self._accrued_capital = simplify(self.k * self.payment - self._accrued_interest)

    def set_up(self):
        i = Symbol('i', float=True)
        m = Symbol('m', integer=True)
        expr = (1 + i/2.0)**(2.0/m) - 1
        if self.modality == Modality.accelerated_weekly:
            j = expr.subs({i:self._interest, m:12})
            annuity = (1-(1 + j)**(-self.term * 12))/j
            payment = self.loan / annuity / 4
            return payment, expr.subs({i:self._interest, m:52})

    def interest(self, k):
        expr = lambdify([self.k], self._present_value, "numpy")
        return expr(k-1) * self.j

    def capital(self, k):
        return self.payment - self.interest(k)

    def accrued_interest(self, k):
        expr = lambdify([self.k], self._accrued_interest, "numpy")
        return expr(k)

    def accrued_capital(self, k):
        expr = lambdify([self.k], self._accrued_capital, "numpy")
        return expr(k)
