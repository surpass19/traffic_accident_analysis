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

# U-Traffic_Accident_LGBM.ipynb

## 特徴量ごとの特徴量作成(Groupby)

```
# メッシュごとの特徴量作成用
mesh_df = traffic_accident_data[(traffic_accident_data.accident_date > "2019-01-01") &\
                                                   (traffic_accident_data.accident_date < "2019-09-01")].reset_index(drop=True)

mesh_summary_df = mesh_df.groupby('third_mesh')['death_flag'].agg([np.sum, "count"]).reset_index()
mesh_summary_df.columns = ["third_mesh", "death_count", "accident_count"]
mesh_summary_df.tail()
# ---------------------------------- #
third_mesh	death_count	accident_count
44738	68410593	0	1
44739	68410594	0	1
44740	68410680	0	1
44741	68411042	0	1
44742	68411504	0	1
# ---------------------------------- #

summary_column_name_list = ["road_type","road_bypass","road_updown_type","day_night_type","weather_type",
                                                "terrain_type","road_condition_type","road_shape_type","traffic_lights_type",
                                                "pause_sign_type_a","pause_sign_type_b","pause_display_type_a","pause_display_type_b",
                                                "road_width_type","road_alignment_type","zone_regulation_type",
                                                "pedestrian_road_division_type","accident_vehicle_type","age_type_a","age_type_b",
                                                "parties_type_a","parties_type_b","use_type_a","use_type_b","vehicle_shape_type_a",
                                                "vehicle_shape_type_b","speed_regulation_type_a","speed_regulation_type_b",
                                                "collision_site_type_a","collision_site_type_b","damage_to_vehicle_type_a",
                                                "damage_to_vehicle_type_b","airbag_equipment_type_a","airbag_equipment_type_b",
                                                "side_airbag_equipment_type_a","side_airbag_equipment_type_b","weekday_type","holiday_type"]

for each_variable_name in summary_column_name_list:
    df_pv = pd.pivot_table(data=mesh_df,
                                       fill_value=0,
                                       index="third_mesh",
                                       columns=each_variable_name,
                                       aggfunc = {each_variable_name:"count"}).reset_index()
    
    column_list = [df_pv.columns.levels[0][1]]
    add_column_list = [ each_variable_name + "_" + str(_) for _ in df_pv.columns.levels[1].tolist()[:-1]]
    column_list.extend(add_column_list)
    df_pv.columns = column_list
    mesh_summary_df = pd.merge(mesh_summary_df, df_pv, on="third_mesh", how="left")
    print(each_variable_name)
```
内訳, (参考にできる → Github : U-youtube-scraping_to_visualization/visualizing.ipynb)
```
df_pv = pd.pivot_table(data=mesh_df,
                                       fill_value=0,
                                       index="third_mesh",
                                       columns=each_variable_name,
                                       aggfunc = {each_variable_name:"count"}).reset_index()
# ---------------------------------- #
third_mesh	holiday_type
holiday_type		その他	前日	当日
0	36235060	1	0	0
1	36243193	2	0	0
2	36244049	2	0	0
3	36244101	1	0	0
4	36244102	12	0	0
...	...	...	...	...
44738	68410593	1	0	0
44739	68410594	1	0	0
44740	68410680	1	0	0
44741	68411042	1	0	0
44742	68411504	0	0	1
# ---------------------------------- #

column_list = [df_pv.columns.levels[0][1]]
# ---------------------------------- #
['third_mesh']
# ---------------------------------- #

add_column_list = [ each_variable_name + "_" + str(_) for _ in df_pv.columns.levels[1].tolist()[:-1]]
# ---------------------------------- #
['holiday_type_その他', 'holiday_type_前日', 'holiday_type_当日']
# ---------------------------------- #

df_pv.columns = column_list
df_pv
# ---------------------------------- #
third_mesh	holiday_type_その他	holiday_type_前日	holiday_type_当日
0	36235060	1	0	0
1	36243193	2	0	0
2	36244049	2	0	0
3	36244101	1	0	0
4	36244102	12	0	0
...	...	...	...	...
44738	68410593	1	0	0
44739	68410594	1	0	0
44740	68410680	1	0	0
44741	68411042	1	0	0
44742	68411504	0	0	1
# ---------------------------------- #
```
