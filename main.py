"""PyQt5 coffee machine with stock, payment, and change management."""

import sys
from collections import Counter

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class CoffeeMachine:
    """Store coffee recipes, ingredients, cash, and purchase operations."""

    EXTRA_MILK_PRICE = 1000
    MAX_CAPACITY = {
        "water": 5000,
        "milk": 2000,
        "sugar": 500,
        "cups": 20,
        "coffee_beans": 500,
        "cacao_beans": 500,
    }
    MAX_BILLS_PER_DENOMINATION = 20
    MAX_COINS = 100
    RECIPES = {
        "Еспресо": {"water": 250, "milk": 0, "beans": 16, "price": 4000},
        "Лате": {"water": 350, "milk": 75, "beans": 20, "price": 7000},
        "Капучино": {"water": 200, "milk": 100, "beans": 12, "price": 6000},
        "Американо": {"water": 300, "milk": 0, "beans": 16, "price": 5000},
        "Мокачино": {"water": 300, "milk": 75, "beans": 18, "price": 8000},
        "Какао": {"water": 200, "milk": 150, "cacao_beans": 10, "price": 5500},
        "Горячий шоколад": {"water": 100, "milk": 200, "cacao_beans": 15, "price": 6500},
    }
    BILL_DENOMINATIONS = (2000, 5000, 10000, 20000, 50000, 100000)
    CHANGE_BILL_DENOMINATIONS = (100000, 50000, 20000, 10000, 5000, 2000)
    CHANGE_COIN_DENOMINATIONS = (50, 100, 200, 500, 1000)

    def __init__(self):
        self.water = 5000
        self.milk = 2000
        self.sugar = 500
        self.cups = 20
        self.coffee_beans = 500
        self.cacao_beans = 500
        self.money_nal = 0
        self.money_beznal = 0
        self.money = 0
        self.money_bills = Counter({2000: 2, 5000: 1, 10000: 1})
        self.money_coins = Counter({50: 20})
        
    @property
    def available_coins(self):
        return sum(value * count for value, count in self.money_coins.items())

    @property
    def available_bills(self):
        return sum(value * count for value, count in self.money_bills.items())

    def buy(self, coffee_type, payment_method, paid=0, sugar=False, extra_milk=False, paid_bills=None):
        """Prepare a drink after validating stock, payment, and available change."""
        recipe = self.RECIPES[coffee_type]
        required_milk = recipe["milk"] + (500 if extra_milk else 0)
        required_sugar = 10 if sugar else 0
        required_coffee_beans = recipe.get("beans", 0)
        required_cacao_beans = recipe.get("cacao_beans", 0)
        price = recipe["price"] + (self.EXTRA_MILK_PRICE if extra_milk else 0)

        for resource, required, label in (
            (self.water, recipe["water"], "води"),
            (self.milk, required_milk, "молока"),
            (self.coffee_beans, required_coffee_beans, "кавових зерен"),
            (self.cacao_beans, required_cacao_beans, "какао-бобів"),
            (self.sugar, required_sugar, "цукру"),
            (self.cups, 1, "стаканчиків"),
        ):
            if resource < required:
                return False, f"Недостатньо {label}.", 0

        if payment_method == "card":
            change = 0
        else:
            if paid < price:
                return False, f"Внесено недостатньо коштів. Потрібно {price / 100:.2f} грн.", 0
            change = paid - price
            change_parts = self._make_change(change)
            if change_parts is None:
                return False, "Наразі немає купюр і монет для видачі здачі.", 0

        self.water -= recipe["water"]
        self.milk -= required_milk
        self.sugar -= required_sugar
        self.coffee_beans -= required_coffee_beans
        self.cacao_beans -= required_cacao_beans
        self.cups -= 1
        self.money += price
        if payment_method == "card":
            self.money_beznal += price
        else:
            self.money_nal += price
            change_bills, change_coins = change_parts
            for bill, count in change_bills.items():
                self.money_bills[bill] -= count
            for coin, count in change_coins.items():
                self.money_coins[coin] -= count
            for bill, count in (paid_bills or {}).items():
                self.money_bills[bill] += count
        return True, f"Ваш напій готовий: {coffee_type}. Смачного! Здача: {change / 100:.2f} грн.", change

    def _make_change(self, amount):
        """Build a change set from available bills and 50-kopeck coins."""
        bills = Counter()
        coins = Counter()
        remaining = amount
        for denomination in self.CHANGE_BILL_DENOMINATIONS:
            usable = min(self.money_bills[denomination], remaining // denomination)
            bills[denomination] = usable
            remaining -= denomination * usable
        for denomination in self.CHANGE_COIN_DENOMINATIONS:
            usable = min(self.money_coins[denomination], remaining // denomination)
            coins[denomination] = usable
            remaining -= denomination * usable
        return (bills, coins) if remaining == 0 else None

    def fill(self, water, milk, sugar, cups, coffee_beans, cacao_beans, bills, coins):
        """Refill ingredients and money without exceeding machine capacities."""
        before = {
            "water": self.water,
            "milk": self.milk,
            "sugar": self.sugar,
            "cups": self.cups,
            "coffee_beans": self.coffee_beans,
            "cacao_beans": self.cacao_beans,
        }
        for name, amount in (
            ("water", water),
            ("milk", milk),
            ("sugar", sugar),
            ("cups", cups),
            ("coffee_beans", coffee_beans),
            ("cacao_beans", cacao_beans),
        ):
            setattr(self, name, min(self.MAX_CAPACITY[name], getattr(self, name) + amount))
        for denomination, count in bills.items():
            self.money_bills[denomination] = min(
                self.MAX_BILLS_PER_DENOMINATION,
                self.money_bills[denomination] + count,
            )
        for denomination, count in coins.items():
            if denomination == 50:
                self.money_coins[denomination] = min(self.MAX_COINS, self.money_coins[denomination] + count)
        return {
            name: getattr(self, name) - before[name]
            for name in before
        }

    def take(self):
        """Collect recorded revenue and reset the revenue counters."""
        total = self.money
        self.money = self.money_nal = self.money_beznal = 0
        return total


class CoffeeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.machine = CoffeeMachine()
        self.status_window = None
        self.admin_authenticated = False
        self.setWindowTitle("Кавовий автомат")
        self.setMinimumWidth(560)
        self._build_ui()
        self._refresh_status()

    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)
        title = QLabel("Кавовий автомат")
        title.setObjectName("title")
        root.addWidget(title)

        order_box = QGroupBox("Замовлення")
        order_layout = QFormLayout(order_box)
        service_layout = QGridLayout()
        service_layout.setContentsMargins(12, 20, 12, 12)
        self.coffee = QComboBox()
        for name, recipe in self.machine.RECIPES.items():
            self.coffee.addItem(f"{name} — {recipe['price'] / 100:.2f} грн", name)
        self.sugar = QCheckBox("Додати цукор (+10 г)")
        self.extra_milk = QCheckBox(
            f"Додати молоко (+50 мл, +{self.machine.EXTRA_MILK_PRICE / 100:.2f} грн)"
        )
        self.price_label = QLabel()
        self.payment = QComboBox()
        self.payment.addItem("Готівка", "cash")
        self.payment.addItem("Банківська картка", "card")
        self.bill = QComboBox()
        for denomination in self.machine.BILL_DENOMINATIONS:
            self.bill.addItem(f"{denomination / 100:.0f} грн", denomination)
        self.bill_count = QSpinBox()
        self.bill_count.setRange(1, 10)
        self.bill_count.setValue(1)
        self.buy_button = QPushButton("Приготувати каву")
        self.buy_button.clicked.connect(self._buy)
        self.payment.currentIndexChanged.connect(self._payment_changed)
        self.coffee.currentIndexChanged.connect(self._refresh_price)
        self.extra_milk.toggled.connect(self._refresh_price)
        order_layout.addRow("Напій:", self.coffee)
        order_layout.addRow(self.sugar)
        order_layout.addRow(self.extra_milk)
        order_layout.addRow("До сплати:", self.price_label)
        order_layout.addRow("Оплата:", self.payment)
        order_layout.addRow("Купюра:", self.bill)
        order_layout.addRow("Кількість купюр:", self.bill_count)
        order_layout.addRow(self.buy_button)
        root.addWidget(order_box)

        self.status = QLabel()
        self.status.setWordWrap(True)
        root.addWidget(self.status)

        service_box = QGroupBox("Обслуговування")
        service_layout = QGridLayout(service_box)
        service_layout.setContentsMargins(12, 20, 12, 12)
        self.fill_button = QPushButton("Заправити автомат")
        self.take_button = QPushButton("Забрати виручку")
        self.details_button = QPushButton("Відкрити стан і виручку")
        self.fill_button.clicked.connect(self._fill)
        self.take_button.clicked.connect(self._take)
        self.details_button.clicked.connect(self._show_status_window)
        service_layout.addWidget(self.fill_button, 0, 0)
        service_layout.addWidget(self.take_button, 0, 1)
        service_layout.addWidget(self.details_button, 1, 0, 1, 2)
        root.addWidget(service_box)
        self.setCentralWidget(central)
        self.setStyleSheet("QMainWindow { background: #f5efe6; } QGroupBox { font-weight: bold; margin-top: 10px; } QPushButton { padding: 8px; } #title { font-size: 24px; font-weight: bold; color: #5b321e; }")
        self._refresh_price()

    def _refresh_price(self):
        recipe = self.machine.RECIPES[self.coffee.currentData()]
        price = recipe["price"]
        if self.extra_milk.isChecked():
            price += self.machine.EXTRA_MILK_PRICE
        self.price_label.setText(f"{price / 100:.2f} грн")

    def _payment_changed(self):
        is_cash = self.payment.currentData() == "cash"
        self.bill.setEnabled(is_cash)
        self.bill_count.setEnabled(is_cash)

    def _buy(self):
        paid = 0
        paid_bills = None
        if self.payment.currentData() == "cash":
            denomination = self.bill.currentData()
            count = self.bill_count.value()
            paid = denomination * count
            paid_bills = {denomination: count}
        success, message, _ = self.machine.buy(self.coffee.currentData(), self.payment.currentData(), paid, self.sugar.isChecked(), self.extra_milk.isChecked(), paid_bills)
        (QMessageBox.information if success else QMessageBox.warning)(self, "Кавовий автомат", message)
        self._refresh_status()

    def _fill(self):
        if not self._require_admin():
            return
        added = self.machine.fill(2000, 1000, 300, 10, 200, 200, {2000: 2, 5000: 2, 10000: 1}, {50: 20})
        self._refresh_status()
        if self.status_window:
            self.status_window.refresh()
        QMessageBox.information(
            self,
            "Обслуговування",
            "Поповнення виконано з урахуванням максимальних місткостей.\n"
            f"Додано: вода {added['water']} мл, молоко {added['milk']} мл, "
            f"цукор {added['sugar']} г, зерна {added['coffee_beans']} г, "
            f"какао-боби {added['cacao_beans']} г, "
            f"стаканчики {added['cups']}.",
        )

    def _take(self):
        if not self._require_admin():
            return
        total = self.machine.take()
        QMessageBox.information(self, "Інкасація", f"Забрано {total / 100:.2f} грн.")
        self._refresh_status()
        if self.status_window:
            self.status_window.refresh()

    def _show_status_window(self):
        if not self._require_admin():
            return
        if self.status_window is None:
            self.status_window = StatusWindow(self.machine)
        self.status_window.refresh()
        self.status_window.show()
        self.status_window.raise_()
        self.status_window.activateWindow()

    def _refresh_status(self):
        self.status.setText("Автомат готовий до замовлення.")

    def _require_admin(self):
        if self.admin_authenticated:
            return True
        dialog = AdminLoginDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return False
        self.admin_authenticated = True
        return True


class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вхід адміністратора")
        self.setModal(True)

        self.login = QLineEdit()
        self.login.setPlaceholderText("Логін")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.Password)
        self.error = QLabel()
        self.error.setStyleSheet("color: #a12626;")

        form = QFormLayout(self)
        form.addRow("Логін:", self.login)
        form.addRow("Пароль:", self.password)
        form.addRow(self.error)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._check_credentials)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _check_credentials(self):
        if self.login.text() == "admin" and self.password.text() == "admin":
            self.accept()
            return
        self.error.setText("Невірний логін або пароль.")
        self.password.clear()
        self.password.setFocus()


class StatusWindow(QDialog):
    def __init__(self, machine):
        super().__init__()
        self.machine = machine
        self.setWindowTitle("Стан автомата і виручка")
        self.setMinimumWidth(420)
        self.details = QLabel()
        self.details.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.details)
        self.refresh()

    def refresh(self):
        machine = self.machine
        resources = (
            ("Вода", machine.water, machine.MAX_CAPACITY["water"], "мл"),
            ("Молоко", machine.milk, machine.MAX_CAPACITY["milk"], "мл"),
            ("Цукор", machine.sugar, machine.MAX_CAPACITY["sugar"], "г"),
            ("Кавові зерна", machine.coffee_beans, machine.MAX_CAPACITY["coffee_beans"], "г"),
            ("Какао-боби", machine.cacao_beans, machine.MAX_CAPACITY["cacao_beans"], "г"),
            ("Стаканчики", machine.cups, machine.MAX_CAPACITY["cups"], "шт."),
        )
        resource_lines = [
            f"{name}: {current} / {maximum} {unit} ({current / maximum * 100:.0f}%)"
            for name, current, maximum, unit in resources
        ]
        self.details.setText(
            "Заповненість запасів:\n"
            + "\n".join(resource_lines)
            + "\n\nВиручка:\n"
            + f"Загалом: {machine.money / 100:.2f} грн\n"
            + f"Готівка: {machine.money_nal / 100:.2f} грн\n"
            + f"Картка: {machine.money_beznal / 100:.2f} грн\n\n"
            + f"Купюри для здачі: {machine.available_bills / 100:.2f} грн\n"
            + f"Монети по 50 копійок: {machine.available_coins / 100:.2f} грн"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoffeeWindow()
    window.show()
    sys.exit(app.exec_())
