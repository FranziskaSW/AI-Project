from random import randint
color = []


for _ in range(30):
    color.append('#%06x' % randint(0, 0xFFFFFF))


def get_all_colors():
    ''' :return: Color Options '''
    return color
