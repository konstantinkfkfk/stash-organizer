import os
import zipfile
from collections import Counter
import shutil
import io
import wave
import re
import customtkinter as ctk
from tkinter import messagebox, filedialog

# --- КОНСТАНТЫ АБСТРАКТНОГО СВЕТЛОГО ДИЗАЙНА ---
BG_MAIN = "#F7F6F2"  # Матовая слоновая кость
BG_PANEL = "#EDEDE6"  # Теплый пепельный винтаж
ACCENT_GREEN = "#5A7861"  # Благородный шалфейно-зеленый
TEXT_MAIN = "#2A2E2B"  # Мягкий графитовый черный
TEXT_MUTED = "#8E948F"  # Пепельный серый для подписей
BORDER_COLOR = "#D1D1C7"  # Тонкие пастельные границы

# Настройка глобальной темы CustomTkinter
ctk.set_appearance_mode("Light")

CATEGORIES = {
    "FX": ["fx", "riser", "fall", "sweep", "transition", "crash", "hit"],
    "Open Hats": ["open hat", "open_hat", "op hat", "op_hat", "openhat", "ophat", "open", "op"],
    "Hi-Hats": ["hihat", "hi_hat", "hi hat", "hat", "hh", "hhat", "closed", "cl_hat", "cl hat"],
    "Snares": ["snare", "snr"],
    "Claps": ["clap", "clp"],
    "Kicks": ["kick", "kck"],
    "808": ["808", "bass", "sub"],
    "Vox": ["vox", "chant", "ch", "vocal", "shout", "choir", "vocals"],
    "Percs": ["perc", "rim", "shaker", "tamb", "snap", "conga"]
}


def get_sample_category(filename):
    name_lower = filename.lower()
    if any(phrase in name_lower for phrase in ["open hat", "open_hat", "op hat", "op_hat", "openhat", "ophat"]):
        return "Open Hats"
    if any(phrase in name_lower for phrase in ["hi hat", "hi_hat", "hihat"]):
        return "Hi-Hats"

    tokens = re.split(r'[_ \-\.\(\)\[\]\+]+', name_lower)
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in tokens:
                return category

    fallback_keywords = {
        "FX": ["fx", "riser", "fall", "sweep", "transition"],
        "Hi-Hats": ["hihat", "hi_hat"],
        "Snares": ["snare"],
        "Claps": ["clap"],
        "Kicks": ["kick", "kck"],
        "808": ["808", "bass", "sub"],
        "Vox": ["vox", "chant"],
        "Percs": ["perc", "shaker", "tamb"]
    }
    for category, keywords in fallback_keywords.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "Unsorted"


def get_wav_duration_from_zip(zip_path, file_in_zip):
    try:
        with zipfile.ZipFile(zip_path, 'r') as archive:
            file_bytes = archive.read(file_in_zip)
            with wave.open(io.BytesIO(file_bytes), 'rb') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                if rate > 0:
                    return frames / float(rate)
    except Exception:
        pass
    return None


class RetroStashApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("STASH EXTRACTOR // РУССКАЯ ВЕРСИЯ")
        self.geometry("640x580")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)

        self.source_dir = ctk.StringVar(value=os.path.expanduser("~/Documents"))
        self.target_dir = ctk.StringVar(value=os.path.expanduser("~/Documents"))

        # --- ВЕРХНЯЯ ШАПКА ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(30, 15))

        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="С Т Э Ш  //  О Р Г А Н А Й З Е Р",
            font=ctk.CTkFont(family="Courier New", size=18, weight="bold"),
            text_color=TEXT_MAIN
        )
        self.header_title.pack(anchor="w")

        self.header_subtitle = ctk.CTkLabel(
            self.header_frame,
            text="[ МОДУЛЬНЫЙ ФИЛЬТР ОТКЛЮЧЕН. СИСТЕМА СОРТИРУЕТ ВСЕ КАТЕГОРИИ ]",
            font=ctk.CTkFont(family="Courier New", size=9),
            text_color=TEXT_MUTED
        )
        self.header_subtitle.pack(anchor="w", pady=(2, 0))

        # --- ИНФОРМАЦИОННОЕ ТАБЛО ---
        self.info_panel = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=6
        )
        self.info_panel.pack(fill="x", padx=30, pady=5)

        self.status_display = ctk.CTkLabel(
            self.info_panel,
            text="СТАТУС: ГОТОВ К РАБОТЕ\nПожалуйста, выберите папки импорта и экспорта в меню ниже.",
            font=ctk.CTkFont(family="Helvetica", size=11),
            text_color=ACCENT_GREEN,
            justify="left",
            anchor="w"
        )
        self.status_display.pack(fill="x", padx=20, pady=15)

        # --- ПАНЕЛЬ НАСТРОЕК (ЦЕНТРАЛЬНАЯ) ---
        self.config_panel = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=6
        )
        self.config_panel.pack(fill="both", expand=True, padx=30, pady=10)

        # 1. Сетка параметров ввода
        self.inputs_grid = ctk.CTkFrame(self.config_panel, fg_color="transparent")
        self.inputs_grid.pack(fill="x", padx=20, pady=20)

        # Название кита
        self.nick_label = ctk.CTkLabel(
            self.inputs_grid,
            text="НАЗВАНИЕ КИТА (ИМЯ ПАПКИ)",
            font=ctk.CTkFont(family="Helvetica", size=9, weight="bold"),
            text_color=TEXT_MUTED
        )
        self.nick_label.grid(row=0, column=0, sticky="w", padx=10, pady=(0, 2))

        self.nickname_entry = ctk.CTkEntry(
            self.inputs_grid,
            width=260,
            height=32,
            fg_color=BG_MAIN,
            border_color=BORDER_COLOR,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Helvetica", size=12),
            corner_radius=4,
            border_width=1,
            placeholder_text="STASH"
        )
        self.nickname_entry.grid(row=1, column=0, padx=10, pady=(0, 15), sticky="w")
        self.nickname_entry.insert(0, "STASH")

        # Тэг / Префикс
        self.tag_label = ctk.CTkLabel(
            self.inputs_grid,
            text="АВТОРСКИЙ ТЕГ (ПРЕФИКС СЭМПЛОВ)",
            font=ctk.CTkFont(family="Helvetica", size=9, weight="bold"),
            text_color=TEXT_MUTED
        )
        self.tag_label.grid(row=0, column=1, sticky="w", padx=10, pady=(0, 2))

        self.tag_entry = ctk.CTkEntry(
            self.inputs_grid,
            width=260,
            height=32,
            fg_color=BG_MAIN,
            border_color=BORDER_COLOR,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Helvetica", size=12),
            corner_radius=4,
            border_width=1,
            placeholder_text="[GAWS]"
        )
        self.tag_entry.grid(row=1, column=1, padx=10, pady=(0, 15), sticky="w")
        self.tag_entry.insert(0, "[PROD]")

        # Лимиты по сэмплам
        self.limit_title_label = ctk.CTkLabel(
            self.config_panel,
            text="ЛИМИТ СЭМПЛОВ НА КАЖДУЮ КАТЕГОРИЮ",
            font=ctk.CTkFont(family="Helvetica", size=9, weight="bold"),
            text_color=TEXT_MUTED
        )
        self.limit_title_label.pack(anchor="w", padx=30, pady=(0, 2))

        self.slider_frame = ctk.CTkFrame(self.config_panel, fg_color="transparent")
        self.slider_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.limit_slider = ctk.CTkSlider(
            self.slider_frame,
            from_=5,
            to=30,
            number_of_steps=25,
            fg_color=BORDER_COLOR,
            progress_color=ACCENT_GREEN,
            button_color=ACCENT_GREEN,
            button_hover_color=TEXT_MAIN,
            corner_radius=4,
            height=14,
            command=self.update_slider_label
        )
        self.limit_slider.pack(side="left", fill="x", expand=True, pady=5)
        self.limit_slider.set(10)

        self.slider_val_label = ctk.CTkLabel(
            self.slider_frame,
            text="10 СЭМПЛОВ",
            width=110,
            font=ctk.CTkFont(family="Courier New", size=11, weight="bold"),
            text_color=TEXT_MAIN
        )
        self.slider_val_label.pack(side="right", padx=(15, 0))

        # --- БЛОК ВЫБОРА ДИРЕКТОРИЙ ---
        self.paths_frame = ctk.CTkFrame(self.config_panel, fg_color="transparent")
        self.paths_frame.pack(fill="x", padx=30, pady=(5, 15))

        # Кнопка Источника
        self.src_btn = ctk.CTkButton(
            self.paths_frame,
            text="ОТКУДА (ZIP)",
            width=120,
            height=28,
            fg_color=BG_MAIN,
            border_color=BORDER_COLOR,
            border_width=1,
            hover_color=BG_PANEL,
            text_color=TEXT_MAIN,
            corner_radius=4,
            font=ctk.CTkFont(family="Helvetica", size=10, weight="bold"),
            command=self.browse_source
        )
        self.src_btn.grid(row=0, column=0, pady=5, sticky="w")

        self.src_entry = ctk.CTkEntry(
            self.paths_frame,
            textvariable=self.source_dir,
            fg_color=BG_MAIN,
            border_color=BORDER_COLOR,
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=11),
            corner_radius=4,
            border_width=1,
            height=28
        )
        self.src_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")

        # Кнопка Экспорта
        self.tgt_btn = ctk.CTkButton(
            self.paths_frame,
            text="КУДА ЭКСПОРТ",
            width=120,
            height=28,
            fg_color=BG_MAIN,
            border_color=BORDER_COLOR,
            border_width=1,
            hover_color=BG_PANEL,
            text_color=TEXT_MAIN,
            corner_radius=4,
            font=ctk.CTkFont(family="Helvetica", size=10, weight="bold"),
            command=self.browse_target
        )
        self.tgt_btn.grid(row=1, column=0, pady=5, sticky="w")

        self.tgt_entry = ctk.CTkEntry(
            self.paths_frame,
            textvariable=self.target_dir,
            fg_color=BG_MAIN,
            border_color=BORDER_COLOR,
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=11),
            corner_radius=4,
            border_width=1,
            height=28
        )
        self.tgt_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky="ew")

        self.paths_frame.grid_columnconfigure(1, weight=1)

        # --- СУПЕР КНОПКА ЗАПУСКА ---
        self.execute_btn = ctk.CTkButton(
            self,
            text="СГЕНЕРИРОВАТЬ СТЭШ КИТ",
            command=self.run_extraction,
            fg_color=ACCENT_GREEN,
            hover_color=TEXT_MAIN,
            text_color="#FFFFFF",
            height=46,
            font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
            corner_radius=6
        )
        self.execute_btn.pack(fill="x", padx=30, pady=(15, 30))

    def update_slider_label(self, val):
        self.slider_val_label.configure(text=f"{int(val)} СЭМПЛОВ")

    def update_screen(self, text, is_error=False):
        color = "#C25959" if is_error else ACCENT_GREEN
        self.status_display.configure(text=text, text_color=color)
        self.update()

    def browse_source(self):
        directory = filedialog.askdirectory(initialdir=self.source_dir.get())
        if directory:
            self.source_dir.set(directory)
            self.update_screen(
                f"ПАПКА ИМПОРТА ВЫБРАНА:\n{directory}\n\nНажмите 'КУДА ЭКСПОРТ', чтобы указать путь сохранения.")

    def browse_target(self):
        directory = filedialog.askdirectory(initialdir=self.target_dir.get())
        if directory:
            self.target_dir.set(directory)
            self.update_screen(
                f"ПАПКА ЭКСПОРТА ВЫБРАНА:\n{directory}\n\nВсё готово к работе! Нажмите зеленую кнопку для сборки.")

    def run_extraction(self):
        kit_name = self.nickname_entry.get().strip()
        tag = self.tag_entry.get().strip()
        source_path = self.source_dir.get()
        target_path = self.target_dir.get()
        limit = int(self.limit_slider.get())

        if not kit_name:
            messagebox.showerror("ОШИБКА СИСТЕМЫ", "Пожалуйста, введите название стэш кита.")
            return

        if not os.path.exists(source_path) or not os.path.exists(target_path):
            messagebox.showerror("ОШИБКА СИСТЕМЫ", "Указанные папки не существуют. Проверьте пути.")
            return

        self.execute_btn.configure(state="disabled")
        self.update_screen(
            "ПРОЦЕСС ЗАПУЩЕН: Сканирую ZIP-архивы...\nЭто может занять немного времени. Пожалуйста, подождите.")

        folder_name = f"{kit_name} стэш кит"
        output_dir = os.path.join(target_path, folder_name)

        all_samples = []
        sample_source_map = {}
        zip_count = 0

        for root_dir, dirs, files in os.walk(source_path):
            for file_name in files:
                if file_name.endswith('.zip'):
                    zip_count += 1
                    zip_path = os.path.join(root_dir, file_name)

                    try:
                        with zipfile.ZipFile(zip_path, 'r') as archive:
                            for member in archive.namelist():
                                if member.lower().endswith(('.wav', '.mp3')):
                                    clean_name = os.path.basename(member)
                                    if clean_name:
                                        all_samples.append(clean_name)
                                        sample_source_map[clean_name] = (zip_path, member)
                    except Exception as e:
                        print(f"Error: {e}")

        if zip_count == 0:
            self.update_screen("ОШИБКА: Архивы не найдены.\nВ папке 'ОТКУДА' должны лежать ZIP-файлы с проектами.",
                               is_error=True)
            self.execute_btn.configure(state="normal")
            return

        self.update_screen(
            f"АНАЛИЗ ЗАВЕРШЕН: Найдено {len(all_samples)} сэмплов в {zip_count} ZIP-архивах.\nНачинаю сортировку и копирование лучших звуков...")

        global_counter = Counter(all_samples)
        categorized_samples = {cat: [] for cat in CATEGORIES.keys()}
        categorized_samples["Unsorted"] = []

        for sample, count in global_counter.items():
            cat = get_sample_category(sample)
            if cat in categorized_samples:
                categorized_samples[cat].append((sample, count))

        copied_count = 0
        for category, samples_list in categorized_samples.items():
            if category == "Unsorted":
                continue

            sorted_by_usage = sorted(samples_list, key=lambda x: x[1], reverse=True)
            category_dir = os.path.join(output_dir, category)
            valid_samples_copied = 0

            for sample, count in sorted_by_usage:
                if valid_samples_copied >= limit:
                    break

                if sample in sample_source_map:
                    zip_path, original_path_in_zip = sample_source_map[sample]
                    duration = get_wav_duration_from_zip(zip_path, original_path_in_zip)

                    if duration is not None:
                        if category == "808" and duration < 0.45:
                            continue
                        if category in ["Hi-Hats", "Open Hats", "Claps", "Kicks", "Vox"] and duration > 2.5:
                            continue

                    try:
                        with zipfile.ZipFile(zip_path, 'r') as archive:
                            source = archive.open(original_path_in_zip)
                            os.makedirs(category_dir, exist_ok=True)

                            final_filename = f"{tag} {sample}" if tag else sample
                            target_file_path = os.path.join(category_dir, final_filename)

                            with open(target_file_path, "wb") as target:
                                shutil.copyfileobj(source, target)
                            copied_count += 1
                            valid_samples_copied += 1
                    except Exception as e:
                        print(f"Error copying {sample}: {e}")

        self.execute_btn.configure(state="normal")
        self.update_screen(
            f"УСПЕШНО ЗАВЕРШЕНО: Экспортировано {copied_count} звуков.\nНовый стэш кит готов к работе в FL Studio!")

        messagebox.showinfo(
            "ГОТОВО",
            f"Успех!\n\nТвой стэш кит '{folder_name}' собран.\n"
            f"Скопировано самых ходовых звуков: {copied_count}.\n"
            f"Все сэмплы помечены префиксом: '{tag}'."
        )


if __name__ == "__main__":
    app = RetroStashApp()
    app.mainloop()