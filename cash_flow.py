import json

from constants import*


def get_cashflow():
    return [j for j in CASH_DIR.glob("*") if j.suffix == ".json"]


def load_cashflow(path):
    with open(path, "r") as f:
        content = json.load(f)
        month = content["parameters"]["init"][0]
        year = content["parameters"]["init"][1]
        new_cashflow = CashFlow(month, year)
        new_cashflow["parameters"] = content["parameters"]
        new_cashflow["cashflow"] = content["cashflow"]
        return new_cashflow


class CashFlow(dict):
    def __init__(self, month, year):
        super().__init__()
        self.month = month.upper()
        self.year = year
        self.cash_id = 0
        self._initialize()

    def _initialize(self):
        if (CASH_DIR / f"{self.month}_{self.year}.json").exists():
            return False
        self["parameters"] = {
            "init": (self.month, self.year),
            "cash_id": []
        }
        self["cashflow"] = {}
        self._update_parameters()
        self.sav_cashflow()

    def _update_parameters(self):
        self["parameters"]["cash_id"] = self.cash_id

    def add_cash(self, name, price):
        self.cash_id += 1
        cash_id = str(self.cash_id).zfill(3)
        self["cashflow"][cash_id] = [name.upper(), price]
        self._update_parameters()
        self.sav_cashflow()

    def remove_cash(self, cash_id):
        if self["cashflow"].get(cash_id):
            self["cashflow"].pop(cash_id)
            self.sav_cashflow()

    def sav_cashflow(self):
        file_name = f"{self.month}_{self.year}.json"
        with open(CASH_DIR / file_name, "w") as f:
            json.dump(self, f, indent=4)

    def get_cash(self, sum_=False):
        all_cashflow = (element[1] for element in self["cashflow"].values())
        if sum_:
            return sum(all_cashflow)
        return all_cashflow
