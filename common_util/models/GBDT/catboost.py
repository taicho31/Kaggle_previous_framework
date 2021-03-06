# https://catboost.ai/docs/concepts/python-reference_catboost_predict.html
# https://catboost.ai/docs/concepts/python-reference_catboostclassifier.html
from catboost import CatBoost
from catboost import Pool
def accuracy_class(train, test):
    X_train = train.drop(['accuracy_group'],axis=1) 
    y_train = train.accuracy_group.copy()

    X_test = test.drop(["installation_id","accuracy_group"], axis=1)
    n_folds=5
    skf=GroupKFold(n_splits = n_folds)
    cat_params = {
    'loss_function': 'Logloss',
    'depth': 4,
    "num_boost_round":100000,
    'learning_rate': 0.01,
    "early_stopping_rounds":100,
    }

    pred_value = np.zeros([X_test.shape[0]])
    valid = pd.DataFrame(np.zeros([X_train.shape[0]]))
    features_list = [i for i in X_train.columns if i != "installation_id"]
    feature_importance_df = pd.DataFrame(features_list, columns=["Feature"])
    for i , (train_index, test_index) in enumerate(skf.split(X_train, y_train, X_train["installation_id"])):
        print("Fold "+str(i+1))
        X_train2 = X_train.iloc[train_index,:]
        y_train2 = y_train.iloc[train_index]
        X_train2 = X_train2.drop(['installation_id'],axis=1)
    
        X_test2 = X_train.iloc[test_index,:]
        y_test2 = y_train.iloc[test_index]
        X_test2 = X_test2.drop(['installation_id'],axis=1)
            
        train_pool = Pool(X_train2, label=y_train2)
        test_pool = Pool(X_test2, label=y_test2)
        clf = CatBoost(cat_params)
        clf.fit(train_pool, eval_set=[train_pool, test_pool], use_best_model=True, verbose_eval = 300)
        test_predict = clf.predict(X_test2, prediction_type = "Probability")
        
        valid.iloc[test_index] = test_predict[:,1].reshape(X_test2.shape[0], 1)
        pred_value += model.predict(X_test, prediction_type = "Probability")[:,1] / n_folds
        feature_importance_df["Fold_"+str(i+1)] = clf.get_feature_importance()
    
    print("logloss = \t {}".format(log_loss(y_train, valid)))
    
    feature_importance_df["Average"] = np.mean(feature_importance_df.iloc[:,1:n_folds+1], axis=1)
    feature_importance_df["Std"] = np.std(feature_importance_df.iloc[:,1:n_folds+1], axis=1)
    feature_importance_df["Cv"] = feature_importance_df["Std"] / feature_importance_df["Average"]
    
    return pred_value, valid, feature_importance_df

pred_value, valid, feat_df  = accuracy_class(new_train, new_test)
