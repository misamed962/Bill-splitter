import webview
import json
import os

DATA_FILE = "data.json"

MENU = [
    {"id": 1, "name": "Салат «Греческий»", "price": 250},
    {"id": 2, "name": "Салат «Цезарь»", "price": 300},
    {"id": 3, "name": "Салат «Морской коктейль»", "price": 350},
    {"id": 4, "name": "Салат Капрезе", "price": 590},
    {"id": 5, "name": "Салат с осьминогом", "price": 750},
    {"id": 6, "name": "Борщ со сметаной", "price": 220},
    {"id": 7, "name": "Суп-лапша куриная", "price": 220},
    {"id": 8, "name": "Рассольник", "price": 220},
    {"id": 9, "name": "Грибной крем-суп", "price": 380},
    {"id": 10, "name": "Том-Ям с морепродуктами", "price": 480},
    {"id": 11, "name": "Пицца «Маргарита»", "price": 530},
    {"id": 12, "name": "Пицца «Карбонара»", "price": 710},
    {"id": 13, "name": "Пицца «Мясная»", "price": 540},
    {"id": 14, "name": "Пицца «4 сыра»", "price": 720},
    {"id": 15, "name": "Спагетти «Карбонара»", "price": 680},
    {"id": 16, "name": "Пенне с лососем", "price": 680},
    {"id": 17, "name": "Мясо по-Рузски", "price": 220},
    {"id": 18, "name": "Котлета куриная", "price": 190},
    {"id": 19, "name": "Рыбная котлета", "price": 185},
    {"id": 20, "name": "Люля из баранины", "price": 850},
    {"id": 21, "name": "Каре ягнёнка", "price": 1350},
    {"id": 22, "name": "Стейк из свиной шеи", "price": 850},
    {"id": 23, "name": "Осьминог с картофелем", "price": 1100},
    {"id": 24, "name": "Картофельное пюре", "price": 165},
    {"id": 25, "name": "Медовик", "price": 480}
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"accounts": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        print("Ошибка чтения data.json, создаём пустой файл.")
        return {"accounts": {}}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка записи data.json: {e}")

class Api:
    def __init__(self):
        self.data = load_data()

    def get_menu(self):
        return MENU

    def register(self, name, tables):
        name = (name or "").strip()
        if not name:
            return {"ok": False, "error": "ФИО не может быть пустым"}
        if name in self.data["accounts"]:
            return {"ok": False, "error": "Сотрудник с таким ФИО уже существует"}
        self.data["accounts"][name] = {
            "tables": tables,
            "guests": {},
            "orders": {}
        }
        save_data(self.data)
        return {"ok": True}

    def login(self, name):
        name = (name or "").strip()
        acc = self.data["accounts"].get(name)
        if not acc:
            return {"ok": False, "error": "Учетная запись не найдена"}
        return {"ok": True, "account": acc}

    def update_schema(self, name, new_tables):
        if name not in self.data["accounts"]:
            return {"ok": False, "error": "Учетная запись не найдена"}
        self.data["accounts"][name]["tables"] = new_tables
        self.data["accounts"][name]["guests"] = {}
        self.data["accounts"][name]["orders"] = {}
        save_data(self.data)
        return {"ok": True}

    def add_guest(self, name, table_id, seat_id, guest_name):
        acc = self.data["accounts"][name]
        t_id, s_id = str(table_id), str(seat_id)
        
        if t_id not in acc["guests"]:
            acc["guests"][t_id] = {}
        if s_id not in acc["guests"][t_id]:
            acc["guests"][t_id][s_id] = []
            
        if len(acc["guests"][t_id][s_id]) >= 2:
            return {"ok": False, "error": "Максимум 2 гостя на одно посадочное место"}
            
        acc["guests"][t_id][s_id].append(guest_name)
        save_data(self.data)
        return {"ok": True, "guests": acc["guests"][t_id][s_id]}

    def remove_guest(self, name, table_id, seat_id, guest_index):
        acc = self.data["accounts"][name]
        t_id, s_id = str(table_id), str(seat_id)
        try:
            acc["guests"][t_id][s_id].pop(guest_index)
            if t_id in acc["orders"] and s_id in acc["orders"][t_id]:
                acc["orders"][t_id][s_id].pop(str(guest_index), None)
            save_data(self.data)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def add_order(self, name, table_id, seat_id, guest_index, dish_id):
        acc = self.data["accounts"][name]
        t_id, s_id, g_idx = str(table_id), str(seat_id), str(guest_index)
        
        seat_orders = acc["orders"].setdefault(t_id, {}).setdefault(s_id, {})
        guest_orders = seat_orders.setdefault(g_idx, [])
        
        # Защита от дубликатов
        if dish_id in guest_orders:
            return {"ok": True}
        
        guest_orders.append(dish_id)
        save_data(self.data)
        return {"ok": True}

    def get_bill(self, name, table_id, seat_id=None):
        acc = self.data["accounts"][name]
        t_id = str(table_id)
        
        def calc_for_seat(s_id):
            total = 0
            items = []
            seat_orders = acc["orders"].get(t_id, {}).get(s_id, {})
            for g_idx, dishes in seat_orders.items():
                for d_id in dishes:
                    dish = next((d for d in MENU if d["id"] == d_id), None)
                    if dish is None:
                        continue
                    total += dish["price"]
                    items.append(f"{dish['name']} — {dish['price']}₽")
            return total, items

        if seat_id is not None:
            total, items = calc_for_seat(str(seat_id))
            guests = acc["guests"].get(t_id, {}).get(str(seat_id), [])
            count = len(guests) if guests else 1
            return {"total": total, "avg": round(total / count, 2), "items": items, "guests": guests}
        else:
            total_all = 0
            items_all = []
            guests_all = []
            seats = acc["guests"].get(t_id, {})
            for s_id, g_list in seats.items():
                guests_all.extend(g_list)
                t, i = calc_for_seat(s_id)
                total_all += t
                items_all.extend(i)
            
            count_all = len(guests_all) if guests_all else 1
            return {"total": total_all, "avg": round(total_all / count_all, 2), "items": items_all, "guests_count": count_all}

if __name__ == "__main__":
    api = Api()
    webview.create_window("Разделитель счетов", "index.html", js_api=api, width=1100, height=850)
    webview.start()
