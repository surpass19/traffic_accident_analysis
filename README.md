# traffic_accident_analysis

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







