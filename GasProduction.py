import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import date, datetime, timedelta
import numpy as np
from seffaflik.elektrik import uretim
from matplotlib.backends.backend_pdf import PdfPages

df = pd.read_csv('GasProduction.csv')
# df = df.drop('Unnamed: 0', axis = 1)
#df.sort_values(by='DateTime', ascending = True, inplace=True)
"""
Reset tek bir kere çalıştırılacak sonra commande alınacak
"""
#df = df.reset_index(drop=True)
df = df.set_index('DateTime')
#df = df.reset_index(drop=False)

today = datetime.today().strftime('%Y-%m-%d')

yesterday = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')

uretim1 = uretim.gerceklesen(baslangic_tarihi=yesterday, bitis_tarihi=today, santral_id = '2217')
uretim1['DateTime'] = pd.to_datetime(uretim1.Tarih) + uretim1.Saat.astype('timedelta64[h]')
uretim1 = uretim1.set_index('DateTime')
uretim1 = pd.DataFrame(uretim1['Toplam'])
uretim1 = uretim1.replace(np.nan, 0)

PlantID = ['1113','1449','2411','1426','2170','1673','754','869','1424','2048','966','2334','2045','1112','1224','687','1230','638','893','962','661']
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
uretim1 = uretim1.set_axis(['KAZAN SODA', 'HAMITABAT', 'HABAS 1', 'HABAS 2', 'ENERJISA BANDIRMA', 
                            'ACWA', 'AK ENERJI ERZIN', 'AKSA ANTALYA', 'BILGIN SAMSUN', 
                            'YENI ELEKTRIK', 'IC ANADOLU', 'RWE TURCAS', 'CENGIZ 610', 
                            'ENERJISA BANDIRMA 2', 'EUAS TEKIRDAG A', 'EUAS TEKİRDAG B', 'EUAS BURSA', 
                            'EUAS ISTANBUL', 'EUAS ISTANBUL FUELOIL', 'BAYMINA','İZMİR','GEBZE'], axis=1, inplace=False)
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

df.to_csv('GasProduction.csv', index = True)


files_path = r"/Users/toygar/Documents/PYTHON Examples/NYKEnergy/Santral_Production"

files = ['GasProduction.csv']


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
#    plt.savefig('{}PRODUCTION365.png'.format(col))
    plt.show()


for col in df.columns:
    df_seag = seag(df[col].resample("D").mean()[:today-timedelta(days=1)].rolling(7).mean())
    plot_seag(df_seag, "{} 7 Day Rolling Production".format(col))

#%% EXPORTING PDF

x = pd.read_csv('GasProduction.csv')

x.tail(24).to_excel('santrallergas.xlsx')

yesterday = date.today() - timedelta(days=1)
yesterday.strftime('%d%m%y')

fig, ax =plt.subplots(figsize=(12,4))
ax.axis('off')
the_table = ax.table(cellText=x[x.columns[0:8]].tail(24).values,colLabels=x.columns[0:8],loc='center',fontsize=20)
pp = PdfPages("Gas1_Uretim.pdf")
pp.savefig(fig, bbox_inches='tight')
pp.close()

fig, ax =plt.subplots(figsize=(12,4))
ax.axis('off')
the_table = ax.table(cellText=x[x.columns[8:16]].tail(24).values,colLabels=x.columns[8:16],loc='center',fontsize=20)
pp = PdfPages("Gas2_Uretim.pdf")
pp.savefig(fig, bbox_inches='tight')
pp.close()

fig, ax =plt.subplots(figsize=(12,4))
ax.axis('off')
the_table = ax.table(cellText=x[x.columns[16:23]].tail(24).values,colLabels=x.columns[16:23],loc='center',fontsize=20)
pp = PdfPages("Gas3_Uretim.pdf")
pp.savefig(fig, bbox_inches='tight')
pp.close()

