import tkinter as tk
import random

class QuantTamagotchi:
    def __init__(self):
        self.window = tk.Tk()
        
        # Настройки прозрачности и отображения поверх всех окон
        self.window.config(highlightbackground='black')
        self.window.overrideredirect(True) # Убираем рамки Windows
        self.window.wm_attributes('-topmost', True) # Всегда поверх всех окон
        self.window.wm_attributes('-transparentcolor', 'black') # Черный фон станет прозрачным
        self.window.config(bg='black')

        # Изначальные координаты (центр экрана)
        self.x = 500
        self.y = 500
        
        # Игровые состояния нашего тамагочи
        self.state = "calm" 
        self.timer = 0
        
        # Список фраз, которые он бормочет (твоя макро-математика и ворчание)
        self.phrases = [
            "🤖: Хм... Вижу скрытую аномалию 4-й степени...",
            "📉: Куда ты покупаешь?! Там же Ловушка Ликвидаций!",
            "☀️: Опять лето... Ликвидность упала на 70%, все на пляже.",
            "🏛️: Политический стресс растет. Запахло 3-мя сигмами...",
            "⚡: Анти-гэп щит активирован! Сижу на заборе, курю бамбук.",
            "📊: Прогнал историю через тест Бенфорда. Вокруг один скам...",
            "🔥: Осторожно! Синдром Икара! Рынок в зоне безумия!",
            "💤: Рынок мертв, объемы нулевые. Пойду посплю...",
            "💥: Опять ветвления перегрузили процессор... Ща сгорим!",
            "👑: Ха! Попался, инсайдер! Я вижу твой скрытый закуп!"
        ]
        
        # Создаем облачко для мыслей (текст)
        self.bubble = tk.Label(self.window, text="🤖: Запуск систем HASE...", fg='white', bg='#222222', font=('Courier', 10, 'bold'))
        self.bubble.pack()
        
        # Создаем самого персонажа (текстовый арт кота, чтобы не искать картинки)
        self.avatar = tk.Label(self.window, text="  /\_/\  \n ( o.o ) \n  > ^ <  ", fg='#00FF00', bg='black', font=('Courier', 14, 'bold'))
        self.avatar.pack()

        # Запуск главного цикла анимации
        self.window.after(1, self.update_pet)
        self.window.mainloop()

    def update_pet(self):
        # Переключаем состояния раз в несколько секунд
        self.timer += 1
        if self.timer > 30: # Каждые ~3 секунды меняем поведение
            self.timer = 0
            self.state = random.choice(["calm", "walking", "talking"])
            
            # Если он решил поговорить — выбираем случайную квантовую фразу
            if self.state == "talking":
                self.bubble.config(text=random.choice(self.phrases), bg='#332244')
            else:
                self.bubble.config(text="", bg='black') # Прячем облачко

        # Логика движения по экрану
        if self.state == "walking":
            # Случайно шагает влево, вправо, вверх или вниз
            self.x += random.choice([-5, 0, 5])
            self.y += random.choice([-3, 0, 3])
            
            # Меняем вид кота во время движения (анимация шага)
            self.avatar.config(text="  /\_/\  \n ( -.- ) \n  / | \  ")
        else:
            # Вид кота в спокойном состоянии
            self.avatar.config(text="  /\_/\  \n ( o.o ) \n  > ^ <  ")

        # Ограничиваем, чтобы не убежал за пределы экрана
        self.x = max(10, min(self.x, 1500))
        self.y = max(10, min(self.y, 800))

        # Обновляем позицию окна на экране
        self.window.geometry(f"+{self.x}+{self.y}")
        
        # Повторяем цикл каждые 100 миллисекунд
        self.window.after(100, self.update_pet)

if __name__ == "__main__":
    QuantTamagotchi()
