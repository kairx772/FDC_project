import pandas as pd
import numpy as np
import finlab
from finlab import data
import plotly.express as px

class TwStockTreeMap:

    def __init__(self, close, basic_info, start=None, end=None):
        self.start = start
        self.end = end
        self.close = close
        self.basic_info = basic_info

    # dataframe filter by selected date
    def df_date_filter(self, df, start=None, end=None):
        if start:
            df = df[df.index >= start]
        if end:
            df = df[df.index <= end]
        return df

    # map stock_name from basic info(stock_id +name)
    def map_stock_name(self, basic_info, s):
        target = basic_info[basic_info['stock_id'].str.find(s) > -1]
        if len(target) > 0:
            s = target['stock_id'].values[0]
        return s

    def create_data(self):
        close_data = self.df_date_filter(self.close, self.start, end=self.end)
        return_ratio = (close_data.iloc[-1] / close_data.iloc[0]).dropna().replace(np.inf, 0)
        return_ratio = round((return_ratio - 1) * 100, 2)
        return_ratio = pd.concat([return_ratio, close_data.iloc[-1]], axis=1).dropna()
        return_ratio = return_ratio.reset_index()
        return_ratio.columns = ['stock_id', 'return_ratio', 'close']
        return_ratio['stock_id'] = return_ratio['stock_id'].apply(lambda s: self.map_stock_name(basic_info, s))
        return_ratio = return_ratio.merge(self.basic_info[['stock_id', '產業類別', '市場別', '實收資本額(元)']], how='left',
                                          on='stock_id')
        return_ratio = return_ratio.rename(columns={'產業類別': 'category', '市場別': 'market', '實收資本額(元)': 'base'})
        return_ratio['market_value'] = round(return_ratio['base'] / 10 * return_ratio['close'] / 100000000, 2)
        return_ratio = return_ratio.dropna(thresh=5)
        return_ratio['country'] = 'TW-Stock'
        return_ratio['return_ratio_text_info']=return_ratio['return_ratio'].astype(str).apply(lambda s: '+' + s if '-' not in s else s) + '%'
        return return_ratio

    def create_fig(self, relative_market_strength=False):
        df = self.create_data()
        if relative_market_strength is True:
            color_continuous_midpoint = np.average(df['return_ratio'], weights=df['base'])
        else:
            color_continuous_midpoint = 0
        fig = px.treemap(df, path=['country', 'market', 'category', 'stock_id'], values='market_value',
                         color='return_ratio',
                         color_continuous_scale='Tealrose',
                         color_continuous_midpoint=color_continuous_midpoint,
                         custom_data=['return_ratio_text_info','close'],
                         title=f'TW-Stock Market TreeMap({self.start}~{self.end})',
                         width=1350, 
                         height=900)
        
        fig.update_traces(textposition='middle center', 
                          textfont_size=24,
                          texttemplate= "%{label}<br>%{customdata[0]}<br>%{customdata[1]}"
                          )
        return fig

finlab.login('vPrVSU1klPn98i5OBK3HQRjQBhR9odXvB6dqSOsU/GvjjkNSgQ2Q0vr7Y/kSI8Wa')
close=data.get('price:收盤價')
basic_info=data.get('company_basic_info')

#@title 台股漲跌與市值板塊圖
start= '2021-05-20' #@param {type:"date"}
end = '2021-05-21' #@param {type:"date"}
relative_market_strength = "False" #@param ["False", "True"] {type:"raw"}

df=TwStockTreeMap(close,basic_info,start,end).create_fig()
df.show()