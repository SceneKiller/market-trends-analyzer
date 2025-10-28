from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InvestmentType(Enum):
    DEPOSIT = "bank_deposit"
    BONDS = "bonds"
    ETF = "etf"


@dataclass
class FinancialProduct:
    id: str
    name: str
    type: InvestmentType
    risk_level: RiskLevel
    interest_rate: float
    min_amount: float
    max_amount: Optional[float] = None
    duration_days: Optional[int] = None
    is_replenishable: bool = False
    is_withdrawable: bool = False
    issuer: str = ""


class ConsoleFinancialAssistant:
    def __init__(self):
        self.products = self._load_products()
        self.current_user = None

    def _load_products(self) -> List[FinancialProduct]:
        """Загрузка тестовых данных о продуктах"""

        #todo пример вывода, добавить в будущем настоящий анализатор по апи тинька
        return [
            FinancialProduct(
                id="1",
                name="Вклад 'Надежный'",
                type=InvestmentType.DEPOSIT,
                risk_level=RiskLevel.LOW,
                interest_rate=5.5,
                min_amount=10000,
                duration_days=365,
                is_replenishable=True,
                issuer="Сбербанк"
            ),
            FinancialProduct(
                id="2",
                name="Облигации РФ",
                type=InvestmentType.BONDS,
                risk_level=RiskLevel.LOW,
                interest_rate=7.2,
                min_amount=50000,
                duration_days=730,
                issuer="МинФин"
            ),
            FinancialProduct(
                id="3",
                name="ETF на золото",
                type=InvestmentType.ETF,
                risk_level=RiskLevel.MEDIUM,
                interest_rate=9.1,
                min_amount=5000,
                is_withdrawable=True,
                issuer="Тинькофф"
            )
        ]

    def start(self):
        """Запуск консольного интерфейса"""
        print("=== Финансовый помощник ===")
        print("Анализируем варианты вложения денег с минимальным риском\n")

        while True:
            self._collect_user_data()
            recommendations = self._get_recommendations()
            self._show_recommendations(recommendations)

            if not self._ask_to_continue():
                break

    def _collect_user_data(self):
        """Сбор данных от пользователя"""
        print("\n=== Введите ваши параметры ===")

        # Выбор уровня риска
        print("\nВыберите уровень риска:")
        print("1. Консервативный (минимальный риск)")
        print("2. Умеренный")
        print("3. Агрессивный (высокая доходность)")

        risk_choice = input("Ваш выбор (1-3): ")
        while risk_choice not in ["1", "2", "3"]:
            print("Пожалуйста, введите 1, 2 или 3")
            risk_choice = input("Ваш выбор (1-3): ")

        risk_map = {"1": RiskLevel.LOW, "2": RiskLevel.MEDIUM, "3": RiskLevel.HIGH}

        # Сумма инвестирования
        amount = input("\nКакую сумму вы готовы инвестировать (руб): ")
        while not amount.isdigit() or float(amount) <= 0:
            print("Пожалуйста, введите положительное число")
            amount = input("Какую сумму вы готовы инвестировать (руб): ")

        # Срок инвестирования
        duration = input("\nЖелаемый срок вложения в днях (0 если неважно): ")
        while not duration.isdigit() or float(amount) <= 0:
            print("Пожалуйста, введите число дней")
            duration = input("Желаемый срок вложения в днях: ")

        self.current_user = {
            "risk_level": risk_map[risk_choice],
            "amount": float(amount),
            "duration": int(duration) if int(duration) > 0 else None
        }

    def _get_recommendations(self) -> List[FinancialProduct]:
        """Получение рекомендаций на основе введенных данных"""
        filtered = [
            p for p in self.products
            if p.risk_level == self.current_user["risk_level"]
               and p.min_amount <= self.current_user["amount"]
        ]

        if self.current_user["duration"]:
            filtered = [
                p for p in filtered
                if p.duration_days is None
                   or p.duration_days >= self.current_user["duration"]
            ]

        return sorted(filtered, key=lambda x: x.interest_rate, reverse=True)[:3]

    def _show_recommendations(self, products: List[FinancialProduct]):
        """Вывод рекомендаций пользователю"""
        print("\n=== Рекомендуемые варианты ===")

        if not products:
            print("К сожалению, нет подходящих продуктов для ваших критериев")
            return

        for i, product in enumerate(products, 1):
            print(f"\n{i}. {product.name} ({product.issuer})")
            print(f"   Тип: {product.type.value}")
            print(f"   Процентная ставка: {product.interest_rate}% годовых")
            print(f"   Минимальная сумма: {product.min_amount} руб.")

            if product.duration_days:
                print(f"   Срок: {product.duration_days} дней")

            features = []
            if product.is_replenishable:
                features.append("пополнение")
            if product.is_withdrawable:
                features.append("частичное снятие")

            if features:
                print(f"   Возможности: {', '.join(features)}")

    def _ask_to_continue(self) -> bool:
        """Запрос на продолжение работы"""
        choice = input("\nХотите сделать еще один подбор? (да/нет): ").lower()
        while choice not in ["да", "нет"]:
            print("Пожалуйста, введите 'да' или 'нет'")
            choice = input("Хотите сделать еще один подбор? (да/нет): ").lower()

        return choice == "да"


if __name__ == "__main__":
    assistant = ConsoleFinancialAssistant()
    assistant.start()
    print("\nСпасибо за использование финансового помощника!")