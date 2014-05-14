 #!/usr/bin/env python2

"""
    Author: Fabian Brix
    with help of 'thesaurus.com'
"""

predict = {}
predict['inc'] = ['increase', 'inflate', 'rise', 'raise', 'augment', 'multiply']
predict['dec'] = ['tumble', 'decline', 'lessen', 'diminish', 'decrease', 'mitigate', 'reduce', 'curb']

price = {}
price['low'] = ['low', 'low-cost', 'cheap', 'low-budget', 'dirt-cheap', 'bargain', 'cut-price', 'cut-rate', 'afford', 'affordable']
price['high'] = ['high', 'expensive', 'costly', 'pricey', 'pricy', 'overpriced']

sentiment = {}
sentiment['positive'] = ['bargain', 'good', 'purchase', 'acquired', 'wealth', 'confident', 'satisfied', 'happy', 'smile', 'laugh', 'joke', 'delight', 'gratitude']
sentiment['neutral'] = ['alright', 'average', 'stagnate', 'level', 'content']
sentiment['negative'] = ['hungry', 'starving', 'anger', 'angry', 'hate', 'misfortune', 'craving', 'pessimist', 'complain', 'incontent', 'crying', 'disappointed', 'dissatisfied', 'distress', 'deprived', 'worry', 'upset', 'pain', 'depressed', 'agitated']

poverty = {}
poverty['high'] = ['poor', 'starving', 'craving', 'poverty', 'hardship', 'debt', 'misfortune']
poverty['low'] = ['lot', 'much', 'many', 'money', 'wealth', 'well-off', 'power', 'extravagance', 'affluence', 'worth', 'capital', 'estate', 'inheritance', 'plenty', 'thrive']

needs = {}
needs['low'] = ['satisfied', 'saturated', 'plenty', 'fortune', 'nonessential', 'comfort']
needs['high'] = ['crave', 'long', 'want', 'relish', 'must', 'demand', 'wish', 'urgent', 'urge', 'essential', 'need']

# include cooking related words in high supply
supply = {}
supply['high'] = ['available', 'full', 'enough', 'sustain', 'access', 'convenient', 'dish', 'meal', 'ate', 'eat', 'cook', 'fry', 'heat', 'curry']
supply['low'] = ['run-out', 'empty', 'depleted', 'rotting']


predictors_dict = {'predict': predict, 'price': price, 'sentiment': sentiment, 'poverty': poverty, 'needs': needs, 'supply': supply}

if __name__ == '__main__':
    print predictors_dict

