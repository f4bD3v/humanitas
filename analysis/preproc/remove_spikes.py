import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

csv_in1 = os.getcwd()+''
csv_in2 = os.getcwd()+''


def remove_spikes(df_full, df_ts, threshold):
    #generate return df_ret from df_ts

    #remove spikes in df_full according to df_ret

    ddf = ddf[ddf_ret<threshold]
    ddf_ret = ddf_ret[ddf_ret<threshold]
    ddf = ddf[ddf_ret > -threshold]
    ddf_ret = ddf_ret[ddf_ret > -threshold]

    return ddf, ddf_ret



if __name__ == '__main__':
