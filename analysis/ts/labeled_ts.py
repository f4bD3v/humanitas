import pandas as pd

class LabeledSeries:
    label = ''
    series = pd.Series()
    def __init__(self, l, s):
        label = l
        series = s
