from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import date, datetime, timedelta
import numpy as np
from seffaflik.elektrik import uretim


#%% IMPORTING
df = pd.read_csv('CoalProduction.csv')
#df = df.drop('Unnamed: 0', axis = 1)
#
#df = df.reset_index(drop=True)
df = df.set_index('DateTime')

today = datetime.today().strftime('%Y-%m-%d')

yesterday = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')

uretim1 = uretim.gerceklesen(baslangic_tarihi=yesterday, bitis_tarihi=today, santral_id = '706')
uretim1['DateTime'] = pd.to_datetime(uretim1.Tarih) + uretim1.Saat.astype('timedelta64[h]')
uretim1 = uretim1.set_index('DateTime')
uretim1 = pd.DataFrame(uretim1['Toplam'])
uretim1 = uretim1.replace(np.nan, 0)

PlantID = ['996','2264','877','2065','712','892','965','705','710','738','2391','2198','1693','708','2305','688','1758','1723','782','1731','1085','2227','1699','1641','694']
for i in range(len(PlantID)):
    uretim2 = uretim.gerceklesen(baslangic_tarihi=yesterday, bitis_tarihi=today, santral_id = PlantID[i])
    uretim2['DateTime'] = pd.to_datetime(uretim2.Tarih) + uretim2.Saat.astype('timedelta64[h]')
    uretim2 = uretim2.drop('Tarih', axis = 1)
    uretim2 = uretim2.drop('Saat', axis = 1)
    uretim2 = uretim2.set_index('DateTime')
    uretim2 = pd.DataFrame(uretim2['Toplam'])
    uretim2 = uretim2.reset_index(drop=False)
    uretim1 = pd.merge(uretim1, uretim2, how="outer", on=["DateTime", "DateTime"])
    print("İşlem tamamlandı")
uretim1 = uretim1.set_index('DateTime')
uretim1 = uretim1.set_axis(['YATAGAN', 'SILOPI', 'ZETESEREN1', 'ZETESEREN2', 'ZETESEREN3', 
                            'EUASCAN', 'EUASCAYIRHAN', 'ICDASBEKIRLI', 'SOMA', 
                            'KEMERKOY', 'SEYITOMER', 'HIDROGENSOMA', 'KANGAL', 
                            'ENERJISATUFANBEYLI', 'YENIKOY', 'CANKOMUR', 'CATALAGZI', 
                            'YUNUSEMRE', 'AKSAGOYNUK','ORHANELI','ATLAS','ISKEN','CENAL','IZDEMIR','COLAKOGLU1','COLAKOGLU2'], axis=1, inplace=False)
df = df.reset_index(drop=False)
uretim1 = uretim1.reset_index(drop=False)

df['DateTime'] = pd.to_datetime(df.DateTime)
uretim1['DateTime'] = pd.to_datetime(uretim1.DateTime)

df = df.set_index('DateTime')
uretim1 = uretim1.set_index('DateTime')

df = pd.concat([df, uretim1])
df = df.reset_index(drop=False)
df.drop_duplicates(subset="DateTime",keep = "last", inplace = True)
df = df.set_index('DateTime')

df.to_csv('CoalProduction.csv', index = True)

# You must change document location
files_path = r"/Users/toygar/Documents/PYTHON Examples/NYKEnergy/Santral_Production"

files = ['CoalProduction.csv']


dfs = []
for file in files:
    dfs.append(pd.read_csv(os.path.join(files_path,file), header=0, index_col=0, parse_dates=True))


df = pd.concat(dfs).sort_index()
daily = df.resample("D").mean()
today = datetime.today().replace(hour=0, minute=0,second=0,microsecond=0)
daily = daily[:today-timedelta(days=1)]

def seag(ts):
    seag = ts.groupby([ts.index.dayofyear, ts.index.year]).first().unstack()
    return seag


def plot_seag(seag, title=""):
    plt.figure(figsize=(8,5))
    plt.fill_between(
        seag.index, seag[seag.columns[:-1]].min(axis=1),
        seag[seag.columns[:-1]].max(axis=1), color="gray")
    plt.plot(seag[today.year], color="red", label=today.year)
    plt.title(title, loc="left")
    plt.grid(True)
    plt.legend(loc=0)
    plt.xlim(seag.index.min(), seag.index.max())
    plt.ylabel('MWh')
    plt.xlabel('Months')
    plt.show()


for col in df.columns:
    df_seag = seag(df[col].resample("D").mean()[:today-timedelta(days=1)].rolling(7).mean())
    plot_seag(df_seag, "{} 7 Day Rolling Production".format(col))

