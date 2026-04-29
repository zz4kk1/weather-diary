import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "weather_data.json"


class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("650x500")

        self.records = self.load_data()

        self.setup_ui()
        self.update_table()

    def setup_ui(self):
        # --- Фрейм для ввода данных ---
        input_frame = tk.LabelFrame(self.root, text="Добавить запись", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w")
        self.date_entry = tk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w")
        self.temp_entry = tk.Entry(input_frame)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Описание погоды:").grid(row=1, column=0, sticky="w")
        self.desc_entry = tk.Entry(input_frame)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Осадки:").grid(row=1, column=2, sticky="w")
        self.precip_combobox = ttk.Combobox(input_frame, values=["Да", "Нет"], state="readonly")
        self.precip_combobox.grid(row=1, column=3, padx=5, pady=5)
        self.precip_combobox.set("Нет")

        add_btn = tk.Button(input_frame, text="Добавить запись", command=self.add_record, bg="#4CAF50", fg="white")
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)

        # --- Фрейм для фильтрации ---
        filter_frame = tk.LabelFrame(self.root, text="Фильтры", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Дата:").grid(row=0, column=0, sticky="w")
        self.filter_date_entry = tk.Entry(filter_frame)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, sticky="w")
        self.filter_temp_entry = tk.Entry(filter_frame)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)

        filter_btn = tk.Button(filter_frame, text="Применить", command=self.apply_filters)
        filter_btn.grid(row=0, column=4, padx=5)

        reset_btn = tk.Button(filter_frame, text="Сбросить", command=self.update_table)
        reset_btn.grid(row=0, column=5, padx=5)

        # --- Таблица (Treeview) ---
        columns = ("date", "temp", "desc", "precip")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=12)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")

        self.tree.column("date", width=100, anchor="center")
        self.tree.column("temp", width=120, anchor="center")
        self.tree.column("desc", width=250, anchor="w")
        self.tree.column("precip", width=80, anchor="center")

    def add_record(self):
        date_str = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc_str = self.desc_entry.get().strip()
        precip_str = self.precip_combobox.get()

        # Валидация: Дата
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            return

        # Валидация: Температура
        try:
            temp_val = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return

        # Валидация: Описание
        if not desc_str:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым!")
            return

        record = {
            "date": date_str,
            "temp": temp_val,
            "desc": desc_str,
            "precip": precip_str
        }

        self.records.append(record)
        self.save_data()
        self.update_table()

        # Очистка полей ввода (кроме даты и осадков)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    def apply_filters(self):
        f_date = self.filter_date_entry.get().strip()
        f_temp_str = self.filter_temp_entry.get().strip()

        filtered = self.records

        if f_date:
            filtered = [r for r in filtered if r['date'] == f_date]

        if f_temp_str:
            try:
                min_temp = float(f_temp_str)
                filtered = [r for r in filtered if r['temp'] > min_temp]
            except ValueError:
                messagebox.showerror("Ошибка фильтра", "Температура для фильтра должна быть числом!")
                return

        self.update_table(filtered)

    def update_table(self, data=None):
        if data is None:
            data = self.records
            self.filter_date_entry.delete(0, tk.END)
            self.filter_temp_entry.delete(0, tk.END)

        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполняем таблицу
        for row in data:
            self.tree.insert("", tk.END, values=(row["date"], row["temp"], row["desc"], row["precip"]))

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(self.records, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()