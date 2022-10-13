import pygame
import ast
import sys
from pygame.locals import (
    MOUSEBUTTONUP,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
)

# lab = [[0,0,0,0,0],[1,1,0,1,0],[1,1,0,0,0],[1,1,0,1,1],[1,1,0,0,0]]

visited = []
path = []
a = []

SCREEN_WIDTH = 1005
SCREEN_HEIGHT = 1005
tile = 5
cols = 201
rows = 201

running = True
Black = (0, 0, 0)
White = (255, 255, 255)
Red = (255, 0, 0)
Green = (0, 255, 0)
Blue = (0, 0, 255)


class TailRecurseException(BaseException):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


def tail_call_optimized(g):
    """
    This function decorates a function with tail call
    optimization. It does this by throwing an exception
    if it is it's own grandparent, and catching such
    exceptions to fake the tail call optimization.
    This function fails if the decorated
    function recurses in a non-tail context.
    """

    def func(*args, **kwargs):
        f = sys._getframe()
        if f.f_back and f.f_back.f_back \
                and f.f_back.f_back.f_code == f.f_code:
            raise TailRecurseException(args, kwargs)
        else:
            while 1:
                try:
                    return g(*args, **kwargs)
                except TailRecurseException as e:
                    args = e.args
                    kwargs = e.kwargs

    func.__doc__ = g.__doc__
    return func


class Lab_room:
    "Класс для генерации лабиринта"

    def __init__(self, x_start, y_start, width_height, is_white):
        self.x_start = x_start
        self.y_start = y_start
        self.width_height = width_height
        self.is_white = is_white


def lab_to_graph(lab):
    "Преобразование лабиринта в граф. В форме списка смежности"
    graph = {}
    for x in range(0, len(lab)):
        for y in range(0, len(lab[0])):
            if lab[x][y] == 0:
                graph[(x, y)] = []
    for x, y in graph.keys():
        if y < len(lab[0]) - 1:
            if lab[x][y + 1] == 0:
                graph[(x, y)].append((x, y + 1))
                graph[(x, y + 1)].append((x, y))
        if x < len(lab) - 1:
            if lab[x + 1][y] == 0:
                graph[(x, y)].append((x + 1, y))
                graph[(x + 1, y)].append((x, y))
    return graph


@tail_call_optimized
def find_all_paths(graph, x, y, end_x, end_y, path):
    """
    Функция для поиска всех путей в графе.
    Из-за того, что она рекурсивная, на больших лабиринтах происходит переполнение стека.
    @tail_call_optimized - реализует хвостовую рекурсию, для того, чтобы избегать этой ошибки
    К сожалению, лабиринт 200 * 200 все равно слишком велик, и на нем у меня функция не работает
    Но на маленьких лабиритнах - работает. С задачей поиска всех путей в лабиринте 200 * 200 не справился
    """
    path.append((x, y))
    if x == end_x and y == end_y:
        print(path, file=file1)  # Записываем пути в файл all_paths.txt
    else:
        for i, j in graph[(x, y)]:
            if (i, j) not in path:
                find_all_paths(graph, i, j, end_x, end_y, path)
    path.pop()


def find_all_paths_alter(graph, x, y, end_x, end_y, path):
    """
    Алгоритм BFS для поиска кратчайшего пути в графе.
    Я оставил аргумент path, чтобы у обеих функций поиска были одинаковые аргументы
    """
    queue = [[(x, y)]]
    visited = []
    if (x, y) == (end_x, end_y):
        print("Same Node")
        return
    while queue:
        path = queue.pop(0)
        current = path[-1]
        if current not in visited:
            try:
                neighbours = graph[current]
            except KeyError as e:
                print("Выбирая конец или начало пути, вы кликнули на стенку лабиринта", e)
                global running
                running = False
                break
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)

                if neighbour == (end_x, end_y):
                    print(path, file=file1)  # Записываем путь в файл all_paths.txt
                    return path
            visited.append(current)


def calculate_coordinates(x_array, y_array, is_white):
    "Расчет координат комнат лабиринта"
    if SCREEN_WIDTH < SCREEN_HEIGHT or SCREEN_WIDTH == SCREEN_HEIGHT:
        width_height = SCREEN_WIDTH / rows
    else:
        width_height = SCREEN_HEIGHT / cols

    x_coordinate = x_array * width_height
    y_coordinate = y_array * width_height

    return Lab_room(x_coordinate, y_coordinate, width_height, is_white)


def get_position(pos):
    "Преобразование координат клика мышки по комнате лабиринта в координаты самой комнаты"
    x = pos[0] // tile
    y = pos[1] // tile
    return (tile * x, tile * y)


def Create_lab(lab):
    "Генерация (прорисовка) лабиринта"
    for row in lab:
        for square in row:
            surf = pygame.Surface((square.width_height, square.width_height))
            if square.is_white:
                surf.fill((255, 255, 255))
            else:
                surf.fill((0, 0, 0))
            rect = surf.get_rect()
            screen.blit(surf, (square.x_start, square.y_start))
            pygame.display.flip()


def drawGrid():
    """
    Генерация линий для разграничения комнат в лабиринте
    Стоит использовать только для маленьких лабиринтов
    """
    blockSize = SCREEN_WIDTH // rows
    for x in range(0, SCREEN_WIDTH, blockSize):
        for y in range(0, SCREEN_WIDTH, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            pygame.draw.rect(screen, Black, rect, 1)
            pygame.display.flip()


Labyrintian = open('Labyrint_1', 'r+')
lab1 = []
filecontents = Labyrintian.readlines()  # Получаем лабиринт из файла Labyrint_1
for line in filecontents:
    obs = ast.literal_eval(line)  # Преобразуем сторку в список
    lab1.append(obs)

Labyrintian.close()
Lab_for_pygame = []  # Двумерный список всех комнат лабиринта с правильными цветами для функции Create_lab

for y in range(len(lab1[0])):
    l_row = []
    for x in range(len(lab1)):
        l_row.append(calculate_coordinates(x, y, not lab1[y][x]))
    Lab_for_pygame.append(l_row)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Labyrint')
clock = pygame.time.Clock()

count = 0  # Использую для обеспечения правильного порядка действий
# Лабиринт состоит из клеток двух цветов: черные - стенки, белые - комнаты
# Сначала 2 клика мышкой по белым комнатам лабиринта для выбора комнат начала пути и конца пути
# Можно кликнуть и на черный цвет, но тогда ни одного пути не найдется
# Потом клики SPACE для показа всех путей по очереди
# ESCAPE для завершения работы с лабиринтом
all_coordinates = []
graph = lab_to_graph(lab1)
Create_lab(Lab_for_pygame)

while running:
    if count == 3:
        file1 = open('all_paths.txt', 'r+')
        count += 1
    # drawGrid() # Рисует линии для разграничения комнат
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            if event.key == K_SPACE and count == 4:
                # Create_lab(Lab_for_pygame) # Обновляет лабиринт.
                # Если путей несколько, надо включить для того, чтобы пути не накладывались друг на друга при прорисовке
                currentPlace = file1.readline()  # Считываем пути из файла all_paths.txt
                data = ast.literal_eval(currentPlace)
                if data == [10]:  # Испоьзую как флаг для своевременной остановки считывания
                    file1.close()
                    count += 1
                else:
                    for x in data:  # Перекрашиваем в зеленый цвет все клетки пути
                        surf = pygame.Surface((tile, tile))
                        surf.fill((0, 255, 0))
                        rect = surf.get_rect()
                        screen.blit(surf, (x[1] * tile, x[0] * tile))
                        pygame.display.flip()

        if event.type == MOUSEBUTTONUP and count < 2:
            count += 1
            pos = pygame.mouse.get_pos()  # Получаем координаты клика мышкой по лабиринту (начало и конец пути)
            coordinates = get_position(pos)
            all_coordinates.append(coordinates)
            print(coordinates, all_coordinates)
            surf = pygame.Surface((tile, tile))  # Перекрашиваем начало и конец в красный цвет
            surf.fill((255, 0, 0))
            rect = surf.get_rect()
            screen.blit(surf, (coordinates[0], coordinates[1]))
            pygame.display.flip()
        if event.type == MOUSEBUTTONUP and count == 2:
            count += 1
            file1 = open('all_paths.txt', 'w+')  # Функция find_all_paths_alter запишет пути в файл all_paths.txt
            find_all_paths_alter(graph, all_coordinates[0][1] // tile, all_coordinates[0][0] // tile,
                                 all_coordinates[1][1] // tile, all_coordinates[1][0] // tile, path)
            file1.write('[10]')  # Флаг конца списка путей
            file1.close()

    clock.tick(30)
pygame.quit()
