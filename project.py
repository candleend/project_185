import sqlite3
import sys
from random import sample
from PyQt5.Qt import QProgressBar, QLCDNumber, QBasicTimer, QFont, QDialogButtonBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QMessageBox
from PyQt5 import QtGui


class Window_game(QWidget):
    def __init__(self):
        super().__init__()
        self.init()

    def init(self):
        self.setWindowTitle('Угадай слово')
        self.setStyleSheet("background: #75c1ff")
        self.setFixedSize(550, 550)

        self.line_time = QProgressBar(self)
        self.line_time.setGeometry(10, 515, 400, 25)
        self.line_time.setStyleSheet("""background-color: green; 
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;""")

        # Поле вывода правильных ответов
        self.print_col_right = QLCDNumber(self)
        self.print_col_right.display(col_right)
        self.print_col_right.setStyleSheet("""background-color: green""")
        self.print_col_right.setGeometry(417, 515, 45, 25)

        # Таймер для ограничения времени для ответа
        self.timer = QBasicTimer()
        self.timer.start(600, self)
        self.step = 0

        # Отрисовываем алфавит для выбора букв играющим
        dictionary1 = ['а', 'б', 'в', 'г', 'д', 'е', "ё", 'ж', 'з', 'и', "й"]
        dictionary2 = ['к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф']
        dictionary3 = ['х', 'ц', 'ч', 'ш', 'щ', 'ъ', "ы", "ь", "э", "ю", "я"]
        a = 0
        b = 0
        v = 0
        self.col_clicked = 0
        for i in dictionary1:
            self.btn_dictionary1 = QPushButton(i, self)
            self.btn_dictionary1.clicked.connect(self.inputtt)
            self.btn_dictionary1.setGeometry(a, 350, 50, 50)
            a += 50
        for k in dictionary2:
            self.btn_dictionary2 = QPushButton(k, self)
            self.btn_dictionary2.clicked.connect(self.inputtt)
            self.btn_dictionary2.setGeometry(v, 400, 50, 50)
            v += 50
        for j in dictionary3:
            self.btn_dictionary3 = QPushButton(j, self)
            self.btn_dictionary3.clicked.connect(self.inputtt)
            self.btn_dictionary3.setGeometry(b, 450, 50, 50)
            b += 50

        # Из базы данных отбираем записи (слова и вопросы) по выбранной категории number
        con = sqlite3.connect("questions_db (3).sqlite")
        cur = con.cursor()
        global number
        word11 = cur.execute(f"""SELECT questionandword.woords, questionandword.qquestion
            FROM questionandword, chapter JOIN chapter_question
            ON questionandword.num = chapter_question.id_question AND
            chapter.id = chapter_question.id_chapter
            WHERE id_chapter = {number}""").fetchall()
        con.close()
        word_question = []
        self.questionn1 = ""
        for i in word11:
            for j in i:
                word_question.append(j)

        # Из полученной выборки случайным образом определяем пару загаданное слово и вопрос к нему
        # Загаданное слово word1 и вопрос относящийся к нему questionn1
        global rand1
        rand = rand1
        global col_question
        col_question += 1
        self.word1 = word_question[rand[col_question - 1]]
        self.questionn1 = word_question[rand[col_question - 1] + 1]

        # Поле где будет выводится загаданное слово. Вначале вместо букв загаданного слова выводим *
        self.word2 = "*" * len(self.word1)
        self.card1 = QLineEdit(self.word2, self)
        self.card1.setAlignment(Qt.AlignCenter)
        self.card1.setEnabled(False)
        self.card1.setFont(QFont('Arial Black', 18))
        self.card1.setGeometry(125, 150, 250, 50)

        # Поле куда выводим вопрос к загаданному слову
        self.print_question = QLabel(self)
        self.print_question.setText("Вопрос:\n" + self.questionn1)
        self.print_question.setWordWrap(True)
        self.print_question.setFixedHeight(145)
        self.print_question.setMinimumWidth(40)
        self.print_question.setFont(QtGui.QFont("Consolas", 14, QtGui.QFont.Bold))
        self.print_question.setStyleSheet("""color: green""")
        self.print_question.resize(500, 500)
        self.print_question.move(10, 5)

        # Поле для ввода ответа игрока
        self.print_word = QLineEdit(self)
        self.print_word.setAlignment(Qt.AlignCenter)
        self.print_word.setFont(QFont('Arial', 12))
        self.print_word.setGeometry(125, 300, 250, 25)

        # Кнопка проверить ответ
        self.btn_print = QPushButton("Проверить", self)
        self.btn_print.setStyleSheet('background: #f5f5f5')
        self.btn_print.setEnabled(True)
        self.btn_print.clicked.connect(self.answer)
        self.btn_print.setGeometry(380, 300, 75, 25)

        self.btn_print2 = QPushButton("Показать ответ", self)
        self.btn_print2.setStyleSheet('background: #b4e600')
        self.btn_print2.clicked.connect(self.answer_rightr)
        self.btn_print2.setGeometry(15, 300, 100, 25)

        # Определение максимально возможного количества букв-подсказок
        self.maxx = len(self.word1) // 2
        if self.maxx > 4:
            self.maxx = 4
        if self.maxx == 1:
            self.strmaxx = 'одну букву'
        if self.maxx == 2:
            self.strmaxx = 'две буквы'
        if self.maxx == 3:
            self.strmaxx = 'три буквы'
        if self.maxx == 4:
            self.strmaxx = 'четыре буквы'

        self.hints = QLabel(self)
        self.hints.setText('Вы можете открыть ' + self.strmaxx + ' или сразу написать ответ!')
        self.hints.setFont(QFont('Arial Black', 10))
        self.hints.move(50, 225)

        self.hints2 = QLabel(self)
        self.hints2.setFixedHeight(18)
        self.hints2.setMinimumWidth(550)
        self.hints2.setFont(QtGui.QFont('Arial Black', 10, QtGui.QFont.Bold))
        self.hints2.move(50, 245)

        self.hints3 = QLabel(self)
        self.hints3.setFixedHeight(18)
        self.hints3.setMinimumWidth(550)
        self.hints3.setFont(QtGui.QFont('Arial Black', 10, QtGui.QFont.Bold))
        self.hints3.move(50, 265)

        # Поле наименования выбранной категории и номера текущего вопроса
        self.hints4 = QLabel(self)
        self.hints4.setText("Категория " + name_category + ", " + str(col_question) + " вопрос из 5 вопросов")
        self.hints4.setFont(QFont('Arial Black', 10))
        self.hints4.move(10, 15)

        # Кнопка следующий вопрос
        self.btn_print2 = QPushButton("Следующий вопрос", self)
        self.btn_print2.setStyleSheet('background: #b4e600')
        self.btn_print2.clicked.connect(self.printt)
        self.btn_print2.setGeometry(410, 15, 120, 25)

        # Кнопка выход
        self.btn_exitt = QPushButton("Выход", self)
        self.btn_exitt.setStyleSheet('background: #f5f5f5')
        self.btn_exitt.clicked.connect(self.exitt)
        self.btn_exitt.setGeometry(470, 515, 70, 25)


    def printt(self):
        if col_question >= 5:
            self.timer.stop()
            self.w_the_end = Window_the_end()
            self.w_the_end.show()
            self.close()
        else:
            self.timer.stop()
            self.w_game = Window_game()
            self.w_game.show()
            self.close()

    def answer_rightr(self):
        self.card1.setText(self.word1)
        self.timer.stop()
        self.btn_print.setEnabled(False)
        self.hints.setText('Ответ на эране')
        self.hints2.setText(" ")
        self.hints3.setText(" ")

    # Таймер для отображения прогресса времени
    def timerEvent(self, e):
        if self.step == 80:
            self.hints.setText("Время истекло! Введите ответ и нажмите Проверить!")
            self.hints2.setText("Если в течении 15 секунд Вы не введете ответ,  ")
            self.hints3.setText("произойдет автоматический переход к следующему вопросу ")
            self.line_time.setStyleSheet("""background-color: #CD96CD; 
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;""")
        if self.step == 101:
            self.timer.stop()
            self.printt()
        self.step = self.step + 1
        self.line_time.setValue(self.step)

    # Нажатие на буквы - играющий открывает разрешенное количество букв
    def inputtt(self):
        self.col_clicked += 1
        if self.col_clicked > self.maxx:
            self.hints2.setText("Вы уже выбрали " + self.strmaxx + "!")
            self.hints3.setText("Теперь Вы можете только ввести слово целиком")
        else:
            spusok_word2 = list(self.card1.text())
            j = self.btn_dictionary1.sender().text()
            if j in self.word1:
                self.hints2.setText("Выбрана буква " + j.upper() + " . Есть такая буква!")
                for i in range(len(self.word1)):
                    if self.word1[i] == j:
                        spusok_word2[i] = j
            else:
                self.hints2.setText("Выбрана буква " + j.upper() + " . Нет такой буквы!")
            self.card1.setText("".join(spusok_word2))

    # Играющий нажал на кнопку - Проверить ответ
    def answer(self):
        self.hints2.setText(" ")
        self.hints3.setText(" ")
        i = self.print_word.text().lower()
        global col_question
        global col_right
        if i == self.word1 and col_question < 5:
            self.hints.setText(i.upper() + " - ПРАВИЛЬНЫЙ ОТВЕТ!")
            self.hints3.setText("Переходите к следующему вопросу ")
            self.timer.stop()
            self.card1.setText(self.word1)
            self.col_clicked = 0
            col_right += 1
            self.print_col_right.display(col_right)
        elif i == self.word1 and col_question >= 5:
            self.hints.setText(i.upper() + " - ПРАВИЛЬНЫЙ ОТВЕТ!")
            self.card1.setText(self.word1)
            self.timer.stop()
            self.col_clicked = 0
            col_right += 1
            self.print_col_right.display(col_right)
            self.w_the_end = Window_the_end()
            self.w_the_end.show()
            self.close()
        elif i == "":
            self.hints.setText("Ответ не введен. Введите слово")
        else:
            self.hints.setText(i.upper() + " - это неправильный ответ. Подумайте ещё")

    def exitt(self):
        dlg1 = QMessageBox(self)
        dlg1.setWindowTitle("ВЫХОД?")
        dlg1.setText("Вы уверены, что хотите выйти?")
        dlg1.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        dlg1.setIcon(QMessageBox.Question)
        self.btn_exitt = dlg1.exec()
        if self.btn_exitt == QMessageBox.Yes:
            self.close()


# Приветственное окно, Правила игры
class Window_orientation(QWidget):
    def __init__(self):
        super().__init__()
        self.creature()

    def creature(self):
        self.setWindowTitle('Игра: угадай слово!')
        self.setFixedSize(550, 550)
        self.setStyleSheet("background: #a7d4d0")

        self.print_welcome = QLabel(self)
        # self.print_welcome.setText("Добро пожаловать!")
        self.print_welcome.setText('"Угадай слово"')
        self.print_welcome.setStyleSheet("""
                    font: bold italic 18px;
                    style: outset;           
                    color: red""")
        self.print_welcome.move(200, 50)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setGeometry(250, 350, 250, 250)
        self.buttonBox.accepted.connect(self.show_new_window)
        self.buttonBox.rejected.connect(self.cclose)

        self.print_name_rules =  QLabel("Правила игры", self)
        self.print_name_rules.setFont(QFont('Arial Black', 12))
        self.print_name_rules.setGeometry(215, 100, 200, 25)

        self.print_rules = QLabel(self)
        self.print_rules.setText('В начале каждого раунда Вам необходимо выбрать тему вопросов.\n'
                                 'Каждый раунд игры состоит из 5 вопросов, посвященных выбранной теме.\n'
                                 'На экран выводится вопрос, ответ на который (загаданное слово) скрыт на табло.\n'
                                 'Длина слова известна - каждая скрытая буква отображена *.\n'
                                 'Вам разрешается открыть определенное количество букв. Выбор буквы \n'
                                 'осуществляется наведением курсора на соответствующую букву  \n'
                                 'и нажатием левой кнопки мыши. Если выбранная буква есть в загаданном слове,\n'
                                 'то она будет открыта. Если Вы знаете ответ - полное слово, то введите его \n'
                                 'в поле для ввода ответа и нажмите кнопку Проверить.\n'
                                 'Основная задача игрока - угадать загаданное слово раньше истечения таймера.\n'
                                 '\n\n'
                                 'Для продолжения игры нажмите "OK".')

        self.print_rules.setFont(QFont('Arial', 10))
        self.print_rules.move(25, 150)

    def show_new_window(self):
        self.w_choice = Window_choice()
        self.w_choice.show()
        self.close()

    def cclose(self):
        self.close()


# Окно выбора категории вопросов
class Window_choice(QWidget):
    def __init__(self):
        super().__init__()
        self.creature_choice()

    def creature_choice(self):
        self.setFixedSize(550, 550)
        self.setWindowTitle('Игра: "Угадай слово!": выбор предмета')
        self.setStyleSheet("background: #a496f2")

        self.print_choice = QLabel(self)
        self.print_choice.setText('Выберите предмет')
        self.print_choice.setFont(QFont('Arial Black', 16))
        self.print_choice.move(150, 150)

        self.btn_choice = QPushButton("Языки", self)
        self.btn_choice.setGeometry(25, 400, 100, 100)
        self.btn_choice.setStyleSheet('background: #f5f5f5')
        self.btn_choice.clicked.connect(self.choice_languages)

        self.btn_choice2 = QPushButton("Биология", self)
        self.btn_choice2.clicked.connect(self.choice_biology)
        self.btn_choice2.setGeometry(125, 250, 100, 100)
        self.btn_choice2.setStyleSheet('background: #f5f5f5')

        self.btn_choice3 = QPushButton("История", self)
        self.btn_choice3.clicked.connect(self.choice_history)
        self.btn_choice3.setGeometry(225, 400, 100, 100)
        self.btn_choice3.setStyleSheet('background: #f5f5f5')

        self.btn_choice4 = QPushButton("Физика", self)
        self.btn_choice4.clicked.connect(self.choice_physics)
        self.btn_choice4.setGeometry(325, 250, 100, 100)
        self.btn_choice4.setStyleSheet('background: #f5f5f5')

        self.btn_choice5 = QPushButton("Математика", self)
        self.btn_choice5.clicked.connect(self.choice_different)
        self.btn_choice5.setGeometry(425, 400, 100, 100)
        self.btn_choice5.setStyleSheet('background: #f5f5f5')

    def choice_different(self):
        global number
        global name_category
        number = 1
        name_category = "Разное"
        self.w_game = Window_game()
        self.w_game.show()
        self.close()

    def choice_languages(self):
        global number
        global name_category
        number = 2
        name_category = "Языки"
        self.w_game = Window_game()
        self.w_game.show()
        self.close()

    def choice_biology(self):
        global number
        global name_category
        number = 3
        name_category = "Биология"
        self.w_game = Window_game()
        self.w_game.show()
        self.close()

    def choice_history(self):
        global number
        global name_category
        number = 4
        name_category = "История"
        self.w_game = Window_game()
        self.w_game.show()
        self.close()

    def choice_physics(self):
        global number
        global name_category
        number = 5
        name_category = "Физика"
        self.w_game = Window_game()
        self.w_game.show()
        self.close()


# Окно результатов
class Window_the_end(QWidget):
    def __init__(self):
        super().__init__()
        self.creature_the_end()

    def creature_the_end(self):
        self.setFixedSize(550, 550)
        self.setWindowTitle('Результаты')
        self.setStyleSheet("background: #a7d4d0")

        self.print_end = QLabel(self)
        self.print_end.setText("Игра подошла к концу!")
        self.print_end.setStyleSheet("""
                    font: bold italic 18px;
                    style: outset;           
                    color: red""")
        self.print_end.move(150, 150)

        self.print_end2 = QLabel(self)
        self.print_end2.move(135, 200)
        self.print_end2.setFont(QFont('Arial Black', 12))
     #  self.print_end2.setStyleSheet("""color: green""")

        self.print_end3 = QLabel(self)
        self.print_end3.move(170, 250)
        self.print_end3.setFont(QFont('Arial Black', 12))
      #  self.print_end3.setStyleSheet("""color: blue""")
        self.print_end3.setText('Попробуйте ещё раз!')

        self.print_end4 = QLabel(self)
        self.print_end4.move(175, 100)
        self.print_end4.setFont(QFont('Arial Black', 12))
        self.print_end4.setStyleSheet("""color: #ffff00""")

        self.buttonBox2 = QDialogButtonBox(self)
        self.buttonBox2.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Yes)
        self.buttonBox2.setGeometry(100, 250, 250, 250)
        self.buttonBox2.accepted.connect(self.again)
        self.buttonBox2.rejected.connect(self.ccclose)

        if col_right == 5:
            self.print_end4.setText("!!!ВЫ ВЫИГРАЛИ!!!")
            self.print_end2.setText("В Категории " + name_category + " 5 из 5 верно")
        else:
            self.print_end2.setText("В Категории " + name_category + f" {col_right} из 5 верно")

    def again(self):
        global col_right
        col_right = 0
        global col_question
        col_question = 0
        self.w_choice = Window_choice()
        self.w_choice.show()
        self.close()

    def ccclose(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window_orientation()
    # number - номер категории вопросов
    number = 0
    # col_question - номер вопроса из пяти возможных вопросов
    col_question = 0
    #  name_category - название категории
    name_category = ""
    # rand1 - список с числами без повторения
    rand1 = sample(range(0, 19, 2), 5)
    # col_right - количество верных ответов
    col_right = 0
    ex.show()
    sys.exit(app.exec())
