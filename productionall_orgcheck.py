import pandas as pd
from datetime import datetime, timedelta
from seffaflik.elektrik import uretim
import matplotlib.pyplot as plt

def prodorg():
    today = datetime.today().strftime('%Y-%m-%d')
    presentday = datetime.now()
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday2 = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')
    tomorrow = (presentday + timedelta(1)).strftime('%Y-%m-%d')
    #%%
    x = uretim.tum_santraller_gerceklesen(baslangic_tarihi=yesterday2, bitis_tarihi=yesterday)
    #%%
    x['DateTime'] = pd.to_datetime(x.Tarih) + x.Saat.astype('timedelta64[h]')
    x.drop(['Tarih','Saat'],axis=1,inplace=True)
    x.set_index('DateTime',inplace=True)
    ayin4u = x.loc[:'{} 23:00:00'.format(yesterday2)]
    ayin5i = x.loc['{} 00:00:00'.format(yesterday):]
    df1 = ayin4u.copy()
    df2 = ayin5i.copy()
    df1.reset_index(inplace=True)
    df2.reset_index(inplace=True)
    df1.drop('DateTime',axis=1,inplace=True)
    df2.drop('DateTime',axis=1,inplace=True)
    new = df2-df1 
    toplamlar = pd.DataFrame(new[new.columns].sum())
    toplamlar.rename(columns = {0:'PROD'},inplace=True) 
    toplamlar.sort_values(by='PROD',ascending=False) 

    maxx = toplamlar.sort_values(by='PROD',ascending=False).head(15)
    minn = toplamlar.sort_values(by='PROD',ascending=False).tail(15)
    return maxx, minn

maxx, minn= prodorg()

#%% EXPORTING PDF

fig, ax =plt.subplots(figsize=(3,1))
ax.axis('off')
the_table = ax.table(cellText = maxx.values, rowLabels = maxx.index, loc='center', colLabels = maxx.columns, cellLoc='center')
the_table.set_fontsize(8)
plt.savefig("MAX.pdf", format="pdf", bbox_inches = 'tight')

fig, ax =plt.subplots(figsize=(3,1))
ax.axis('off')
the_table = ax.table(cellText = minn.values, rowLabels = minn.index, loc='center', colLabels = minn.columns, cellLoc='center')
the_table.set_fontsize(8)
plt.savefig("MIN.pdf", format="pdf", bbox_inches = 'tight')
