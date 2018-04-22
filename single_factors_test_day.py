# -*- coding: utf-8 -*-

import os
os.chdir('D:/yh_min-mfactors')
from functions import *
from address_data import *
import pandas as pd
#import statsmodels.api as sm
import numpy as np

# 某一时间截面，所有个股的收益对所有个股的各个因子进行多元回归，
# 得到某个因子在某个时间个股的残差值，数据量191*227*300，得到有效因子
# 然后对每个截面求得预测收益和实际收益的相关系数，即IC(t)值，最后得到一个时间序列的IC值
# 对IC值进行T检验

# 第一步 读取行业数据
code_HS300 = pd.read_excel(add_gene_file + 'data_mkt.xlsx',sheetname='HS300')
stockList = list(code_HS300['code'][:])
industry = pd.read_pickle\
    (add_gene_file + 'industry.pkl').drop_duplicates()
industry = industry[industry['code'].isin(stockList)]
industry.index = industry['code']
industry.drop(['code'],axis = 1,inplace = True)
industry = industry.T
industry.reset_index(inplace = True)
industry.rename(columns={'index':'date'},inplace = True)

# 第二步 读取风格因子数据
# 因子数据截止到2017-12-06日'
style_filenames = os.listdir(add_Nstyle_factors)
style_list = list(map(lambda x : x[:-4],style_filenames))
for sfilename in style_filenames:
    names = locals()
    names[sfilename[:-4]] = pd.read_csv(add_Nstyle_factors+sfilename)
   
# 第三步 因子值回归,得到行业和风格中性的因子残差值
standard_alpha = os.listdir(add_alpha_day_stand)
for saf in standard_alpha:
    print (saf)
    # saf = 'standard_alpha_001.csv'
    alpha_d = pd.read_csv(add_alpha_day_stand + saf)
    factor_data = possess_alpha(alpha_d,saf)
    df_resid=pd.DataFrame(index=stockList,columns =factor_data['date'])
    n=0
    for date in factor_data['date']:
        print (n)
        X = industry
        Y = factor_data[factor_data['date'] == date] # 每个时间截面的因子值
        Y = Y.loc[:,stockList].T
#        Y = np.array(Y.fillna(0))
        for sfile in style_list:
            mid_sd = eval(sfile)
            X = X.append(mid_sd[mid_sd['date'] == date])
        X = X.loc[:,stockList].T
        X = np.array(X.fillna(0))
        df_resid.iloc[:,n] = resid(Y, X)
        n=n+1
    df_resid.to_csv(add_resid_value_day+saf[9:18]+'_resid.csv',index = False)

# 第三步 针对给定的预测周期，通过回归方程计算单期因子收益率；
# 个股收益率
return_data = pd.read_pickle\
    (add_gene_file + 'dailyreturn.pickle').rename(columns={'symbol':'code'})
return_data['code'] = return_data['code'].apply(lambda x:add_exchange(x))   
return_data = return_data[(return_data['date']>='2016-12-30') & 
                 (return_data['date']<='2017-12-06') & (return_data['code'].isin(stockList))]
return_data=return_data.pivot(index='date', columns='code', values='daily_return')

# 建立回归方程,求单因子收益率
def factor_return(daynum):
    date_list = list(return_data.index)
    resid_value = os.listdir(add_resid_value_day)
    factor_freturn=pd.DataFrame(columns =[['alpha_factors'] + \
                                         [x for x in date_list if x >='2017-01-01' ]])
    n=0
    for ar in resid_value:
        try:
            resid_val = pd.read_csv(add_resid_value_day + ar) 
        except:
            n=n+1
            continue
        print (n)
        factor_freturn.loc[n,'alpha_factors'] = ar[:9]
        for date in resid_val.columns:
            X = industry
#            Y = return_data[return_data.index == date] # 每个时间截面的因子值
            before_daynum = date_list[date_list.index(date)-daynum]
            Y = return_data[return_data.index == before_daynum]
            Y = Y.loc[:,stockList].T
            Y = np.array(Y.fillna(0))
            for sfile in style_list:
                mid_sd = eval(sfile)
                X = X.append(mid_sd[mid_sd['date'] == date])
            resid_v = resid_val.iloc[:,resid_val.columns == date]
            resid_v.index = stockList
            resid_v = resid_v.T
            X = X.append(resid_v)
            X = X.loc[:,stockList].T
            X = np.array(X.fillna(0))        
            factor_freturn.loc[n,date] = beta_value(Y, X)[-1]
        n=n+1
    factor_freturn.to_csv(add_factor_freturn+'factors_return_%s.csv'%daynum,index = False)
    return 0

for daynum in range(1,6):
    factor_return(daynum)

# 第四步 检验因子有效性
freturn_value = os.listdir(add_factor_freturn)
test = pd.read_csv('G:/short_period_mf/factor_freturn_day/factors_return_1.csv')
# 计算年化收益率和IR
for ndays in range(1,6):
    df = pd.DataFrame(columns=['factors','return_peryear','IR'])
    f_return = pd.read_csv(add_factor_freturn+'factors_return_%s.csv'%ndays)
    df['factors'] = f_return['alpha_factors']
    df['return_peryear'] = f_return[f_return.columns[1:]].apply( \
                                  lambda x : ((x/ndays).mean())*252,axis=1)
    df['IR'] = f_return[f_return.columns[1:]].apply( \
                          lambda x : ((x.mean()/ndays)*np.sqrt(252))/((x/ndays).std()),axis=1)
    df.to_csv(add_factor_freturn_IR+'factors_return_IR_%s.csv'%ndays,index=False)


# 第五步 统计因子收益
factors_return_IR = os.listdir(add_factor_freturn_IR)
df = pd.DataFrame(columns=['factors_return_mean','IR_mean'])
n=0
for frI in factors_return_IR:
    frI_return = pd.read_csv(add_factor_freturn_IR+frI)
    df.loc[n,'factors_return_mean'] = frI_return['return_peryear'].mean()
    df.loc[n,'IR_mean'] = frI_return['IR'].mean()
    n = n+1




































































