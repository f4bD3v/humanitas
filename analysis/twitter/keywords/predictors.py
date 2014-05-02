"""
    Author: Fabian Brix
    with help of 'thesaurus.com'
"""

predict = {}
predict['inc'] = list('increase', 'inflate', 'rise', 'raise', 'augment', 'multiply')
predict['dec'] = list('decline', 'lessen', 'diminish', 'decerase', 'mitigate', 'reduce', 'curb')

price = {}
price['low'] = (['low', 'low-cost', 'cheap', 'low-budget', 'dirt-cheap', 'bargain', 'cut-price', 'cut-rate', 'affordable'],['not expensive'])
price['high'] = (['high', 'expensive', 'costly', 'pricey', 'pricy', 'overpriced'], ['not afford','not cheap'])

sentiment = {}
sentiment['positive'] = (['bargain', 'good', 'purchase', 'acquired', 'wealth', 'confident', 'satisfied', 'happy', 'smile', 'laugh', 'joke', 'delight', 'gratitude'],[])
sentiment['neutral'] = (['alright', 'average', 'stagnate', 'level', 'content'],['not bad', 'no complaints'])
sentiment['negative'] = (['hungry', 'starving', 'anger', 'angry', 'hate', 'misfortune', 'craving', 'pessimist', 'complain', 'incontent', 'crying', 'disappointed', 'dissatisfied', 'distress', 'deprived', 'worry', 'upset', 'pain', 'depressed', 'agitated'],['not happy'])

poverty = {}
poverty['high'] = (['poor', 'starving', 'craving', 'poverty', 'hardship', 'debt', 'misfortune'],['no money', 'no means'])
poverty['low'] = (['lot', 'much', 'many', 'money', 'wealth', 'well-off', 'power', 'extravagance', 'affluence', 'worth', 'capital', 'estate', 'inheritance', 'plenty', 'thrive'],[])

needs = {}
needs['low'] = (['satisfied', 'saturated', 'plenty', 'fortune', 'nonessential', 'comfort'],[])
needs['high'] = (['crave', 'long', 'want', 'relish', 'must', 'demand', 'wish', 'urgent', 'urge', 'essential'])

# include cooking related words in high supply
supply = {}
supply['high'] = (['available', 'full', 'enough', 'sustain', 'access', 'convenient', 'dish', 'meal', 'ate', 'eat', 'cook', 'fry', 'heat', 'curry'],[])
supply['low'] = (['run-out', 'empty', 'depleted', 'rotting'],['nothing left'])

#starving



