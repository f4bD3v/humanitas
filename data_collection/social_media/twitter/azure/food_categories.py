#---------------------------------
#Joseph Boyd - joseph.boyd@epfl.ch
#---------------------------------

def get_food_words():
    food_words = {}
    food_words['rice'] = list(['rice'])
    food_words['wheat'] = list(['wheat', 'bread', 'flour'])
    food_words['coriander'] = list(['coriander'])
    food_words['potato'] = list(['potato'])
    food_words['onion'] = list(['onion'])
    food_words['oil'] = list(['oil'])
    food_words['sugar'] = list(['sugar'])
    food_words['salt'] = list(['salt'])
    food_words['tea'] = list(['tea'])
    food_words['coffee'] = list(['coffee'])
    food_words['fish'] = list(['fish', 'carp', 'catfish', 'prawn'])
    food_words['chicken'] = list(['chicken', 'poultry'])
    food_words['corn'] = list(['corn', 'maize'])
    food_words['egg'] = list(['egg'])
    food_words['milk'] = list(['milk'])
    food_words['general'] = list(['breakfast', 'lunch', 'dinner', 'meal', 'food', 'eat'])
    return food_words

def print_foods():
    foods = get_food_words()
    for food in foods:
        print foods[food]



