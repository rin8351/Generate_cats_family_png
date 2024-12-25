from PIL import Image, ImageDraw, ImageFont
import random
import os

def load_images_from_folder(folder_path):
    images = []
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png')):
            img_path = os.path.join(folder_path, filename)
            try:
                with Image.open(img_path) as img:
                    rgb_img = img.convert('RGB')  # Преобразование в RGB
                    images.append(rgb_img)
            except IOError:
                print(f"Cannot load image {filename}")
    return images

def choose_random_image(images):
    return random.choice(images)

def combine_images(ear, eyes, body, tail, legs):
    # Create a vertical combination of ear, eyes, and body
    vertical_height = ear.height + eyes.height + body.height
    vertical_width = max(ear.width, eyes.width, body.width)
    vertical_image = Image.new('RGB', (vertical_width, vertical_height))
    
    # Paste ear, eyes, and body one below the other
    current_height = 0
    vertical_image.paste(ear, ((vertical_width - ear.width) // 2, current_height))
    current_height += ear.height
    vertical_image.paste(eyes, ((vertical_width - eyes.width) // 2, current_height))
    current_height += eyes.height
    vertical_image.paste(body, ((vertical_width - body.width) // 2, current_height))
    
    # Now attach the tail to the right of the body
    final_width = vertical_width + tail.width
    combined_image = Image.new('RGB', (final_width, vertical_height))
    combined_image.paste(vertical_image, (0, 0))
    
    # Высчитываем высоту начала тела
    body_start_height = ear.height + eyes.height
    tail_top_position = body_start_height + (body.height - tail.height)
    combined_image.paste(tail, (vertical_width, tail_top_position))

    # Finally, add legs below the vertical combination adjusting to the new width
    final_image = Image.new('RGB', (final_width, vertical_height + legs.height))
    final_image.paste(combined_image, (0, 0))
    final_image.paste(legs, ((final_width - legs.width) // 2, vertical_height))

    return final_image

def gen_form():
    folders = {'ear': 'ear', 'eyes': 'eyes', 'body': 'body', 'tail': 'tail', 'legs': 'legs'}
    parts_images = {part: load_images_from_folder(path) for part, path in folders.items()}
    selected_parts = {part: choose_random_image(images) for part, images in parts_images.items()}
    cat_image = combine_images(selected_parts['ear'], selected_parts['eyes'], selected_parts['body'], selected_parts['tail'], selected_parts['legs'])
    return cat_image, selected_parts

def gen_form_kitten(selected_parts):
    cat_image = combine_images(selected_parts['ear'], selected_parts['eyes'], selected_parts['body'], selected_parts['tail'], selected_parts['legs'])
    return cat_image

def add_text_to_image(img, text, position):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=26)  
    except IOError:
        font = ImageFont.load_default()
    draw.text(position, text, font=font, fill=(0, 0, 0))

def create_monotone_cat(color, name):
    img, selected_parts = gen_form()
    img = img.convert('RGB')
    pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            if pixels[x, y] in gray_colors:
                pixels[x, y] = color
    add_text_to_image(img, name, (10, 10))  # Добавляем имя в верхний левый угол изображения
    return img, selected_parts

def create_kitten(parent1_color, parent2_color, name,sel_parts1, sel_parts2):
    sel_body = random.choice([sel_parts1['body'], sel_parts2['body']])
    sel_ear = random.choice([sel_parts1['ear'], sel_parts2['ear']])
    sel_eyes = random.choice([sel_parts1['eyes'], sel_parts2['eyes']])
    sel_tail = random.choice([sel_parts1['tail'], sel_parts2['tail']])
    sel_legs = random.choice([sel_parts1['legs'], sel_parts2['legs']])
    selected_parts = {'body': sel_body, 'ear': sel_ear, 'eyes': sel_eyes, 'tail': sel_tail, 'legs': sel_legs}
    img = gen_form_kitten(selected_parts)
    pixels = img.load()
    colors_used = []
    part_colors = {}
    for gray_color in gray_colors:
        chosen_color = random.choice([parent1_color, parent2_color])
        part_colors[gray_color] = chosen_color
        colors_used.append(chosen_color)
    for x in range(img.width):
        for y in range(img.height):
            if pixels[x, y] in gray_colors:
                if pixels[x, y]==(252, 252, 252):
                    if part_colors[pixels[x, y]] not in main_colors:
                        main_colors.append(part_colors[pixels[x, y]])
                pixels[x, y] = part_colors[pixels[x, y]]
    add_text_to_image(img, name, (10, 10))  # Добавляем имя
    return img, colors_used, selected_parts

# Прочитать имена из файла
with open('cats_name.TXT', 'r', encoding='utf-8') as f:
    cats_names = f.read().splitlines()

def create_grand_kitten(colors1, colors2, main_colors, name, sel_parts1, sel_parts2):
    sel_body = random.choice([sel_parts1['body'], sel_parts2['body']])
    sel_ear = random.choice([sel_parts1['ear'], sel_parts2['ear']])
    sel_eyes = random.choice([sel_parts1['eyes'], sel_parts2['eyes']])
    sel_tail = random.choice([sel_parts1['tail'], sel_parts2['tail']])
    sel_legs = random.choice([sel_parts1['legs'], sel_parts2['legs']])
    selected_parts = {'body': sel_body, 'ear': sel_ear, 'eyes': sel_eyes, 'tail': sel_tail, 'legs': sel_legs}
    img = gen_form_kitten(selected_parts)
    pixels = img.load()

    # Объединяем цвета обоих родителей и удаляем дубликаты, создавая набор уникальных цветов
    unique_colors = list(set(colors1 + colors2))

    # Выбираем случайное количество цветов (2, 3 или максимум доступное количество уникальных цветов)
    num_colors_to_use = random.choice([2, 3, len(unique_colors)])
    selected_colors = random.sample(unique_colors, num_colors_to_use)

    # Выбираем один случайный цвет для основных частей тела
    main_color = random.choice(main_colors)

    # Создаем словарь окраски для каждой серой части, распределяя цвета циклически для неосновных частей
    part_colors = {gray_color: selected_colors[i % num_colors_to_use] for i, gray_color in enumerate(gray_colors)}

    # Применяем цвета к изображению
    for x in range(img.width):
        for y in range(img.height):
            if pixels[x, y] in gray_colors:
                if pixels[x, y] == (252, 252, 252):  # Проверяем, является ли часть основной
                    pixels[x, y] = main_color
                else:
                    pixels[x, y] = part_colors[pixels[x, y]]
    
    add_text_to_image(img, name, (10, 10))  # Добавляем имя
    return img, selected_colors, main_color, selected_parts

gray_colors = [
    (195, 195, 195), (212, 212, 212), (224, 224, 224),
    (235, 235, 235), (201, 201, 201), (194, 194, 194),
    (189, 189, 189), (181, 181, 181), (171, 171, 171),
    (247, 247, 247), (252, 252, 252)
]

cats_colors = [
    (255, 0, 0), (0, 0, 255), (0, 128, 0), (255, 255, 0),
    (255, 165, 0), (255, 192, 203), (128, 0, 128),
    (165, 42, 42), (128, 128, 128), (50, 205, 50), (0, 255, 255),
    (255, 0, 255), (128, 128, 0),
    (230, 230, 250), (135, 206, 250), (152, 251, 152), (255, 218, 185),
    (255, 182, 193), (240, 128, 128), (255, 255, 224),
    (216, 191, 216), (245, 245, 220), (175, 238, 238), (255, 228, 225),
    (250, 250, 210), (255, 229, 180), (245, 255, 250)
]

main_colors = []

colors1 = random.sample(cats_colors, 2)
colors2 = random.sample(cats_colors, 2)

parent1, sel_parts1 = create_monotone_cat(colors1[0], "Parent 1")
parent2, sel_parts2 = create_monotone_cat(colors1[1], "Parent 2")
kitten1, colors_kitten1, sel_part_kitten1 = create_kitten(colors1[0], colors1[1], 'Kitten 1', sel_parts1, sel_parts2)

parent3, sel_parts3 = create_monotone_cat(colors2[0], "Parent 3")
parent4, sel_parts4 = create_monotone_cat(colors2[1], "Parent 4")
kitten2, colors_kitten2, sel_part_kitten2 = create_kitten(colors2[0], colors2[1], 'Kitten 2', sel_parts3, sel_parts4)

choose_name = random.choice(cats_names)
string = 'GrandKitten1 = '
grand_kitten_name = string + choose_name.split(' ')[1]
grand_kitten1, grang_kitten_colors1, main_color1, sel_part_great_gran1 = create_grand_kitten(colors_kitten1, colors_kitten2, main_colors, grand_kitten_name, sel_part_kitten1, sel_part_kitten2)
add_text_to_image(grand_kitten1, grand_kitten_name, (10, 10))

# следующая пара родителей и их котенок
main_colors = []

color3 = random.sample(cats_colors, 2)
color4 = random.sample(cats_colors, 2)

parent5, sel_parts5 = create_monotone_cat(color3[0], "Parent 5")
parent6, sel_parts6 = create_monotone_cat(color3[1], "Parent 6")
kitten3, colors_kitten3, sel_part_kitten3 = create_kitten(color3[0], color3[1], 'Kitten 3', sel_parts5, sel_parts6)

parent7, sel_parts7 = create_monotone_cat(color4[0], "Parent 7")
parent8, sel_parts8 = create_monotone_cat(color4[1], "Parent 8")
kitten4, colors_kitten4, sel_part_kitten4 = create_kitten(color4[0], color4[1], 'Kitten 4', sel_parts7, sel_parts8)

choose_name = random.choice(cats_names)
string = 'GrandKitten2 = '
grand_kitten_name2 = string + choose_name.split(' ')[1]
grand_kitten2, grang_kitten_colors2, main_color2, sel_part_great_gran2 = create_grand_kitten(colors_kitten3, colors_kitten4, main_colors, grand_kitten_name2, sel_part_kitten3, sel_part_kitten4)
add_text_to_image(grand_kitten2, grand_kitten_name2, (10, 10))

main_colors_for_ggkitten = [main_color1, main_color2]

# Теперь генерируем Правнука от двух Внуков
choose_name = random.choice(cats_names)
string = 'GreatGrandKitten = '
great_grand_kitten_name = string + choose_name.split(' ')[1]
great_grand_kitten, great_grand_kitten_colors, main_color, sel_part_great_gran3 = create_grand_kitten(grang_kitten_colors1, grang_kitten_colors2, main_colors_for_ggkitten, great_grand_kitten_name, sel_part_great_gran1, sel_part_great_gran2)
add_text_to_image(great_grand_kitten, great_grand_kitten_name, (10, 10))


layout = [
    [parent1, parent2, kitten1,grand_kitten1, great_grand_kitten],
    [parent3, parent4, kitten2],
    [parent5, parent6, kitten3,grand_kitten2],
    [parent7, parent8, kitten4],
]
def display_cats(layout):
    # Расчет размеров для всего изображения
    max_width = max(cat.width for row in layout for cat in row)  # максимальная ширина кота
    max_height = max(cat.height for row in layout for cat in row)  # максимальная высота кота
    total_width = max_width * max(len(row) for row in layout)  # общая ширина (макс. количество котов в строке)
    total_height = max_height * len(layout)  # общая высота (количество строк)

    # Создаем новое изображение
    combined_img = Image.new('RGB', (total_width, total_height), (189, 255, 255))  # задаем цвет фона

    # Располагаем котов в изображении
    y_offset = 0
    for row in layout:
        x_offset = 0
        for cat in row:
            combined_img.paste(cat, (x_offset, y_offset))
            x_offset += cat.width  # сдвигаемся на ширину кота вправо
        y_offset += max_height  # сдвигаемся на высоту кота вниз

    # Сохраняем итоговое изображение
    combined_img.save('cats_family.png')

# Пример вызова функции
display_cats(layout)
