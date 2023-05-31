import streamlit as st
import datetime
import numpy as np
import pandas as pd

today=datetime.datetime.now()+datetime.timedelta(days=-1)
url='https://raw.githubusercontent.com/Qnnis/my_streamlit/master/data/每日数据.csv'
df0=pd.read_csv(url,encoding='gb18030',thousands=',',header=0,sep=',',parse_dates=['日期'])

#@st.cache_data
def get_UN_data():
    AWS_BUCKET_URL = "https://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
    return df.set_index("Region")

def get_date(df):
    df['年']=df['日期'].map(lambda x:x.year)
    df['季']=df['日期'].map(lambda x:x.quarter)
    df['月']=df['日期'].map(lambda x:x.month)
    df['周']=df['日期'].map(lambda x:x.week+1)
    df['周几']=df['日期'].map(lambda x:x.isoweekday())
    df['日']=df['日期'].map(lambda x:x.day)
    df['月日']=df['月'].astype(str)+'-'+df['日'].astype(str)
    df['周报计算周']=df['日期'].map(lambda x:(x+datetime.timedelta(days=-3)).week+1)
    
def get_index(df):
    df['月日']=df['日期'].map(lambda x:x.month).astype(str)+'-'+df['日期'].map(lambda x:x.day).astype(str)
    df=df.set_index('月日')

def get_cols(df):
    df['客服销售占比']=df['客服销售额']/df['店铺销售额']
    df['转化率']=df['最终付款人数']/df['询单人数']
    df['Callin转化率']=df['接待人数']/df['访客数']
    
    df['平响']=df['总响应时间']/df['客服消息数']
    df['首响']=df['总首响时间']/df['接待人数']
    df['满意比']=df['总满意量']/df['收到评价数']
    df['满意度']=(df['评价很满意']*5+df['评价满意']*4+df['评价一般']*3+df['评价不满意']*2+df['评价很不满意']*1)/df['收到评价数']
     
    df['退款率']=df['店铺退款金额']/df['店铺销售额']
    df['仅退款率']=df['仅退款金额']/df['店铺销售额']
    df['退货退款率']=df['退款率']-df['仅退款率']
    df['发货后退货退款率']=df['退货退款率']/(1-df['仅退款率'])
    
    df['客服客单价']=df['客服销售额']/df['客服销售人数']
    df['客服客件数']=df['客服销售量']/df['客服销售人数']
    df['客服AOV']=df['客服销售额']/df['客服销售量']
    
    df['静默销售额']=df['店铺销售额']-df['客服销售额']
    df['静默销售人数']=df['店铺销售人数']-df['客服销售人数']
    df['静默销售量']=df['店铺销售量']-df['客服销售量']
    
    df['静默客单价']=df['静默销售额']/df['静默销售人数']
    df['店铺客单价']=df['店铺销售额']/df['店铺销售人数']
    df['店铺AOV']=df['店铺销售额']/df['店铺销售量'] 
    
    df['客服销售额']=round(df['客服销售额']/10000.0,1)
    df['店铺销售额']/=10000.0
    df['访客数']/=10000.0
    
    return df

#主体
#st.markdown('Streamlit Demo')
st.title('LBG-CS日报')
st.caption('日期:'+today.strftime("%Y-%m-%d"))

# 一、整体数据
st.header('一、整体数据')
st.caption('明细如下')

df_all=df0.groupby(['年','month']).sum().reset_index().query("(年=='TY')").rename({'month':'月'},axis=1)
del df_all['年']
df_all.loc['YTD']=df_all.sum()
df_all=get_cols(df_all).set_index('月')
st.dataframe(df_all)
#df_all

df_by_day=df0.groupby(['年','日期']).sum().reset_index('年',drop=True)
chart_data = df_by_day.loc[:,'客服销售额']
st.line_chart(chart_data)

# 二、店铺数据
df_shop=df0.groupby(['店铺','年','month']).sum().reset_index().query("(年=='TY')").rename({'month':'月'},axis=1)
df_shop=get_cols(df_shop).set_index('店铺')

df_shop_sales=df_shop[['月','客服销售额','客服销售占比','询单人数','转化率','客服客单价','客服客件数','客服AOV']].sort_values('客服销售额',ascending=False)
df_shop_service=df_shop[['月','接待人数','访客数','Callin转化率','平响','首响','满意比']].sort_values('接待人数',ascending=False)
df_shop_rrc=df_shop[['月','店铺AOV','退款率','仅退款率','退货退款率','发货后退货退款率']].sort_values('退款率',ascending=True)

st.header('二、店铺数据')
shops= st.multiselect("请选择店铺", list(set(df_shop.index)), ["NET-A-PORTER","TORYBURCH"])
months= st.multiselect("请选择月份", list(set(df_shop['月'])), [5])

# 2.1 销售数据
#st.subheader('')
df_shop_sales = df_shop_sales.loc[(df_shop_sales.index.isin(shops))&(df_shop_sales.月.isin(months))]
st.write('#### 1.1 销售数据',df_shop_sales)

# 2.2 服务数据
df_shop_service = df_shop_service.loc[(df_shop_service.index.isin(shops))&(df_shop_service.月.isin(months))]
st.write('#### 1.2 服务数据',df_shop_service)

# 2.3 退款数据
df_shop_rrc = df_shop_rrc.loc[(df_shop_rrc.index.isin(shops))&(df_shop_rrc.月.isin(months))]
st.write('#### 1.3 退款数据',df_shop_rrc)
