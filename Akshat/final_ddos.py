# -*- coding: utf-8 -*-
"""Final_DDOS.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PcS1Y0WVN8-OVxVaDb9HfHX49iyseW42

#Setup
"""

# Commented out IPython magic to ensure Python compatibility.
# Python ≥3.5 is required
import sys

# Scikit-Learn ≥0.20 is required
import sklearn

import warnings 
warnings.filterwarnings("ignore")

# Common imports
import numpy as np
import pandas as pd
import os

# To plot pretty figures
# %matplotlib inline
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

#File extraction
from zipfile import ZipFile
from urllib.request import urlopen
import io

"""#Get the data

Extracting column names from website
"""

colnames = ["duration","protocol_type","service","flag",
            "src_bytes","dst_bytes","land","wrong_fragment",
            "urgent","hot","num_failed_logins","logged_in",
            "num_compromised","root_shell","su_attempted",
            "num_root","num_file_creations","num_shells",
            "num_access_files","num_outbound_cmds",
            "is_host_login","is_guest_login","count",
            "srv_count","serror_rate","srv_serror_rate",
            "same_srv_rate","diff_srv_rate","srv_diff_host_rate",
            "una1","una2","dst_host_count","dst_host_srv_count",
            "dst_host_same_srv_rate","dst_host_diff_srv_rate",
            "dst_host_same_src_port_rate","dst_host_srv_diff_host_rate",
            "dst_host_serror_rate","dst_host_srv_serror_rate",
            "dst_host_rerror_rate","dst_host_srv_rerror_rate","result"]

f = urlopen('https://raw.githubusercontent.com/AkshatGarg7/DDOS-Detection-using-Machine-Learning/master/Dataset/dataset.zip').read()
zip_file = ZipFile(io.BytesIO(f))
train_df = pd.read_csv(zip_file.open('kddcup.csv'),header = None,names = colnames)
#print("train_df shape -> ",train_df.shape)
test_df = pd.read_csv(zip_file.open('corrected.csv'),header = None,names = colnames)
# print("test_df shape -> ",test_df.shape)

"""#Data Manpulation and Analysis using Pandas framework"""

frames = [train_df,test_df]
df = pd.concat(frames)
print("Shape of Dataset: ",df.shape)

df.head()

df.describe()

print('Null values in dataset are: ',len(df[df.isnull().any(1)]))

attack_normal = df["result"].values
attack_normal = set(attack_normal)
print("Different type of attacks/normal are:\n ",attack_normal)
print("No. of different attacks/normal are: ",len(attack_normal))

print(pd.Series(df.result.value_counts(ascending=False)))

df['result'].value_counts().plot(kind ='bar',figsize = (10,5), 
                                        title= 'Distribution of classes in result',
                                        xlabel = 'Subclasses',
                                        ylabel='Frequency count')

# print(pd.Series(df.protocol_type.value_counts(ascending=True)))

"""Dropping duplicate values"""

df_new = df.copy()
df_new.drop_duplicates(subset=colnames, keep='first', inplace = True)
# print("Shape of Dataset before dropping duplicates: ",df.shape)
print("Shape of Dataset after dropping duplicates: ",df_new.shape)

df_new['result'].value_counts().plot(kind ='bar',figsize = (10,5), 
                                        title= 'Distribution of classes after dropping duplicates in result',
                                        xlabel = 'Subclasses',
                                        ylabel='Frequency count')

print("Percentage distribution of classes in the output classes.")
(df_new['result'].value_counts() / df_new.shape[0]) * 100

"""####As per the above plot we can see that class `normal.` and `neptune.` has the highest distritbution. And rest all classes has the very low distribution. This makes it a class imbalance problem.

Checking type of data for all the features
"""

numerical_attr = []
categorical_attr = []
for feature,datatype in zip(df_new.columns,df_new.dtypes):
    if datatype != 'object':
        numerical_attr.append(feature)
    else:
        categorical_attr.append(feature)
print("Numerical attributes: \n", numerical_attr)
print("\nNumerical attributes count: ", len(numerical_attr))
print("-"*50)
print("Categorical attributes: \n", categorical_attr)
print("\nCategorical attributes count: ", len(categorical_attr))

"""The data has 38 numerical attributes and 4 categorical attributes."""

df_new.describe()

def range_num(series):
    return series.max() - series.min()
def outliers(series):
    outliers_count = 0
    iqr = series.quantile(.75) - series.quantile(.25)
    iqr_upperbound = series.quantile(.75) + iqr*1.5
    iqr_lowerbound = series.quantile(.25) - iqr*1.5
    for oneValue in series.values:
        if oneValue > iqr_upperbound or oneValue < iqr_lowerbound:
            outliers_count += 1
    return outliers_count
def outliersPercentage(series):
    outliers_count = 0
    iqr = series.quantile(.75) - series.quantile(.25)
    iqr_upperbound = series.quantile(.75) + iqr*1.5
    iqr_lowerbound = series.quantile(.25) - iqr*1.5
    for oneValue in series.values:
        if oneValue > iqr_upperbound or oneValue < iqr_lowerbound:
            outliers_count += 1
    return (outliers_count/series.size) * 100
print("Summary for quantitative attributes.")
# using aggregate function to get mean, median, standard deviation and range
num_summary = df_new.agg(
    {
        col : ["mean", "median", "std", "min","max",range_num, outliers, outliersPercentage] for col in numerical_attr
    }
)
num_summary

"""#### Columns with range greater than 1"""

num_standardization_cols = []
for col in num_summary.columns:
    if num_summary.loc['range_num',col] > 1:
        num_standardization_cols.append(col)

print("Numbers of columns with range greater than 1: ", len(num_standardization_cols))
num_standardization_cols

"""#### From summary of numerical attributes following are the obervations.
* Data has potential outlier based on IQR.
* 10 columns have range of 1 i.e. we can skip standardization for these attributes.
* Rest columns can be standardized.
"""

df_new.boxplot(column = numerical_attr[3:],figsize=(20,10))

"""#### Checking distribution of categorical features"""

for col in categorical_attr:
    df_new[col].value_counts().plot(kind ='bar',figsize = (10,5), 
                                        title= 'Distribution of categories in ' + col,
                                        xlabel = col,
                                        ylabel='Frequency count')
    plt.show()

"""#### It can be seen that categorical data is highly imbalanced.
* In `protocol_type`, `tcp` has the highest distribution, and rest other classes have very low ditribution.
* In `service`, `http` and `private` has the highest distribution, and rest other classes have very low ditribution.
* In `flag`, `S0` and `SF` has the highest distribution, and rest other classes have very low ditribution.
* In `result`, `normal.` and `neptune.` has the highest distribution, and rest other classes have very low ditribution.

#### Subcategories count in categorical data
"""

for col in categorical_attr:
    print("Subcategories in ", col, " : ", len(df_new[col].unique()))
    print("-"*40)

"""#### For the columns `service` and `flag` has high number of subcategorices. On preprocessing these categorical attributes by converting them to numerical value using one hot encoding will result in adding a column per subcategory. In this case it would result in adding `66 + 11 + 3  - 3 = 77` columns. This would add to the complexity of the model. We will use baseN encoding which will highly reduce the dimentionality as the value of N is increased."""

df_new.groupby(['protocol_type']).agg({'result': 'value_counts'})

"""### Feature selection

#### Checking correlation for the features
"""

plt.figure(figsize=(41,20))
cor = df_new.corr()
sns.heatmap(cor,annot=True, cmap=plt.cm.CMRmap_r)
plt.show()

"""#### As per the correlation matrix above we can eliminate pairs with high correlation and consider only one feature from the pair of highly correlated features. For this problem we are using threshold correlation of 0.8."""

def correlation(dataset, threshold):
    col_corr = set()
    corr_matrix = dataset.corr()
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if (corr_matrix.iloc[i,j]) > threshold:
                colname = corr_matrix.columns[i]
                col_corr.add(colname)
    return col_corr

"""#### Highly correlated feature from their pair"""

corr_features = correlation(df_new, 0.8)
print("Number of highly correlated pairs: ",len(set(corr_features)))
print("-"*40)
print("One feature from each highly correlated pair: \n", corr_features)

# df_new = df_new.drop(corr_features,axis = 1)

df_new.shape

"""#### Removing these features for model training"""

for col in numerical_attr:
    if col in corr_features:
        numerical_attr.remove(col)

for col in num_standardization_cols:
    if col in corr_features:
        num_standardization_cols.remove(col)

print("Numerical attributes after removing highly correlated featured: ", len(numerical_attr))

print("Numerical attributes for standardization after removing highly correlated featured: ", len(num_standardization_cols))

"""### Preprocessing the data

#### Creating pipeline for categorical data preprocessing
"""

!pip install category_encoders

from sklearn.pipeline import Pipeline
import category_encoders as ce

categorical_attr_encoding = categorical_attr
categorical_attr_encoding.remove('result')
categorical_transformer = Pipeline(
    steps=[("base_encoding",ce.BaseNEncoder(base=2))])

"""#### Creating pipeline for numerical data preprocessing"""

from sklearn.preprocessing import StandardScaler

numeric_transformer = Pipeline(
    steps=[("scaler", StandardScaler())]
)

"""#### Creating full pipeline with numerical and categorical preprocessing"""

from sklearn.compose import ColumnTransformer

full_pipeline = ColumnTransformer(transformers=[
        ("num", numeric_transformer, num_standardization_cols),
        ("cat", categorical_transformer, categorical_attr_encoding),
        ("passthrough", "passthrough", list(set(numerical_attr) - set(num_standardization_cols)))
    ])

"""#### Transforming the data"""

df_tf = full_pipeline.fit_transform(df_new)

"""#### Shape of the transformed data"""

print("Number of rows: ",df_tf.shape[0])
print("Number of columns: ",df_tf.shape[1])

"""#### Splitting the data into test and train"""



from sklearn.model_selection import StratifiedShuffleSplit

ss = StratifiedShuffleSplit(test_size=0.2,random_state=42,n_splits=1)

X_train, X_test, y_train, y_test = (None, None, None, None)
for train_index, test_index in ss.split(df_tf, df_new['result']):
    X_train, X_test = df_tf[train_index], df_tf[test_index]
    y_train, y_test = df_new['result'].iloc[train_index], df_new['result'].iloc[test_index]

"""####  Data distribution after stratified sampling"""

print("Percentage distribution in train split: ", (X_train.shape[0]/df_new.shape[0])*100)
print("-"*40)
print("Percentage distribution in test split: ", (X_test.shape[0]/df_new.shape[0])*100)
print("-"*40)
print("Percentage classes distribution on train split:\n",(y_train.value_counts()/df_new.shape[0])*100)
print("-"*40)
print("Percentage classes distribution on test split:\n",(y_test.value_counts()/df_new.shape[0])*100)

"""####Balancing the dataset"""

from imblearn.over_sampling import SMOTE, ADASYN,RandomOverSampler
from collections import Counter
from imblearn.pipeline import Pipeline

counter = Counter(y_train)
print("before: ",counter)
smote = SMOTE()
ros = RandomOverSampler()
pipe = Pipeline([('randomoversampler',ros),('smote',smote)])
# oversample = SMOTE(random_state = 1)
X_train,y_train = pipe.fit_resample(X_train,y_train)
counter = Counter(y_train)
print("after: ",counter)

"""####Standardizing the Data"""

# data standardization with  sklearn
from sklearn.preprocessing import StandardScaler

# copy of datasets
X_train_stand = X_train.copy()
X_test_stand = X_test.copy()



for i in range(X_train_stand.shape[1]):
    
    # fit on training data column
    scale = StandardScaler().fit(X_train_stand[[i]])
    
    # transform the training data column
    X_train_stand[i] = scale.transform(X_train_stand[[i]])
    
    # transform the testing data column
    X_test_stand[i] = scale.transform(X_test_stand[[i]])

"""#Train the model"""

from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.ensemble import AdaBoostClassifier

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

models = [MLPClassifier(alpha=0.005)]
classifiers = ["ABC"]
scores = []

for model in models:
  model.fit(X_train_stand,y_train)
  y_pred = model.predict(X_test_stand)
  score = accuracy_score(y_test, y_pred)*100
  scores.append(score)
  print("Accuracy of  model is: ", score)
  conf_matrix = confusion_matrix(y_test,y_pred)
  report = classification_report(y_test,y_pred)
  print("Confusion Matrix:\n",conf_matrix)
  print("Report:\n",report)
  print("\n==============***===============")