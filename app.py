from datetime import datetime
from pathlib import Path

from PySide6 import QtWidgets, QtGui

from cash_flow import load_cashflow, CashFlow
from constants import CASH_DIR


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyBank")
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.css()
        self.setup_connections()

    def create_widgets(self):
        self.cbb_open_json = QtWidgets.QComboBox()
        self.prg_remaining_money = QtWidgets.QProgressBar()
        self.le_name = QtWidgets.QLineEdit()
        self.le_price = QtWidgets.QLineEdit()
        self.btn_add_money = QtWidgets.QPushButton("Ajouter")
        self.lw_cashflow = QtWidgets.QListWidget()
        self.lw_cashflow.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.lb_info = QtWidgets.QLabel()
        self.lb_date = QtWidgets.QLabel()
        self.btn_delete = QtWidgets.QPushButton('Supprimer')
        self.lb_picture_money = QtWidgets.QLabel()

    def modify_widgets(self):
        self.le_name.setPlaceholderText("Lieu")
        self.le_price.setPlaceholderText("€")
        self.populate_select_cashflow()
        self.loading_current_file()
        picture = QtGui.QPixmap("money.png")
        self.lb_picture_money.setPixmap(picture)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.cbb_open_json, 0, 0, 1, 2)
        self.main_layout.addWidget(self.le_name, 1, 0, 1, 1)
        self.main_layout.addWidget(self.le_price, 1, 1, 1, 1)
        self.main_layout.addWidget(self.btn_add_money, 2, 0, 1, 2)
        self.main_layout.addWidget(self.lw_cashflow, 3, 0, 1, 2)
        self.main_layout.addWidget(self.btn_delete, 4, 0, 1, 2)
        self.main_layout.addWidget(self.lb_picture_money, 5, 0, 1, 1)
        self.main_layout.addWidget(self.lb_info, 5, 1, 1, 1)
        self.main_layout.addWidget(self.prg_remaining_money, 6, 0, 1, 2)

    def setup_connections(self):
        self.cbb_open_json.activated.connect(self.populate_lw_cashflow)
        self.btn_add_money.clicked.connect(self.add_money)
        self.btn_delete.clicked.connect(self.delete_value)

    def populate_select_cashflow(self):
        self.months = {"01": "Janvier", "02": "F\xe9vrier", "03": "Mars", "04": "Avril", "05": "Mai", "06": "Juin",
                       "07": "Juillet", "08": "Ao\xfbt", "09": "Septembre", "10": "Octobre", "11": "Novembre",
                       "12": "D\xe9cembre"}
        years = [i + datetime.now().year for i in range(2)]
        for year in years:
            for month in self.months.values():
                new_element = f"{month.upper()} {year}"
                self.cbb_open_json.addItem(new_element)

    def loading_current_file(self):
        current_month = self.months.get(str(datetime.now().month).zfill(2)).upper()
        get_current_file = Path(CASH_DIR / f"{current_month}_{datetime.now().year}.json")
        if get_current_file.exists():
            self.populate_lw_cashflow(get_current_file, True)
        else:
            self.cbb_open_json.setCurrentIndex(datetime.now().month - 1)
            self.populate_lw_cashflow()

    def css(self):
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

    def create_layouts(self):
        self.main_layout = QtWidgets.QGridLayout(self)

    def populate_lw_cashflow(self, path=Path(), direct_path=False):
        self.lw_cashflow.clear()

        if direct_path:
            file_path = path
            self.cbb_open_json.setCurrentIndex(datetime.now().month - 1)
        else:
            file_name = self.cbb_open_json.currentText().replace(" ", "_")
            file_path = CASH_DIR / f"{file_name}.json"
            cashflow_name_splited = file_name.split("_")
            CashFlow(cashflow_name_splited[0], cashflow_name_splited[1])

        self.CashFlow = load_cashflow(file_path)
        self.CashFlow.cash_id = self.CashFlow["parameters"].get("cash_id")

        elements = [i for i in self.CashFlow["cashflow"].items()]
        sep = " "
        for element in elements:
            sep1 = sep2 = sep * 10
            if "-" in str(element[1][1]):
                sep1 = sep1[:9]
                sep2 = sep * 11
            lw_item = f"{element[0]}{sep1}{element[1][1]}€{sep2}{element[1][0]}"
            self.lw_cashflow.addItem(lw_item)
        self.update_widgets()

    def update_widgets(self):
        self.positive_values = [p for p in (list(self.CashFlow.get_cash())) if "-" not in str(p)]
        self.negative_values = [p for p in (list(self.CashFlow.get_cash())) if "-" in str(p)]
        if not self.CashFlow.get_cash(sum_=True):
            self.lb_info.setText(f"Somme restante : 0€")
            self.prg_remaining_money.setValue(0)
        elif self.CashFlow.get_cash(sum_=True) < 0:
            self.prg_remaining_money.setRange(0, 1)
            self.prg_remaining_money.setValue(1)
            self.lb_info.setText(f"Somme restante : {(sum(self.positive_values)) - sum(self.negative_values) * -1}€")
        else:
            self.lb_info.setText(f"Somme restante : {(sum(self.positive_values)) - sum(self.negative_values) * -1}€")
            self.prg_remaining_money.setRange(0, sum(self.positive_values))
            if sum(self.negative_values) * -1 >= sum(self.positive_values):
                self.prg_remaining_money.setValue(sum(self.positive_values))
                return
            self.prg_remaining_money.setValue(sum(self.negative_values) * -1)

    def add_money(self):
        name = self.le_name.text()
        price = self.le_price.text()
        try:
            price = float(price)
        except ValueError:
            self.lb_info.setText("ERREUR, veuillez entrer un nombre valide.")
        else:
            if self.le_name.text() == "":
                name = "empty"
            self.CashFlow.add_cash(name, price)
            self.CashFlow.sav_cashflow()
            self.lw_cashflow.clear()
            self.populate_lw_cashflow()
            self.update_widgets()

    def delete_value(self):
        for selected_item in self.lw_cashflow.selectedItems():
            item_id = selected_item.text().split(" ")[0]
            if self.CashFlow["cashflow"].get(item_id):
                self.CashFlow["cashflow"].pop(item_id)
                self.CashFlow.sav_cashflow()
            self.lw_cashflow.takeItem(self.lw_cashflow.row(selected_item))
            self.update_widgets()
            

app = QtWidgets.QApplication([])
window = MainWindow()
window.show()
app.exec_()
