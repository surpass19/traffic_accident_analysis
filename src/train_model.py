import pandas as pd
import numpy as np

from sklearn.metrics import confusion_matrix, roc_auc_score, f1_score, precision_score, recall_score, auc, roc_curve, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GroupShuffleSplit

import lightgbm as lgb
from scipy.sparse import csr_matrix

from scipy import interp
import matplotlib.pyplot as plt

from pylab import rcParams
import tqdm
import pickle


def frange(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step

def classification_and_roc_analysis(k, classifier, X_train, y_train, group_id, visualize):     
    # Classification and ROC analysis
    # Run classifier with cross-validation and plot ROC curves
    cv = GroupShuffleSplit(n_splits=10,random_state=123)
    classifier = classifier

    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)

    i = 0
    for train, test in cv.split(X_train, y_train, groups = group_id):
        each_train = X_train[X_train.index.isin(train) ]
        each_train = csr_matrix(each_train)
               
        classifier.fit(each_train ,
                          y_train[y_train.index.isin(train)])

        each_test =  X_train[X_train.index.isin(test)]
        each_test = csr_matrix(each_test)
        
        probas_ =  classifier.predict_proba(each_test)

        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(y_train[ y_train.index.isin(test)], probas_[:,1:])
        tprs.append(interp(mean_fpr, fpr, tpr))
        tprs[-1][0] = 0.0
        roc_auc = auc(fpr, tpr)
        aucs.append(roc_auc)
        if visualize:
            plt.plot(fpr, tpr, lw=1, alpha=0.3,
                     
        label='ROC fold %d (AUC = %0.2f)' % (i, roc_auc))

        i += 1
        
    if visualize:
        plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',
                 label='Chance', alpha=.8)

    print("the number of data: ",len(y_train))
    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    
    if visualize:
        plt.plot(mean_fpr, mean_tpr, color='b',
                 label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),
                 lw=2, alpha=.8)
 
    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    
    if visualize:
        plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                         label=r'$\pm$ 1 std. dev.')

        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic example')
        plt.legend(loc="lower right")
        plt.show()

    return mean_auc, classifier



dataset = pd.read_pickle("../data/dataset.pickle")
teacher_flag = pd.read_pickle("../data/teacher_flag.pickle")

# 欠損値補完は最低限のもの
dataset = dataset.fillna(-1)


X = dataset.drop(columns=["third_mesh"])
# 変数名を格納しておく
feature_name_table = pd.DataFrame([[ 'V' + str(i) for i in range(len(X.columns.tolist()))], X.columns.tolist()]).transpose()
feature_name_table.columns = ['name', 'genuine_name']

# 変数名をv[0-9]に変更する
X.columns = [ 'V' + str(i) for i in range(len(X.columns.tolist()))]

X = pd.concat([X, dataset['third_mesh']], axis=1)

# 教師データ
y = teacher_flag

X_train, X_test, y_train, y_test = train_test_split(X ,
                                                    y,
                                                    test_size=0.3,
                                                    random_state=123,
                                                    stratify=y)


import random
random.seed(123)

learning_rate = list(map(lambda value:round(value,2) , frange(0.1, 0.3, 0.01)))
max_depth = list(map(lambda value:round(value,2) , frange(1, 20, 1)))
num_leaves = list(map(lambda value:round(value,2) , frange(32, 64, 1)))


# パラメータに関するデータフレーム
parameter_df = pd.DataFrame(index=range(30))

parameter_df['learning_rate'] = list(map(lambda parameter:random.choice(learning_rate) , range(parameter_df.index.size)))
parameter_df['max_depth'] = list(map(lambda parameter:random.choice(max_depth) , range(parameter_df.index.size)))
parameter_df['num_leaves'] = list(map(lambda parameter:random.choice(num_leaves) , range(parameter_df.index.size)))
parameter_df['mean_auc'] = np.nan


for iteration in tqdm.tqdm(range(parameter_df.index.size)):
    classifier = lgb.LGBMClassifier(
                            max_depth=parameter_df.max_depth[iteration],
                            learning_rate=parameter_df.learning_rate[iteration], 
                            num_leaves=parameter_df.num_leaves[iteration], 
                            class_weight="balanced",
                            seed=123)
    
    # classification and draw roc curve
    parameter_df['mean_auc'][iteration] = classification_and_roc_analysis(k=3, classifier=classifier,
                                                                            X_train=X_train.drop(columns=["third_mesh"]),
                                                                            y_train=y_train,
                                                                            group_id=pd.factorize( X_train.third_mesh.tolist() )[0], visualize=False)[0]
    print(iteration,":", parameter_df['mean_auc'][iteration],":",parameter_df.mean_auc.max())
    print('max_depth=',parameter_df.max_depth[iteration], '|' ,'max_learning_rate=',parameter_df.learning_rate[iteration],
              '|' , 'num_leaves=',parameter_df.num_leaves[iteration])


parameter_df_ranking = parameter_df.sort_values(by=["mean_auc"], ascending=False).reset_index(drop=True)


classifier = lgb.LGBMClassifier(
                                max_depth=parameter_df_ranking.max_depth[0],
                                learning_rate=parameter_df_ranking.learning_rate[0],
                                num_leaves=parameter_df_ranking.num_leaves[0],            
                                class_weight="balanced",
                                seed=123)

model = classification_and_roc_analysis(k=3,
                                        classifier=classifier,
                                        X_train=X_train.drop(columns=["third_mesh"]),
                                        y_train=y_train,
                                        group_id=pd.factorize( X_train.third_mesh.tolist() )[0],visualize=False)[1]

# モデルを保存する
filename = 'finalized_model.sav'
pickle.dump(model, open(filename, 'wb'))

feature_name_table["importance"] = model.feature_importances_.tolist()

y_pred_test = model.predict_proba(X_test.drop(columns=["third_mesh"]))
y_pred_oof = (y_pred_test[:,1] > y_pred_test[:,1].mean()).astype(int)

labels = ['ok', 'ng']
cm =  confusion_matrix(np.where(y_test.values == 1, 'ok', 'ng'),np.where(  y_pred_oof == 1, 'ok', 'ng'), labels=labels)

# データフレームに変換
cm_labeled = pd.DataFrame(cm, columns=labels, index=labels)

print(cm_labeled)
