# traffic_accident_analysis

# U-Traffic_Accident_processing.ipynb

## numpy.where()
dfに条件処理によって値を変える
numpy.where()は、条件式conditionを満たす場合（真Trueの場合）はx、満たさない場合（偽Falseの場合）はyとするndarrayを返す関数。
```
traffic_accident_data["accident_type"] = \
np.where(traffic_accident_data["事故内容"] == 1, "死亡", np.where(traffic_accident_data["事故内容"] == 2, "負傷", None))

if traffic_accident_data["事故内容"] == 1:
    死亡
elif traffic_accident_data["事故内容"] == 2:
    負傷
else:
    None
```
```
traffic_accident_data["road_bypass"] = np.where(traffic_accident_data.road_cd_l1 > 0, "バイパス区間",
                                                                           np.where(traffic_accident_data.road_cd_l1 == 0, "現道区間又は包括路線", None))
                                                                           
if traffic_accident_data.road_cd_l1 > 0:
    バイパス区間
elif traffic_accident_data.road_cd_l1 == 0:
    現道区間又は包括路線
else:
    None
```


## map関数
DataFrame の**特定のcolumn**に対してのみ map() メソッドを使用することができます。
```
traffic_accident_data["road_cd_f4"] = list(map(lambda text:text[0:4], traffic_accident_data["路線コード"].astype(str)))
```
第一引数に関数、第二引数に加工元となる値群を指定
map関数の第一引数は関数の形で指定する必要はなく、lambda式でも良いとされています。lambda（ラムダ）とはある処理に名前を付けずに定義したもののことで、def文によって関数定義をすることもありません。
```
map(lambda text:text[0:4], traffic_accident_data["路線コード"].astype(str))
<map at 0x1256420a0>

list(map(lambda text:text[0:4], traffic_accident_data["路線コード"].astype(str)))
['4001',
 '4001',
 '4013',
 '4013',
 '3999',
 '9900',....
```

## apply関数
**DataFrame 全体** を変更する apply() メソッド
```
traffic_accident_data["accident_date"] = \
pd.to_datetime(traffic_accident_data[['発生日時　　年', '発生日時　　月', '発生日時　　日', '発生日時　　時', '発生日時　　分']].\
               apply(lambda x: '{}-{}-{} {}:{}'.format(x[0], x[1], x[2], x[3], x[4]), axis=1))

traffic_accident_data["tiiki-code"] = traffic_accident_data[['genuine_pref_cd', '市区町村コード']]\
                                                            .apply(lambda x: '{}{}'.format(x[0], x[1]), axis=1)
```
df = df.apply(dfに対する処理) → 全ての行に処理が適応

https://www.delftstack.com/ja/howto/python-pandas/difference-between-pandas-apply-map-and-applymap/


## 正規表現を使ったreplace

```
import re

def multiple_replace(text, adict):
    rx = re.compile('|'.join(adict))
    
    def dedictkey(text):
        for key in adict.keys():
            if re.search(key, text):
                return key
 
    def one_xlat(match):
        return adict[dedictkey(match.group(0))]
 
    return rx.sub(one_xlat, text)
```
```
replace_list = {'1':'上','2':'下','0':'対象外'}
traffic_accident_data['road_updown_type'] = list(map(lambda text:multiple_replace(text, replace_list) ,
                                                                                traffic_accident_data['上下線'].astype(str)))
                                                                                
replace_list = {'11':'昼－明',
                      '12':' 昼－昼',
                      '13':' 昼－暮',
                      '21':'夜－暮',
                      '22':'夜－夜',
                      '23':'夜－明'
                        }

traffic_accident_data['day_night_type'] = list(map(lambda text:multiple_replace(text, replace_list) ,
                                                                                traffic_accident_data['昼夜'].astype(str)))
```


# U-Traffic_Accident_EDA.ipynb

## matplotlib日本語表示
```
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
```


## Groupby → Plot
```
def GroupbyPlot(df:pd.DataFrame,
                             group:str,
                             target:str,
                             y_label:str,
                             x_label:str):
    group_name_summary = df.groupby(group)[target].agg([np.mean, "count"])
    index_list = group_name_summary.index.tolist()
    
    group_name_summary = group_name_summary.reset_index()
    
    fig, ax = plt.subplots(figsize=(13,5))
    ax3 = ax.twinx()
    rspine = ax3.spines['right'] 
    rspine.set_position(('axes', 1.15))
    ax3.set_frame_on(True)
    ax3.patch.set_visible(False)
    fig.subplots_adjust(right=0.7)
    group_name_summary["mean"].plot(ax=ax, style='r-', kind="line")
    group_name_summary["count"].plot(ax=ax, secondary_y=True,kind="bar",color='b',alpha=0.5 );
    # ax.set_title('');
    ax.set_ylabel(y_label);
    ax.set_xlabel(x_label); 
    ax.set_xticklabels(index_list);
    ax3.set_ylabel('count');
    return group_name_summary
```

## 地域メッシュ

地域メッシュ（ちいきメッシュ）とは、統計に利用するために、緯度・経度に基づいて地域をほぼ同じ大きさの網の目（メッシュ）に分けたものである。メッシュを識別するためのコードを地域メッシュコードと言う。（地域メッシュ - Wikipedia）

地域メッシュは区分の方法により、大きさの異なるいくつかの区画が定められています。

・１次メッシュ: 一辺約80km.
・２次メッシュ: 一辺約10km. １次メッシュを縦横８分割したもの。
・３次メッシュ: 一辺約1km. ２次メッシュを縦横10分割したもの。
・４次メッシュ: 一辺約500m. ３次メッシュを縦横2分割したもの。
・５次メッシュ: 一辺約250m. ４次メッシュを縦横2分割したもの。
・６次メッシュ: 一辺約125m. ５次メッシュを縦横2分割したもの。

### 地域メッシュから緯度経度を割り出すサンプルコード
```
def get_latlon(meshCode):

    # 文字列に変換
    meshCode = str(meshCode)

    # １次メッシュ用計算
    code_first_two = meshCode[0:2]
    code_last_two = meshCode[2:4]
    code_first_two = int(code_first_two)
    code_last_two = int(code_last_two)
    lat  = code_first_two * 2 / 3
    lon = code_last_two + 100

    if len(meshCode) > 4:
        # ２次メッシュ用計算
        if len(meshCode) >= 6:
            code_fifth = meshCode[4:5]
            code_sixth = meshCode[5:6]
            code_fifth = int(code_fifth)
            code_sixth = int(code_sixth)
            lat += code_fifth * 2 / 3 / 8
            lon += code_sixth / 8

        # ３次メッシュ用計算
        if len(meshCode) == 8:
            code_seventh = meshCode[6:7]
            code_eighth = meshCode[7:8]
            code_seventh = int(code_seventh)
            code_eighth = int(code_eighth)
            lat += code_seventh * 2 / 3 / 8 / 10
            lon += code_eighth / 8 / 10

    print(lat, lon)
```
###  地域メッシュから地域メッシュを割り出すサンプルコード
```
def latlon2mesh(lat, lon):
    #1次メッシュ上2けた
    quotient_lat, remainder_lat = divmod(lat * 60, 40)
    first2digits = str(quotient_lat)[0:2]

    #1次メッシュ下2けた
    last2digits = str(lon - 100)[0:2]
    remainder_lon = lon - int(last2digits) - 100

    #1次メッシュ
    first_mesh = first2digits + last2digits

    #2次メッシュ上1けた
    first1digits, remainder_lat = divmod(remainder_lat, 5)

    #2次メッシュ下1けた
    last1digits, remainder_lon = divmod(remainder_lon * 60, 7.5)

    #2次メッシュ
    second_mesh = first_mesh + str(first1digits)[0:1] + str(last1digits)[0:1]

    #3次メッシュ上1けた
    first1digits, remainder_lat = divmod(remainder_lat * 60, 30)

    #3次メッシュ下1けた
    last1digits, remainder_lon = divmod(remainder_lon * 60, 45)

    #3次メッシュ
    third_mesh = second_mesh + str(first1digits)[0:1] + str(last1digits)[0:1]
    
    return third_mesh
```
