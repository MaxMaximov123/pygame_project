from pygame.sprite import (Sprite,
                           AbstractGroup,
                           Group)
from pygame import (Rect,
                    Surface,
                    transform,
                    font,
                    draw,
                    image,
                    Color)
from typing import (Any,
                    Union,
                    Sequence,
                    List,
                    Tuple)
from random import shuffle
import pygame
import pygame_menu

# параметры поля
COUNT: int = 2
IM: Surface = image.load('mamont.jpg')


class Ceil(Sprite):
    # конструктор класса клетки
    def __init__(
            self,
            row_index: int,
            column_index: int,
            number: int,
            is_noop: bool,
            delimeter_width: int,
            pygame_Surface: Surface, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        # проверка входных данных на корректность
        if row_index < 0:
            raise Exception('row_index < 0')
        if column_index < 0:
            raise Exception('column_index < 0')
        if number <= 0:
            raise Exception('number <= 0')
        # оригинальное изображение
        self.__original_Surface: Surface = pygame_Surface
        # номер ячейки
        self.__original_number = number
        #self.__current_number = number
        # строка ячейки
        self.__original_row_index = row_index
        self.current_row_index = row_index
        # столбец ячейки
        self.__original_column_index = column_index
        self.current_column_index = column_index
        # признак что ячейка последняя
        self.__is_noop = is_noop

        self.__delimeter_width = delimeter_width

    # переопределение функции обновления
    # def update(self, *args: Any, **kwargs: Any) -> None:
    #   return super().update(*args, **kwargs)

    def get_number(self) -> int:
        return self.__original_number

    # функция возвращения параметра 'пустоты поля'
    def get_is_noop(self) -> bool:
        return self.__is_noop

    # функция масштабирования изображения
    def set_rect(self, rect: Rect, is_last_row: bool, is_last_column: bool) -> None:
        # вычисляем положение изображения с учетом зазоров
        # вычисляем размер изображения с учетом зазоров
        x: int = rect.x
        y: int = rect.y
        width: int = rect.width
        height: int = rect.height
        if self.current_column_index == 0:
            x += 2*self.__delimeter_width
            width -= 3*self.__delimeter_width
        elif is_last_column:
            x += self.__delimeter_width
            width -= 3*self.__delimeter_width
        else:
            x += self.__delimeter_width
            width -= 2*self.__delimeter_width

        if self.current_row_index == 0:
            y += 2*self.__delimeter_width
            height -= 3*self.__delimeter_width
        elif is_last_row:
            y += self.__delimeter_width
            height -= 3*self.__delimeter_width
        else:
            y += self.__delimeter_width
            height -= 2*self.__delimeter_width

        if width < 10 or height < 10:
            return

        # устанавливаем позицию и размер рисунка
        self.rect = Rect(x, y, width, height)

        # масштабируем отображаемое изображение
        self.image = transform.scale(self.__original_Surface, (width, height))

        if self.__is_noop:
            return
        # впечатываем номер ячейки
        #myfont = font.SysFont(font.get_fonts()[0],48)
        #myfont = font.SysFont(font.get_default_font(), 48)
        myfont = font.SysFont(None, 48)

        fontimg = myfont.render(str(self.__original_number), True, (255, 0, 0))
        #self.image = fontimg
        fontrect = fontimg.get_rect()
        self.image.blit(fontimg, fontrect)


class Field(Group):
    # конструктор
    def __init__(
        self,
        count: int,
        delimeter_width: int,
        image_Surface: Surface,
    ) -> None:
        # проверка входных данных на корректность
        if count < 2:
            raise Exception('count < 2')
        if delimeter_width < 1:
            raise Exception('delimeter_width < 1')

        # число ячеек в строке и столбце
        self.__count: int = count

        # толщина разделителя
        self.__delimeter_width: int = delimeter_width

        # толщина разделителя
        self.__noop_color: Color = (0, 0, 0)

        # признак собранности поля
        self.__is_build = False

        # количство ходов
        self.step_count = 0

        # создаем спрайты
        ceils: Union[Sprite, Sequence[Sprite]] = []

        # получаем размеры изображения
        image_width: int = image_Surface.get_width()
        image_higth: int = image_Surface.get_height()
        # image_width, image_higth =

        # вычисляем размер изображения для ячейки
        image_ceil_width: int = image_width // self.__count
        image_ceil_higth: int = image_higth // self.__count

        ceil_number = 1
        # циклы заполнения ячеек
        for row_index in range(self.__count):
            # вычисляем координату подкартинки в картинке
            image_ceil_y: int = row_index * image_ceil_higth
            for column_index in range(self.__count):
                # вычисляем координаты столбца картинки
                image_ceil_x = column_index * image_ceil_width
                # определяем что стока последняя
                is_last_row: bool = row_index == self.__count - 1
                # определяем что столбец последний
                is_last_column: bool = column_index == self.__count - 1
                # определяем что ячейка последняя
                is_noop: bool = is_last_row and is_last_column
                # вырезаем картинку ячейки из общей картинки
                subsurface: Surface = image_Surface.subsurface(
                    (image_ceil_x, image_ceil_y, image_ceil_width, image_ceil_higth))
                if is_noop:
                    subsurface.fill(self.__noop_color)
                # создаем ячейку
                ceil = Ceil(row_index, column_index, ceil_number,
                            is_noop, self.__delimeter_width, subsurface)
                # увеличиваем номер ячейки
                ceil_number += 1
                # добавляем ячейку в строку поля
                ceils.append(ceil)
        super().__init__(*ceils)
        self.shake_field()

    # переопределяем функцию рисования поля на экране
    def draw(self, surface: Surface) -> List[Rect]:
        # получаем размеры экрана
        surface_width, surface_higth = surface.get_size()
        # вычисляем размер изображения ячейки
        ceil_width = surface_width // self.__count
        ceil_height = surface_higth // self.__count

        # если размеры клетки удовлетворяют условию
        if ceil_width >= 2 and ceil_height >= 2:
            # для каждого спрайта в списке спрайтов
            for sprite in self.sprites():
                # если тип спрайта клетка
                if type(sprite) is Ceil:
                    ceil: Ceil = sprite
                    # вычисляем положение клетки
                    current_row_index = ceil.current_row_index
                    current_column_index = ceil.current_column_index
                    left: int = ceil.current_column_index * ceil_width
                    top: int = ceil.current_row_index * ceil_height
                    rect: Rect = Rect(left, top, ceil_width, ceil_height)
                    is_last_row: bool = current_row_index == self.__count - 1
                    is_last_column: bool = current_column_index == self.__count - 1
                    sprite.set_rect(rect, is_last_row, is_last_column)

        # вызываем родительский метод рисования
        return super().draw(surface)

    # функция перемешивания поля
    def shake_field(self) -> None:
        # формируем список индексов строк и стролбцов
        row_column_index: List[Tuple(int, int)] = []
        for sprite in self.sprites():
            if type(sprite) is Ceil:
                ceil: Ceil = sprite
                row_column_index.append(
                    (ceil.current_row_index, ceil.current_column_index))
        while True:
            # перепутываем индексы
            shuffle(row_column_index)
            # раставляем индексы ячейкам
            index: int = 0
            for sprite in self.sprites():
                # проверка типа спрайта
                if type(sprite) is Ceil:
                    ceil: Ceil = sprite
                    ceil.current_row_index = row_column_index[index][0]
                    ceil.current_column_index = row_column_index[index][1]
                    index += 1
            # считаем что поле не собрано
            self.__is_build = False
            # если поле оказалось собранным
            # if self.is_build():
            # продолжаем запутывать
            #    continue
            # если поле может собраться
            if self.test_aviable_build():
                # заканчиваем запутывать
                return
            # если поле не может быть собранным, то продолжаем запутывать
            else:
                continue

    # функция возвращает номер ячейки
    def __get_ceil_current_number(self, ceil: Ceil) -> int:
        return ceil.current_row_index * self.__count + ceil.current_column_index + 1

    # проверка собираемости поля
    def test_aviable_build(self) -> bool:
        Ceils: List[Ceil] = []
        for sprite in self.sprites():
            if type(sprite) is Ceil:
                ceil: Ceil = sprite
                # добавление клетки в список клеток
                Ceils.append(ceil)
        #print(", ".join(str(i.get_number()) for i in  Ceils))
        #print(", ".join(str(self.__get_ceil_current_number(i)) for i in  Ceils))
        Ceils = sorted(
            Ceils, key=lambda ceil: self.__get_ceil_current_number(ceil))
        #print(", ".join(str(i.get_number()) for i in  Ceils))
        #print(", ".join(str(self.__get_ceil_current_number(i)) for i in  Ceils))

        N: int = 0
        # row_index пустой ячейки
        cell_noop_row_index: int = 0

        for index in range(0, len(Ceils)):
            current_ceil: Ceil = Ceils[index]
            if current_ceil.get_is_noop():
                cell_noop_row_index = current_ceil.current_row_index
                continue
            current_ceil_number: int = current_ceil.get_number()
            Ceils_before = Ceils[:index]
            #print(f'номер текущей ячейки {current_ceil_number}')
            #print('список номеров ячеек до текущей')
            #print(", ".join(str(i.get_number()) for i in  Ceils_before))
            for current_ceil_before in Ceils_before:
                if current_ceil_before.get_is_noop():
                    continue
                if current_ceil_before.get_number() > current_ceil_number:
                    N += 1
            #print(f'результат {N}')
        if self.__count % 2 == 0:
            #print(f'Номер строки с пустой ячейкой {cell_noop_row_index + 1}')
            N += (cell_noop_row_index + 1)

        #print(f'результат {N}')
        #print(f'число строк/столбцов {self.__count}')
        #N += self.__count
        #print(f'результат {N}')
        return (N % 2) == 0

    # функция, выполняющаяся по щелчку мышки
    def mouse_click(self, mouse_pos) -> None:
        if self.__is_build:
            return
        self.step_count += 1
        # получаем координаты курсора мыши
        x, y = mouse_pos[0], mouse_pos[1]
        mouse_rect: Rect = Rect(x, y, 1, 1)
        ceil: Ceil = None
        for sprite in self.sprites():
            if type(sprite) is Ceil:
                ceil = sprite
                ceil_rect: Rect = ceil.rect
                if ceil_rect.contains(mouse_rect):
                    break
        if ceil is None:
            return
        # получаем текущие индексы ячейки
        row_index = ceil.current_row_index
        column_index = ceil.current_column_index
        # формируем список соседних ячеек
        index_list = [[row_index, column_index - 1], [row_index, column_index + 1],
                      [row_index - 1, column_index], [row_index + 1, column_index]]
        for sprite in self.sprites():
            if type(sprite) is Ceil:
                ceil_2: Ceil = sprite
                row_index_2 = ceil_2.current_row_index
                column_index_2 = ceil_2.current_column_index
                index_list_2 = [row_index_2, column_index_2]
                if index_list_2 in index_list and ceil_2.get_is_noop():
                    ceil.current_row_index = row_index_2
                    ceil.current_column_index = column_index_2
                    ceil_2.current_row_index = row_index
                    ceil_2.current_column_index = column_index
                    self.test_aviable_build()
                    self.is_build()
                    return

    # проверка собранности поля
    def is_build(self) -> bool:
        if self.__is_build:
            return True
        for sprite in self.sprites():
            if type(sprite) is Ceil:
                ceil: Ceil = sprite
                if self.__get_ceil_current_number(ceil) != ceil.get_number():
                    return False
        self.__is_build = True
        return True

    # функция возвращения количества ходов
    def get_step_count(self) -> int:
        return self.step_count


pygame.init()
# создание поля
surface = pygame.display.set_mode((800, 800))

# функция установки начальных сведений о игре


def set_difficulty(value, difficulty) -> None:
    global COUNT
    global IM
    COUNT = difficulty
    IM = image.load('mamont.jpg')  # Image.open('mamont.jpg')

# функция рисования текста


def draw_text(surf: Surface, text: str, size: int, x: int, y: int) -> None:
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, (0, 255, 0))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# функция отрисвки текста с заданными параметрами на экране


def show_go_screen(field) -> None:
    surface.blit(surface, pygame.Color(0, 0, 255), surface.get_rect())
    # рисуем текст
    draw_text(surface, "ПОБЕДА!", 64, 400, 400)
    global nickname
    global level
    draw_text(
        surface, f"{nickname.get_value()}, количество сделанных вами ходов: {field.get_step_count()}", 42, 400, 500)
    draw_text(surface, "Нажмите на любую кнопку, чтобы продолжить", 42, 400, 600)
    # файл открыт в режиме 'a' для добавления строк по строчно
    with open("res.txt", "a") as file:
        # запись результата в файл
        file.write(f'{nickname.get_value()}: {level.get_value()[0][0]}: {field.get_step_count()}' + '\n')

    # обновление экрана
    pygame.display.flip()
    waiting = True
    clock = pygame.time.Clock()
    # оставить текст на экране пока его не закроют (кнопкой выйти/любой клавишей)
    while waiting:
        clock.tick(25)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYUP:
                waiting = False


# функция запуска игры
def start_the_game() -> None:
    # x, y = im.size
    pygame.init()

    # screen — холст, на котором нужно рисовать:
    screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    # заполнение экрана цветом
    screen.fill((0, 0, 0))
    running = True

    clock = pygame.time.Clock()
    # установка количества кадров в секунду
    fps = 25

    # заголовок окна
    pygame.display.set_caption('Пятнашки')
    # создаем поле
    field = Field(COUNT, 1, IM)

    while running:
        # цикл приёма и обработки сообщений
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # передать координаты мыши полю
                field.mouse_click(event.pos)
        # field.draw_field(screen)
        # field.update()
        field.draw(screen)
        # временная задержка
        clock.tick(fps)
        # смена кадра
        pygame.display.flip()
        # проверка собрано ли поле
        if field.is_build():
            show_go_screen(field)
            running = False

# функция просмотра результатов


def look_result() -> None:
    #draw_text(surface, "Этот метод пока не работает:(", 64, 400, 150)
    #draw_text(surface, "Нажмите на любую кнопку, чтобы продолжить", 42, 400, 250)
    screen_result = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    # заполнение экрана цветом
    screen_result.fill((255, 0, 0))
    # номер строки с результатом
    number_res = 1
    # horisontal - горизантальная координата текста
    horisontal = 150
    # vertical - вертикальная координата текста
    vertical = 10
    # считывание строк из файла результатов
    with open("res.txt", "r") as file:
        # цикл по строкам файла
        for line in file:
            # выводим текст соотвествующей строчки на экран
            draw_text(screen_result, f"{number_res}) {line}",
                      30, horisontal, vertical)
            # изменяем номер строки
            number_res += 1
            # изменяем вертикальную координату для следующей строчки
            vertical += 30

    draw_text(screen_result,
              "Нажмите на любую кнопку, чтобы продолжить", 42, 400, 750)

    # смена кадра
    pygame.display.flip()
    waiting = True
    clock = pygame.time.Clock()
    while waiting:
        # временная задержка
        clock.tick(25)
        # цикл приёма и обработки сообщений
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYUP:
                waiting = False


# установка музыки
sound = pygame.mixer.Sound("sound.mp3")
# проигрывать музыку бесконечно
sound.play(-1)

# создание меню
menu = pygame_menu.Menu('Пятнашки', 600, 600,
                        theme=pygame_menu.themes.THEME_BLUE)
# поле ввода имени пользователя
nickname = menu.add.text_input('Ваш никнейм: ', default='Никнейм')
# 'шкала' для выбора уровня сложности
level = menu.add.selector('Уровни сложности: ', [
                  ('Простой', 2), ('Cредний', 3), ('Сложный', 4)], onchange=set_difficulty)
# другие элементы меню: кнопки
menu.add.button('Нажмите, чтобы играть', start_the_game)
menu.add.button('Посмотреть результаты', look_result)
menu.add.button('Выход', pygame_menu.events.EXIT)
# добавление меню на экран
menu.mainloop(surface)