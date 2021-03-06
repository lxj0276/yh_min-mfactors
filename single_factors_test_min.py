# -*- coding: utf-8 -*-

import os
os.chdir('D:/yh_min-mfactors')
from functions import *
from address_data import *
import pandas as pd
import statsmodels.api as sm
import numpy as np
#import scipy.io
# 某一时间截面，所有个股的收益对所有个股的各个因子进行多元回归，
# 得到某个因子在某个时间个股的残差值，数据量191*227*300，得到有效因子
# 然后对每个截面求得预测收益和实际收益的相关系数，即IC(t)值，最后得到一个时间序列的IC值
# 对IC值进行T检验

# 第一步 读取行业数据
code_HS300 = pd.read_excel(add_gene_file + 'data_mkt.xlsx',sheetname='HS300')
stockList = list(code_HS300['code'][:])
stockList.remove('600485.SH')  #该股票停牌 没有数据
#~stockList_df = pd.DataFrame(stockList,columns = ['code'])
#~stockList_df.to_csv(add_alpha_min_csv+'stockList.csv',index = False)

industry = pd.read_pickle\
    (add_gene_file + 'industry.pkl').drop_duplicates()
industry = industry[industry['code'].isin(stockList)]
industry.index = industry['code']
industry.drop(['code'],axis = 1,inplace = True)
#~industry.rename(columns={'休闲服务':'XXFW','传媒':'CM','公用事业':'GYSY','农林牧渔':'NLMY'\
#~                          ,'化工':'HG','医药生物':'YYSW','商业贸易':'SYMY','国防军工':'GFJG'\
#~                          ,'家用电器':'JYDQ','建筑材料':'JZCL','建筑装饰':'JZZS','房地产':'FDC'\
#~                          ,'有色金属':'YSJS','机械设备':'JXSB','汽车':'QC','电子':'DZ','电气设备':'DQSB'\
#~                          ,'纺织服装':'FZFZ','综合':'ZH','计算机':'JSJ','轻工制造':'QGZZ'\
#~                         ,'通信':'TX','采掘':'CJ','钢铁':'GT','银行':'YH','非银金融':'FYJR'\
#~                         ,'食品饮料':'SPYL','餐饮旅游':'CYLY','黑色金属':'HSJS'},inplace = True)
#~ industry.to_csv(add_alpha_min_csv+'industry.csv',index = False)
industry = industry.T
industry.reset_index(inplace = True)
industry.rename(columns={'index':'date'},inplace = True)

#~    生成交易日序列文件
dateList = open(add_mintime_SerialFile).read().split('\n')
dateList_df = pd.DataFrame(dateList,columns = ['datetime'])
dateList_df.to_csv(add_alpha_min_csv+'min_dateList.csv',index = False)

dateList_day = open(add_daytime_SerialFile).read().split('\n')
dateList_day = pd.DataFrame(dateList_day,columns = ['datetime'])
dateList_day.to_csv(add_alpha_min_csv+'day_dateList.csv',index = False)

#~    mid_dateList = pd.DataFrame(mid_fac['date'],columns = ['date'])
#~    mid_dateList.to_csv(add_alpha_min_csv+'day_dateList.csv',index = False)

# 第二步 读取风格因子数据
# 因子数据截止到2017-12-06日'
style_filenames = os.listdir(add_Nstyle_factors)
style_list = list(map(lambda x : x[:-4],style_filenames))
for sfilename in style_filenames:
#    names = locals()
    mid_fac = pd.read_csv(add_Nstyle_factors+sfilename)
    mid_fac.drop('600485.SH',axis=1, inplace=True)

    mid_fac.drop(['date'],axis = 1,inplace = True)
    mid_fac = mid_fac.T
    mid_fac.to_csv(add_alpha_min_csv+sfilename,index = False,header = False)
#    names[sfilename[:-4]] = pd.read_csv(add_Nstyle_factors+sfilename)
#    eval(sfilename[:-4]).drop('600485.SH',axis=1, inplace=True)
#    eval(sfilename[:-4]).to_csv(add_alpha_min_csv+sfilename,index = False)
   
# 第三步 因子值回归,得到行业和风格中性的因子残差值
def resid(x, y):
    return sm.OLS(x, y).fit().resid

def beta_value(x, y):
    return sm.OLS(x, y).fit().params

def possess_alpha(alpha_data, saf):
#    alpha_data['code'] = alpha_data['code'].apply(lambda x:add_exchange(poss_symbol(x)))
    mid_columns = ['code'] + [x for x in list(alpha_data.columns)[1:] \
                  if x >='2017-01-01'and x<='2017-12-06']
    alpha_data = alpha_data.loc[:,mid_columns]
    alpha_data.index = alpha_data['code']
    alpha_data.drop(['code'],axis = 1,inplace = True)
    alpha_data = alpha_data.T
    alpha_data.reset_index(inplace = True)
    alpha_data.rename(columns={'index':'date'},inplace = True)
    return alpha_data

standard_alpha = os.listdir(add_alpha_min_stand)
for saf in standard_alpha:
#    saf = 'standard_alpha_001.pickle'
    alpha_d = pd.read_pickle(add_alpha_min_stand + saf)
#    alpha_d.to_csv(add_alpha_min_csv + '%s.csv'%saf[9:18],index = False)
#    
#    
#    code = np.array(alpha_d['code'])
#    standard_alpha_001 = np.array(alpha_d)
#    alpha_d.columns = ['code']+list(\
#      map(lambda x : x[:10]+'-'+x[-8:-6]+'-'+x[-5:-3]+'-'+x[-2:],list(alpha_d.columns)[1:]))
#    
#    alpha_d.to_csv('C:/Users/wuwangchuxin/Desktop/mydata.csv',index = False)
##    datetime.shape((alpha_d.columns.size-1),1)
#    scipy.io.savemat('C:/Users/wuwangchuxin/Desktop/mydata.mat',alpha_d)
#    scipy.io.savemat('C:/Users/wuwangchuxin/Desktop/mydata.mat',\
#         mdict={'code':code,'standard_alpha_001':standard_alpha_001,'datetime':datetime})
#    
#    array_1d=np.array([1,2])  
#    print array_1d.shape, array_1d.transpose()  
#    array_1d.shape=(2,1)  
#    print array_1d.shape, array_1d.transpose()  


    factor_data = possess_alpha(alpha_d,saf)
    df_resid=pd.DataFrame(index=stockList,columns =factor_data['date'])
    n=0
    for date in factor_data['date']:
        X = industry
        Y = factor_data[factor_data['date'] == date] # 每个时间截面的因子值
        Y = Y.loc[:,stockList].T
        Y = np.array(Y.fillna(0))
        for sfile in style_list:
            mid_sd = eval(sfile)
            X = X.append(mid_sd[mid_sd['date'] == date[:10]])
        X = X.loc[:,stockList].T
        X = np.array(X.fillna(0))
        df_resid.iloc[:,n] = resid(Y, X)
        print (n)
        n=n+1
    df_resid.to_csv(add_resid_value_min+saf[9:18]+'_resid.csv',index = False)

# 第三步 针对给定的预测周期，通过回归方程计算单期因子收益率；
# 个股收益率
#return_data = pd.read_pickle\
#    (add_gene_file + 'dailyreturn.pickle').rename(columns={'symbol':'code'})
#return_data['code'] = return_data['code'].apply(lambda x:add_exchange(x))   
#return_data = return_data[(return_data['date']>='2016-12-30') & 
#                 (return_data['date']<='2017-12-06') & (return_data['code'].isin(stockList))]
#return_data=return_data.pivot(index='date', columns='code', values='daily_return')
    


# 建立回归方程,求单因子收益率
def factor_return(daynum):
    alpha_d = pd.read_pickle(add_alpha_min_stand + 'standard_alpha_001.pickle')
    factor_data = possess_alpha(alpha_d,saf)
    date_list = list(factor_data['date'])
    resid_value = os.listdir(add_resid_value_min)
    factor_freturn=pd.DataFrame(columns =[['alpha_factors'] + date_list])
    n=0
    for ar in resid_value:
        try:
            resid_val = pd.read_csv(add_resid_value_min + ar) 
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
freturn_value = os.listdir(add_factor_return_min)
# 计算年化收益率和IR
for nmins in [240,60,120,180]:
    df = pd.DataFrame(columns=['factors','return_peryear','IR'])
    f_return = pd.read_csv(add_factor_return_min+'factor_return_%s.csv'%nmins,header=None)
    df['factors'] = ['alpha_'+alpha_filename(x) for x in range(1,192)]
    df['return_peryear'] = f_return.apply(lambda x : ((x/nmins).mean())*252*240,axis=1)
    df['IR'] = f_return.apply( \
                  lambda x : ((x.mean()/nmins)*np.sqrt(252*240))/((x/nmins).std()),axis=1)
    df.to_csv(add_factor_min_freturn_IR+'factors_return_min_IR_%s.csv'%nmins,index=False)


# 第五步 统计因子收益
factors_return_IR = os.listdir(add_factor_min_freturn_IR)
df = pd.DataFrame(columns=['factors_return_mean','IR_mean'])
n=0
for frI in factors_return_IR:
    frI_return = pd.read_csv(add_factor_min_freturn_IR+frI)
    df.loc[n,'factors_return_mean'] = frI_return['return_peryear'].mean()
    df.loc[n,'IR_mean'] = frI_return['IR'].mean()
    n = n+1

#  factors_return_mean    IR_mean
#0         -0.00538119 -0.0630792
#1          -0.0426761  -0.288343
#2          -0.0512058  -0.426739
#3          -0.0166101  -0.142192

# 第六步 找出4个预测期效果都比较好的因子  
factors_return_IR = os.listdir(add_factor_min_freturn_IR)
df_score = pd.DataFrame(columns=['factors'])
for frI in factors_return_IR:
    print (frI)
    frI_return2 = pd.read_csv(add_factor_min_freturn_IR+frI)
    frI_return2.sort_values(by='return_peryear',axis=0,ascending=True,inplace=True)
    frI_return2['score_return'] = list(range(1,192))
    frI_return2.sort_values(by='IR',axis=0,ascending=True,inplace=True)
    frI_return2['score_IR'] = list(range(1,192))
    if len(frI)==28:
        mid_name = frI[22:24]
    else:
        mid_name = frI[22:25]
    frI_return2['score_%s'%mid_name] = frI_return2['score_return']+ frI_return2['score_IR']
    if frI == 'factors_return_min_IR_120.csv':
        df_score['factors'] = frI_return2['factors']
    frI_return2 = frI_return2[['factors','return_peryear','IR','score_%s'%mid_name]]
    frI_return2.rename(columns={'return_peryear':'return_%s'%mid_name,\
                                'IR':'IR_%s'%mid_name},inplace = True)
    df_score = pd.merge(df_score,frI_return2,on='factors',how='inner')
df_score['score_res'] = df_score['score_120']+df_score['score_60']\
                        +df_score['score_180']+df_score['score_240']
df_score.sort_values(by='score_res',axis=0,ascending=False,inplace=True)
df_score.to_csv(add_effecive_factors_min+'effecive_factors_min.csv',index=False)

df_score.columns
































































