from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from pathlib import Path


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        model_json = model.model_dump_json()
        models_path = Path(self.root_directory_path) / "models.txt"
        index_path = Path(self.root_directory_path) / "models_index.txt"

        with open(
            models_path,
            "a+",
            encoding="utf-8",
            newline="\n"
        ) as file:
            file.seek(0)
            lines = file.readlines()
            line_number = len(lines)
            file.write(model_json.ljust(500) + "\n")

        with open(index_path, "a+", encoding="utf-8") as index_file:
            index_file.seek(0)
            index_lines = index_file.readlines()
            index_lines.append(f"{model.index()} {line_number}\n")

            def get_id(line):
                parts = line.split()
                return int(parts[0])
            index_lines.sort(key=get_id)

        with open(index_path, "w", encoding="utf-8") as index_file:
            for line in index_lines:
                index_file.write(line)
        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        car_json = car.model_dump_json()
        cars_path = Path(self.root_directory_path) / "cars.txt"
        index_car_path = Path(self.root_directory_path) / "cars_index.txt"

        with open(
            cars_path,
            "a+",
            encoding="utf-8",
            newline="\n"
        ) as file:
            file.seek(0)
            lines = file.readlines()
            line_number = len(lines)
            file.write(car_json.ljust(500) + "\n")

        with open(index_car_path, "a+", encoding="utf-8") as index_file:
            index_file.seek(0)
            index_lines = index_file.readlines()
            index_lines.append(f"{car.index()} {line_number}\n")
            index_lines.sort()

        with open(index_car_path, "w", encoding="utf-8") as index_file:
            for line in index_lines:
                index_file.write(line)
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        sale_json = sale.model_dump_json()
        sales_path = Path(self.root_directory_path) / "sales.txt"
        sales_index_path = Path(self.root_directory_path) / "sales_index.txt"
        index_car_path = Path(self.root_directory_path) / "cars_index.txt"
        car_path = Path(self.root_directory_path) / "cars.txt"

        with open(sales_path, "a+", encoding="utf-8") as file:
            file.seek(0)
            lines = file.readlines()
            line_number = len(lines)
            file.write(sale_json.ljust(500) + "\n")

        with open(sales_index_path, "a+", encoding="utf-8") as index_file:
            index_file.seek(0)
            index_lines = index_file.readlines()
            index_lines.append(f"{sale.index()} {line_number}\n")
            index_lines.sort()

        with open(sales_index_path, "w", encoding="utf-8") as index_file:
            for line in index_lines:
                index_file.write(line)

        with open(index_car_path, "r", encoding="utf-8") as car_index_file:
            car_index_lines = car_index_file.readlines()
            for vin in car_index_lines:
                parts = vin.split()
                if parts[0] == sale.index():
                    car_line_number = int(parts[-1])

        with open(car_path, "r", encoding="utf-8") as car_file:
            car_file.seek(car_line_number * 501)
            car_json = car_file.read(500)

        car = Car.model_validate_json(car_json)
        car.status = CarStatus.sold
        car_json = car.model_dump_json()

        with open(
            car_path,
            "r+",
            encoding="utf-8",
            newline="\n"
        ) as car_file:
            car_file.seek(car_line_number * 501)
            car_file.write(car_json.ljust(500) + "\n")
        return car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        car_path = Path(self.root_directory_path) / "cars.txt"
        available_cars = []

        with open(car_path, "r", encoding="utf-8") as car_file:
            for line in car_file:
                car = Car.model_validate_json(line)
                if car.status == status:
                    available_cars.append(car)
        return available_cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        index_car_path = Path(self.root_directory_path) / "cars_index.txt"
        car_path = Path(self.root_directory_path) / "cars.txt"
        model_path = Path(self.root_directory_path) / "models.txt"
        index_model_path = Path(self.root_directory_path) / "models_index.txt"
        sales_path = Path(self.root_directory_path) / "sales.txt"
        car_line_number = None

        with open(index_car_path, "r", encoding="utf-8") as index_file:
            for line in index_file:
                parts = line.split()
                if parts[0] == vin:
                    car_line_number = int(parts[-1])
        if car_line_number is None:
            return None

        with open(car_path, "r", encoding="utf-8") as car_file:
            car_file.seek(car_line_number * 501)
            car_json = car_file.read(500)
            car = Car.model_validate_json(car_json)

        with open(index_model_path, "r", encoding="utf-8") as index_model_file:
            for line in index_model_file:
                parts = line.split()
                if int(parts[0]) == car.model:
                    model_line_number = int(parts[-1])

        with open(model_path, "r", encoding="utf-8") as model_file:
            model_file.seek(model_line_number * 501)
            model_json = model_file.read(500)
            model = Model.model_validate_json(model_json)
        sales_date = None
        sales_cost = None
        if car.status == CarStatus.sold:
            with open(sales_path, "r", encoding="utf-8") as sale_file:
                for line in sale_file:
                    sale = Sale.model_validate_json(line)
                    if sale.car_vin == car.vin:
                        sales_date = sale.sales_date
                        sales_cost = sale.cost
        return CarFullInfo(
            vin=car.vin, car_model_name=model.name,
            car_model_brand=model.brand, price=car.price,
            date_start=car.date_start, status=car.status,
            sales_date=sales_date, sales_cost=sales_cost
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        index_car_path = Path(self.root_directory_path) / "cars_index.txt"
        car_path = Path(self.root_directory_path) / "cars.txt"

        with open(index_car_path, "r", encoding="utf-8") as index_file:
            for line in index_file:
                parts = line.split()
                if parts[0] == vin:
                    car_line_number = int(parts[-1])
                    break

        with open(car_path, "r", encoding="utf-8") as car_file:
            car_file.seek(car_line_number * 501)
            car_json = car_file.read(500)
            car = Car.model_validate_json(car_json)
            car.vin = new_vin
            car_json = car.model_dump_json()

        with open(
            car_path,
            "r+",
            encoding="utf-8",
            newline="\n"
        ) as car_file:
            car_file.seek(car_line_number * 501)
            car_file.write(car_json.ljust(500) + "\n")

        with open(index_car_path, "r", encoding="utf-8") as index_file:
            index_lines = index_file.readlines()
            for i, line in enumerate(index_lines):
                parts = line.split()
                if parts[0] == vin:
                    index_lines[i] = f"{new_vin} {parts[-1]}\n"
            index_lines.sort()

        with open(index_car_path, "w", encoding="utf-8") as index_file:
            index_file.writelines(index_lines)
        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        sales_path = Path(self.root_directory_path) / "sales.txt"
        sales_index_path = Path(self.root_directory_path) / "sales_index.txt"
        index_car_path = Path(self.root_directory_path) / "cars_index.txt"
        car_path = Path(self.root_directory_path) / "cars.txt"

        with open(sales_path, "r", encoding="utf-8") as sale_file:
            sales_lines = sale_file.readlines()
            remaining_sales = []
            for sales in sales_lines:
                sale = Sale.model_validate_json(sales)
                if sale.sales_number == sales_number:
                    car_vin = sale.car_vin
                else:
                    remaining_sales.append(sales)

        with open(sales_path, "w", encoding="utf-8") as sale_file:
            sale_file.writelines(remaining_sales)
        sales_index_lines = []
        for line_number, sale_new in enumerate(remaining_sales):
            sales_index = Sale.model_validate_json(sale_new)
            sales_index_lines.append(f"{sales_index.index()} {line_number}\n")

        sales_index_lines.sort()

        with open(sales_index_path, "w", encoding="utf-8") as index_file:
            index_file.writelines(sales_index_lines)

        with open(index_car_path, "r", encoding="utf-8") as index_car_file:
            for line in index_car_file:
                parts = line.split()
                if parts[0] == car_vin:
                    car_line_number = int(parts[-1])
                    break

        with open(car_path, "r", encoding="utf-8") as car_file:
            car_file.seek(car_line_number * 501)
            car_json = car_file.read(500)

        car = Car.model_validate_json(car_json)
        car.status = CarStatus.available
        car_json = car.model_dump_json()

        with open(
            car_path,
            "r+",
            encoding="utf-8",
            newline="\n"
        ) as car_file:
            car_file.seek(car_line_number * 501)
            car_file.write(car_json.ljust(500) + "\n")
        return car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        sales_path = Path(self.root_directory_path) / "sales.txt"
        index_car_path = Path(self.root_directory_path) / "cars_index.txt"
        car_path = Path(self.root_directory_path) / "cars.txt"
        model_path = Path(self.root_directory_path) / "models.txt"
        index_model_path = Path(self.root_directory_path) / "models_index.txt"
        model_count: dict[int, int] = {}
        model_prices = {}

        with open(sales_path, "r", encoding="utf-8") as sale_file:
            for sale in sale_file:
                sale_obj = Sale.model_validate_json(sale)
                car_vin = sale_obj.car_vin
                with open(
                    index_car_path,
                    "r",
                    encoding="utf-8"
                ) as index_car_file:
                    for line in index_car_file:
                        parts = line.split()
                        if parts[0] == car_vin:
                            car_line_number = int(parts[-1])
                            break
                with open(car_path, "r", encoding="utf-8") as car_file:
                    for number, line in enumerate(car_file):
                        if number == car_line_number:
                            car_json = line.strip()
                            break

                    car = Car.model_validate_json(car_json)

                model_id = car.model
                model_prices[model_id] = car.price

                if model_id in model_count:
                    model_count[model_id] += 1
                else:
                    model_count[model_id] = 1

        sorted_prices = sorted(
            model_prices,
            key=model_prices.__getitem__,
            reverse=True
        )
        sorted_prices.sort(
            key=model_count.__getitem__,
            reverse=True
        )
        top_3 = sorted_prices[:3]
        result = []

        for model_id in top_3:
            with open(
                index_model_path,
                "r",
                encoding="utf-8"
            ) as index_model_file:
                for line in index_model_file:
                    parts = line.split()
                    if int(parts[0]) == model_id:
                        model_line_number = int(parts[-1])
                        break
            with open(model_path, "r", encoding="utf-8") as model_file:
                model_file.seek(model_line_number * 501)
                model_json = model_file.read(500)
                model_obj = Model.model_validate_json(model_json)

            model_stats = ModelSaleStats(
                car_model_name=model_obj.name,
                brand=model_obj.brand,
                sales_number=model_count[model_id]
            )
            result.append(model_stats)
        return result
