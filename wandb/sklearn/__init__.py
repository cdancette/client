from __future__ import absolute_import, division, print_function, unicode_literals
import wandb
import time
import itertools
import sklearn
import numpy as np
import scipy as sp
from wandb.sklearn.utils import *
from sklearn.base import clone
from joblib import Parallel, delayed
from sklearn import model_selection
from sklearn import datasets
from sklearn import metrics
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score
from sklearn.metrics import (brier_score_loss, precision_score, recall_score, f1_score)
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.preprocessing import label_binarize
from sklearn.preprocessing import LabelEncoder
from sklearn.calibration import calibration_curve
from sklearn.utils.multiclass import unique_labels, type_of_target
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.linear_model import LogisticRegression
from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)

def round_3(n):
    return round(n, 3)
def round_2(n):
    return round(n, 2)
chart_limit = 1000
def get_named_labels(labels, numeric_labels):
        return np.array([labels[num_label] for num_label in numeric_labels])

"""
Generates all sklearn classifier plots supported by W&B.
    The following plots are generated:
    feature importances, learning curve, confusion matrix, summary metrics,
    class balance plot, calibration curve, roc curve & precision recall curve.

Should only be called with a fitted classifer (otherwise an error in thrown).

Arguments:
    model (clf): Takes in a fitted classifier.
    X_train (arr): Training set features.
    y_train (arr): Training set labels.
    X_test (arr): Test set features.
    y_test (arr): Test set labels.
    y_pred (arr): Test set predictions by the model passed.
    y_probas (arr): Test set predicted probabilities by the model passed.
    labels (list): Named labels for target varible (y). Makes plots easier to
                    read by replacing target values with corresponding index.
                    For example labels= ['dog', 'cat', 'owl'] all 0s are
                    replaced by 'dog', 1s by 'cat'.
    is_binary (bool): Is the model passed a binary classifier? Defaults to False
    model_name (str): Model name. Defaults to 'Classifier'
    feature_names (list): Names for features. Makes plots easier to read by
                            replacing feature indexes with corresponding names.

Returns:
    Nothing. To see plots, go to your W&B run page then expand the 'media' tab
        under 'auto visualizations'.

Example:
    wandb.sklearn.plot_classifier(model, X_train, X_test, y_train, y_test,
                    y_pred, y_probas, ['cat', 'dog'], False,
                    'RandomForest', ['barks', 'drools, 'plays_fetch', 'breed'])
"""
def plot_classifier(model, X_train, X_test,
                    y_train, y_test, y_pred, y_probas,
                    labels, is_binary=False, model_name='Classifier',
                    feature_names=None):
    wandb.termlog('\nPlotting %s.'%model_name)
    plot_feature_importances(model, feature_names)
    wandb.termlog('Logged feature importances.')
    plot_learning_curve(model, X_train, y_train)
    wandb.termlog('Logged learning curve.')
    plot_confusion_matrix(y_test, y_pred, labels)
    wandb.termlog('Logged confusion matrix.')
    plot_summary_metrics(model, X=X_train, y=y_train, X_test=X_test, y_test=y_test)
    wandb.termlog('Logged summary metrics.')
    plot_class_balance(y_train, y_test, labels)
    wandb.termlog('Logged class balances.')
    plot_calibration_curve(model, X_train, y_train, model_name)
    wandb.termlog('Logged calibration curve.')
    plot_roc(y_test, y_probas, labels)
    wandb.termlog('Logged roc curve.')
    plot_precision_recall(y_test, y_probas, labels)
    wandb.termlog('Logged precision recall curve.')
    # if is_binary:
        # plot_decision_boundaries(model, X_train, y_train)
        # wandb.termlog('Logged decision boundary plot.')

"""
Generates all sklearn regressor plots supported by W&B.
    The following plots are generated:
    learning curve, summary metrics, residuals plot, outlier candidates.

Should only be called with a fitted regressor (otherwise an error in thrown).

Arguments:
    model (clf): Takes in a fitted classifier.
    X_train (arr): Training set features.
    y_train (arr): Training set labels.
    X_test (arr): Test set features.
    y_test (arr): Test set labels.
    model_name (str): Model name. Defaults to 'Regressor'

Returns:
    Nothing. To see plots, go to your W&B run page then expand the 'media' tab
        under 'auto visualizations'.

Example:
    wandb.sklearn.plot_regressor(reg, X_train, X_test, y_train, y_test, 'Ridge')
"""
def plot_regressor(model, X_train, X_test, y_train, y_test,  model_name='Regressor'):
    wandb.termlog('\nPlotting %s.'%model_name)
    plot_summary_metrics(model, X_train, y_train, X_test, y_test)
    wandb.termlog('Logged summary metrics.')
    plot_learning_curve(model, X_train, y_train)
    wandb.termlog('Logged learning curve.')
    plot_outlier_candidates(model, X_train, y_train)
    wandb.termlog('Logged outlier candidates.')
    plot_residuals(model, X_train, y_train)
    wandb.termlog('Logged residuals.')

"""
Generates all sklearn clusterer plots supported by W&B.
    The following plots are generated:
    elbow curve, silhouette plot.

Should only be called with a fitted clusterer (otherwise an error in thrown).

Arguments:
    model (clf): Takes in a fitted classifier.
    X_train (arr): Training set features.
    cluster_labels (list): Names for cluster labels. Makes plots easier to read
                        by replacing cluster indexes with corresponding names.
    labels (list): Named labels for target varible (y). Makes plots easier to
                    read by replacing target values with corresponding index.
                    For example labels= ['dog', 'cat', 'owl'] all 0s are
                    replaced by 'dog', 1s by 'cat'.
    model_name (str): Model name. Defaults to 'Clusterer'

Returns:
    Nothing. To see plots, go to your W&B run page then expand the 'media' tab
          under 'auto visualizations'.

Example:
    wandb.sklearn.plot_clusterer(kmeans, X, cluster_labels, labels, 'KMeans')
"""
def plot_clusterer(model, X_train, cluster_labels, labels=None, model_name='Clusterer'):
    wandb.termlog('\nPlotting %s.'%model_name)
    if isinstance(model, sklearn.cluster.KMeans):
        plot_elbow_curve(model, X_train)
        wandb.termlog('Logged elbow curve.')
        plot_silhouette(model, X_train, cluster_labels, labels=labels, kmeans=True)
    else:
        plot_silhouette(model, X_train, cluster_labels, kmeans=False)
    wandb.termlog('Logged silhouette plot.')

"""
Calculates summary metrics (like mse, mae, r2 score) for both regression and
classification algorithms.

Called by plot_summary_metrics to visualize metrics. Please use the function
plot_summary_metric() if you wish to visualize your summary metrics.
"""
def summary_metrics(model=None, X=None, y=None, X_test=None, y_test=None):
    if (test_missing(model=model, X=X, y=y, X_test=X_test, y_test=y_test) and
        test_types(model=model, X=X, y=y, X_test=X_test, y_test=y_test) and
        test_fitted(model)):
        metric_name=[]
        metric_value=[]
        model_name = model.__class__.__name__

        params = {}
        # Log model params to wandb.config
        for v in vars(model):
            if isinstance(getattr(model, v), str) \
                or isinstance(getattr(model, v), bool) \
                    or isinstance(getattr(model, v), int) \
                    or isinstance(getattr(model, v), float):
                params[v] = getattr(model, v)

        # Classifier Metrics
        if sklearn.base.is_classifier(model):
            y_pred = model.predict(X_test)
            y_probas = model.predict_proba(X_test)

            metric_name.append("accuracy_score")
            metric_value.append(round_2(sklearn.metrics.accuracy_score(y_test, y_pred)))
            metric_name.append("precision")
            metric_value.append(round_2(sklearn.metrics.precision_score(y_test, y_pred, average="weighted")))
            metric_name.append("recall")
            metric_value.append(round_2(sklearn.metrics.recall_score(y_test, y_pred, average="weighted")))
            metric_name.append("f1_score")
            metric_value.append(round_2(sklearn.metrics.f1_score(y_test, y_pred, average="weighted")))

        # Regression Metrics
        elif sklearn.base.is_regressor(model):
            y_pred = model.predict(X_test)

            metric_name.append("mae")
            metric_value.append(round_2(sklearn.metrics.mean_absolute_error(y_test, y_pred)))
            metric_name.append("mse")
            metric_value.append(round_2(sklearn.metrics.mean_squared_error(y_test, y_pred)))
            metric_name.append("r2_score")
            metric_value.append(round_2(sklearn.metrics.r2_score(y_test, y_pred)))

        return wandb.visualize(
            'wandb/metrics/v1', wandb.Table(
            columns=['metric_name', 'metric_value', 'model_name'],
            data= [
                [metric_name[i], metric_value[i], model_name] for i in range(len(metric_name))
            ]
        ))

"""
Logs the charts generated by summary_metrics in wandb.

Should only be called with a fitted model (otherwise an error in thrown).

Arguments:
    model (clf): Takes in a fitted regressor or classifier.
    X (arr): Training set features.
    y (arr): Training set labels.
    X_test (arr): Test set features.
    y_test (arr): Test set labels.

Returns:
    Nothing. To see plots, go to your W&B run page then expand the 'media' tab
          under 'auto visualizations'.

Example:
    wandb.sklearn.plot_summary_metrics(model, X_train, X_test, y_train, y_test)
"""
def plot_summary_metrics(model=None, X=None, y=None, X_test=None, y_test=None):
    wandb.log({'summary_metrics': summary_metrics(model, X, y, X_test, y_test)})


"""
Trains model on datasets of varying lengths and generates a plot of
scores vs training sizes for both training and test sets.

Called by plot_learning_curve to visualize learning curve. Please use the function
plot_learning_curve() if you wish to visualize your learning curves.

"""
def learning_curve(model, X, y, cv=None,
                    shuffle=False, random_state=None,
                    train_sizes=None, n_jobs=1, scoring=None):
    if train_sizes is None:
        train_sizes = np.linspace(.1, 1.0, 5)
    if (test_missing(model=model, X=X, y=y) and
        test_types(model=model, X=X, y=y)):
        train_sizes, train_scores, test_scores = model_selection.learning_curve(
            model, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes,
            scoring=scoring, shuffle=shuffle, random_state=random_state)
        train_scores_mean = np.mean(train_scores, axis=1)
        train_scores_std = np.std(train_scores, axis=1)
        test_scores_mean = np.mean(test_scores, axis=1)
        test_scores_std = np.std(test_scores, axis=1)

        def learning_curve_table(train, test, trainsize):
            data=[]
            for i in range(len(train)):
                if i >= chart_limit/2:
                    break
                train_set = ["train", round(train[i],2), trainsize[i]]
                test_set = ["test", round(test[i],2), trainsize[i]]
                data.append(train_set)
                data.append(test_set)
            return wandb.visualize(
                'wandb/learning_curve/v1', wandb.Table(
                columns=['dataset', 'score', 'train_size'],
                data=data
            ))

        return learning_curve_table(train_scores_mean, test_scores_mean, train_sizes)

"""
Logs the plots generated by learning_curve() to wandb.
Please note this function fits the model to datasets of varying sizes.

Arguments:
    model (model): Takes in a fitted regressor or classifier.
    X (arr): Dataset features.
    y (arr): Dataset labels.

Returns:
    Nothing. To see plots, go to your W&B run page then expand the 'media' tab
          under 'auto visualizations'.

Example:
    wandb.sklearn.plot_learning_curve(model, X, y)
"""
def plot_learning_curve(model=None, X=None, y=None, cv=None,
                        shuffle=False, random_state=None,
                        train_sizes=None, n_jobs=1, scoring=None):
  wandb.log({'learning_curve': learning_curve(model, X, y, cv, shuffle,
      random_state, train_sizes, n_jobs, scoring)})


"""
Calculates receiver operating characteristic scores and visualizes them as the
    ROC curve.

Called by plot_roc to visualize roc curves. Please use the function plot_roc()
if you wish to visualize your roc curves.
"""
def roc(y_true=None, y_probas=None, labels=None,
        plot_micro=True, plot_macro=True, classes_to_plot=None):
        if (test_missing(y_true=y_true, y_probas=y_probas) and
            test_types(y_true=y_true, y_probas=y_probas)):
            y_true = np.array(y_true)
            y_probas = np.array(y_probas)
            classes = np.unique(y_true)
            probas = y_probas

            if classes_to_plot is None:
                classes_to_plot = classes

            fpr_dict = dict()
            tpr_dict = dict()

            indices_to_plot = np.in1d(classes, classes_to_plot)
            def roc_table(fpr_dict, tpr_dict, classes, indices_to_plot):
                data=[]
                count = 0

                for i, to_plot in enumerate(indices_to_plot):
                    fpr_dict[i], tpr_dict[i], _ = roc_curve(y_true, probas[:, i],
                                                            pos_label=classes[i])
                    if to_plot:
                        roc_auc = auc(fpr_dict[i], tpr_dict[i])
                        for j in range(len(fpr_dict[i])):
                            if labels is not None and (isinstance(classes[i], int)
                                        or isinstance(classes[0], np.integer)):
                                class_dict = labels[classes[i]]
                            else:
                                class_dict = classes[i]
                            fpr = [class_dict, fpr_dict[i][j], tpr_dict[i][j]]
                            data.append(fpr)
                            count+=1
                            if count >= chart_limit:
                                break
                return wandb.visualize(
                    'wandb/roc/v1', wandb.Table(
                    columns=['class', 'fpr', 'tpr'],
                    data=data
                ))
            return roc_table(fpr_dict, tpr_dict, classes, indices_to_plot)

"""
Logs the plots generated by roc() to wandb.

Arguments:
    y_true (arr): Test set labels.
    y_probas (arr): Test set predicted probabilities.
    labels (list): Named labels for target varible (y). Makes plots easier to
                    read by replacing target values with corresponding index.
                    For example labels= ['dog', 'cat', 'owl'] all 0s are
                    replaced by 'dog', 1s by 'cat'.

Returns:
    Nothing. To see plots, go to your W&B run page then expand the 'media' tab
          under 'auto visualizations'.

Example:
    wandb.sklearn.plot_roc(y_true, y_probas, labels)
"""
def plot_roc(y_true=None, y_probas=None, labels=None,
             plot_micro=True, plot_macro=True, classes_to_plot=None):
  wandb.log({'roc': roc(y_true, y_probas, labels, plot_micro, plot_macro, classes_to_plot)})


"""
Computes the confusion matrix to evaluate the accuracy of a classification.

Called by plot_confusion_matrix to visualize roc curves. Please use the function
plot_confusion_matrix() if you wish to visualize your confusion matrix.
"""
def confusion_matrix(y_true=None, y_pred=None, labels=None, true_labels=None,
                          pred_labels=None, title=None, normalize=False,
                          hide_zeros=False, hide_counts=False):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if (test_missing(y_true=y_true, y_pred=y_pred) and
        test_types(y_true=y_true, y_pred=y_pred)):
        cm = metrics.confusion_matrix(y_true, y_pred)
        if labels is None:
            classes = unique_labels(y_true, y_pred)
        else:
            classes = np.asarray(labels)

        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            cm = np.around(cm, decimals=2)
            cm[np.isnan(cm)] = 0.0

        if true_labels is None:
            true_classes = classes
        else:
            validate_labels(classes, true_labels, "true_labels")

            true_label_indexes = np.in1d(classes, true_labels)

            true_classes = classes[true_label_indexes]
            cm = cm[true_label_indexes]

        if pred_labels is None:
            pred_classes = classes
        else:
            validate_labels(classes, pred_labels, "pred_labels")

            pred_label_indexes = np.in1d(classes, pred_labels)

            pred_classes = classes[pred_label_indexes]
            cm = cm[:, pred_label_indexes]

        def confusion_matrix_table(cm, pred_classes, true_classes):
            data=[]
            count = 0
            for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
                if labels is not None and (isinstance(pred_classes[i], int)
                                    or isinstance(pred_classes[0], np.integer)):
                    pred_dict = labels[pred_classes[i]]
                    true_dict = labels[true_classes[i]]
                else:
                    pred_dict = pred_classes[i]
                    true_dict = true_classes[j]
                data.append([pred_dict, true_dict, cm[i,j]])
                count+=1
                if count >= chart_limit:
                    break
            return wandb.visualize(
                'wandb/confusion_matrix/v1', wandb.Table(
                columns=['Predicted', 'Actual', 'Count'],
                data=data
            ))

        return confusion_matrix_table(cm, pred_classes, true_classes)

"""
Logs the plots generated by confusion_matrix() to wandb.

Arguments:
    y_true (arr): Test set labels.
    y_probas (arr): Test set predicted probabilities.
    labels (list): Named labels for target varible (y). Makes plots easier to
                    read by replacing target values with corresponding index.
                    For example labels= ['dog', 'cat', 'owl'] all 0s are
                    replaced by 'dog', 1s by 'cat'.

Returns:
    Nothing. To see plots, go to your W&B run page then expand the 'media' tab
          under 'auto visualizations'.

Example:
    wandb.sklearn.plot_confusion_matrix(y_true, y_probas, labels)
"""
def plot_confusion_matrix(y_true=None, y_pred=None, labels=None, true_labels=None,
                          pred_labels=None, title=None, normalize=False,
                          hide_zeros=False, hide_counts=False):
    wandb.log({'confusion_matrix': confusion_matrix(y_true, y_pred, labels, true_labels,
                          pred_labels, title, normalize,
                          hide_zeros, hide_counts)})

"""
Computes the tradeoff between precision and recall for different thresholds.
    A high area under the curve represents both high recall and high precision,
    where high precision relates to a low false positive rate, and high recall
    relates to a low false negative rate. High scores for both show that the
    classifier is returning accurate results (high precision), as well as
    returning a majority of all positive results (high recall).
    PR curve is useful when the classes are very imbalanced.

Called by plot_precision_recall to visualize PR curves. Please use the function
plot_precision_recall() if you wish to visualize your PR curves.
"""
def precision_recall(y_true=None, y_probas=None, labels=None,
                          plot_micro=True, classes_to_plot=None):
    y_true = np.array(y_true)
    y_probas = np.array(y_probas)

    if (test_missing(y_true=y_true, y_probas=y_probas) and
        test_types(y_true=y_true, y_probas=y_probas)):
        classes = np.unique(y_true)
        probas = y_probas

        if classes_to_plot is None:
            classes_to_plot = classes

        binarized_y_true = label_binarize(y_true, classes=classes)
        if len(classes) == 2:
            binarized_y_true = np.hstack(
                (1 - binarized_y_true, binarized_y_true))

        pr_curves = {}
        indices_to_plot = np.in1d(classes, classes_to_plot)
        for i, to_plot in enumerate(indices_to_plot):
            if to_plot:
                average_precision = average_precision_score(
                    binarized_y_true[:, i],
                    probas[:, i])
                precision, recall, _ = precision_recall_curve(
                    y_true, probas[:, i], pos_label=classes[i])

                samples = 20
                sample_precision = []
                sample_recall = []
                for k in range(samples):
                    sample_precision.append(precision[int(len(precision)*k/samples)])
                    sample_recall.append(recall[int(len(recall)*k/samples)])


                pr_curves[classes[i]] = (sample_precision, sample_recall)
        # if plot_micro:
        #     precision, recall, _ = precision_recall_curve(
        #         binarized_y_true.ravel(), probas.ravel())
        #     average_precision = average_precision_score(binarized_y_true,
        #                                                 probas,
        #                                                 average='micro')
        #     ax.plot(recall, precision,
        #             label='micro-average Precision-recall curve '
        #                   '(area = {0:0.3f})'.format(average_precision),
        #             color='navy', linestyle=':', linewidth=4)
        def pr_table(pr_curves):
            data=[]
            count=0
            for i, class_name in enumerate(pr_curves.keys()):
                precision, recall = pr_curves[class_name]
                for p, r in zip(precision, recall):
                    # if class_names are ints and labels are set
                    if labels is not None and (isinstance(class_name, int)
                                    or isinstance(class_name, np.integer)):
                        class_name = labels[class_name]
                    # if class_names are ints and labels are not set
                    # or, if class_names have something other than ints
                    # (string, float, date) - user class_names
                    data.append([class_name, p, r])
                    count+=1
                    if count >= chart_limit:
                        break
            return wandb.visualize(
                'wandb/pr_curve/v1', wandb.Table(
                columns=['class', 'precision', 'recall'],
                data=data
            ))
        return pr_table(pr_curves)

"""
Logs the plots generated by precision_recall() to wandb.

Arguments:
    y_true (arr): Test set labels.
    y_probas (arr): Test set predicted probabilities.
    labels (list): Named labels for target varible (y). Makes plots easier to
                    read by replacing target values with corresponding index.
                    For example labels= ['dog', 'cat', 'owl'] all 0s are
                    replaced by 'dog', 1s by 'cat'.

Returns:
    Nothing. To see plots, go to your W&B run page then expand the 'media' tab
          under 'auto visualizations'.

Example:
    wandb.sklearn.plot_precision_recall(y_true, y_probas, labels)
"""
def plot_precision_recall(y_true=None, y_probas=None, labels=None,
                          plot_micro=True, classes_to_plot=None):
  wandb.log({'precision_recall':precision_recall(y_true, y_probas,
                          labels, plot_micro, classes_to_plot)})

"""
Evaluates & plots the importance of each feature for the classification task.

Should only be called with a fitted classifer (otherwise an error in thrown).

Arguments:
    model (clf): Takes in a fitted classifier.
    X_train (arr): Training set features.
    y_train (arr): Training set labels.
    X_test (arr): Test set features.
    y_test (arr): Test set labels.
    y_pred (arr): Test set predictions by the model passed.
    y_probas (arr): Test set predicted probabilities by the model passed.
    labels (list): Named labels for target varible (y). Makes plots easier to
                    read by replacing target values with corresponding index.
                    For example labels= ['dog', 'cat', 'owl'] all 0s are
                    replaced by 'dog', 1s by 'cat'.
    is_binary (bool): Is the model passed a binary classifier? Defaults to False
    model_name (str): Model name. Defaults to 'Classifier'
    feature_names (list): Names for features. Makes plots easier to read by
                            replacing feature indexes with corresponding names.

Returns:
    Nothing. To see plots, go to your W&B run page then expand the 'media' tab
          under 'auto visualizations'.

Example:
    wandb.sklearn.plot_classifier(model, X_train, X_test, y_train, y_test,
                    y_pred, y_probas, ['cat', 'dog'], False,
                    'RandomForest', ['barks', 'drools, 'plays_fetch', 'breed'])
"""
def plot_feature_importances(model=None, feature_names=None,
                            title='Feature Importance', max_num_features=50):
    if not hasattr(model, 'feature_importances_'):
        wandb.termwarn("feature_importances_ attribute not in classifier. Cannot plot feature importances.")
        return
    if (test_missing(model=model) and test_types(model=model) and
        test_fitted(model)):
        importances = model.feature_importances_

        indices = np.argsort(importances)[::-1]

        if feature_names is None:
            feature_names = indices
        else:
            feature_names = np.array(feature_names)[indices]

        max_num_features = min(max_num_features, len(importances))

        # Draw a stem plot with the influence for each instance
        # format:
        # x = feature_names[:max_num_features]
        # y = importances[indices][:max_num_features]
        def feature_importances_table(feature_names, importances):
            return wandb.visualize(
                'wandb/feature_importances/v1', wandb.Table(
                columns=['feature_names', 'importances'],
                data=[
                    [feature_names[i], importances[i]] for i in range(len(feature_names))
                ]
            ))
        wandb.log({'feature_importances': feature_importances_table(feature_names, importances)})
        return

def plot_elbow_curve(clusterer=None, X=None, cluster_ranges=None, n_jobs=1,
                    show_cluster_time=True):
    if not hasattr(clusterer, 'n_clusters'):
        wandb.termlog('n_clusters attribute not in classifier. Cannot plot elbow method.')
        return
    if (test_missing(clusterer=clusterer) and test_types(clusterer=clusterer) and
        test_fitted(clusterer)):
        if cluster_ranges is None:
            cluster_ranges = range(1, 10, 2)
        else:
            cluster_ranges = sorted(cluster_ranges)

        if not hasattr(clusterer, 'n_clusters'):
            raise TypeError('"n_clusters" attribute not in classifier. '
                            'Cannot plot elbow method.')

        def _clone_and_score_clusterer(clusterer, X, n_clusters):
            start = time.time()
            clusterer = clone(clusterer)
            setattr(clusterer, 'n_clusters', n_clusters)
            return clusterer.fit(X).score(X), time.time() - start

        tuples = Parallel(n_jobs=n_jobs)(delayed(_clone_and_score_clusterer)
                                         (clusterer, X, i) for i in cluster_ranges)
        clfs, times = zip(*tuples)

        clfs = np.absolute(clfs)

        # Elbow curve
        # ax.plot(cluster_ranges, np.absolute(clfs), 'b*-')

        # Cluster time
        # ax2.plot(cluster_ranges, times, ':', alpha=0.75, color=ax2_color)

        # format:
        # cluster_ranges - x axis
        # errors = clfs - y axis
        # clustering_time = times - y axis2

        def elbow_curve(cluster_ranges, clfs, times):
            return wandb.visualize(
                'wandb/elbow/v1',
                wandb.Table(
                        columns=['cluster_ranges', 'errors', 'clustering_time'],
                        data=[
                            [cluster_ranges[i], clfs[i], times[i]] for i in range(len(cluster_ranges))
                        ]
            ))
        wandb.log({'elbow_curve': elbow_curve(cluster_ranges, clfs, times)})
        return

def plot_silhouette(clusterer=None, X=None, cluster_labels=None, labels=None,
                    metric='euclidean', kmeans=True):
    if (test_missing(clusterer=clusterer) and test_types(clusterer=clusterer) and
        test_fitted(clusterer)):
        if isinstance(X, (pd.DataFrame)):
            X = X.values
        # Run clusterer for n_clusters in range(len(cluster_ranges), get cluster labels
        # TODO - keep/delete once we decide if we should train clusterers
        # or ask for trained models
        # clusterer.set_params(n_clusters=n_clusters, random_state=42)
        # cluster_labels = clusterer.fit_predict(X)
        cluster_labels = np.asarray(cluster_labels)
        labels = np.asarray(labels)

        le = LabelEncoder()
        cluster_labels_encoded = le.fit_transform(cluster_labels)
        n_clusters = len(np.unique(cluster_labels))

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed
        # clusters
        silhouette_avg = silhouette_score(X, cluster_labels, metric=metric)

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(X, cluster_labels,
                                                      metric=metric)

        # Plot 1: Silhouette Score
        # y = np.arange(y_lower, y_upper)[]
        # x1 = 0
        # x2 = ith_cluster_silhouette_values[]
        # color = le.classes_[n_clusters]
        # rule_line = silhouette_avg

        y_sil = []
        x_sil = []
        color_sil = []

        y_lower = 10
        count = 0
        for i in range(n_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = \
                sample_silhouette_values[cluster_labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            y_values = np.arange(y_lower, y_upper)

            for j in range(len(y_values)):
                y_sil.append(y_values[j])
                x_sil.append(ith_cluster_silhouette_values[j])
                color_sil.append(i)
                count+=1
                if count >= chart_limit:
                    break

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        # Plot 2: Scatter Plot showing the actual clusters formed
        if kmeans:
            centers = clusterer.cluster_centers_
            def silhouette(x, y, colors, centerx, centery, y_sil, x_sil, color_sil, silhouette_avg):
                return wandb.visualize(
                    'wandb/silhouette_/v1', wandb.Table(
                    columns=['x', 'y', 'colors', 'centerx', 'centery', 'y_sil', 'x1', 'x2', 'color_sil', 'silhouette_avg'],
                    data=[
                        [x[i], y[i], colors[i], centerx[colors[i]], centery[colors[i]],
                        y_sil[i], 0, x_sil[i], color_sil[i], silhouette_avg]
                        for i in range(len(color_sil))
                    ]
                ))
            wandb_key = 'silhouette_plot'
            wandb.log({wandb_key: silhouette(X[:, 0], X[:, 1], cluster_labels, centers[:, 0], centers[:, 1], y_sil, x_sil, color_sil, silhouette_avg)})
        else:
            centerx = [None] * len(color_sil)
            centery = [None] * len(color_sil)
            def silhouette(x, y, colors, centerx, centery, y_sil, x_sil, color_sil, silhouette_avg):
                return wandb.visualize(
                    'wandb/silhouette_/v1', wandb.Table(
                    columns=['x', 'y', 'colors', 'centerx', 'centery', 'y_sil', 'x1', 'x2', 'color_sil', 'silhouette_avg'],
                    data=[
                        [x[i], y[i], colors[i], None, None,
                        y_sil[i], 0, x_sil[i], color_sil[i], silhouette_avg]
                        for i in range(len(color_sil))
                    ]
                ))
            wandb_key = 'silhouette_plot'
            wandb.log({wandb_key: silhouette(X[:, 0], X[:, 1], cluster_labels, centerx, centery, y_sil, x_sil, color_sil, silhouette_avg)})
        return

def plot_class_balance(y_train=None, y_test=None, labels=None):
    if (test_missing(y_train=y_train, y_test=y_test) and
        test_types(y_train=y_train, y_test=y_test)):
        # Get the unique values from the dataset
        y_train = np.array(y_train)
        y_test = np.array(y_test)
        targets = (y_train,) if y_test is None else (y_train, y_test)
        classes_ = np.array(unique_labels(*targets))

        # Compute the class counts
        class_counts_train = np.array([(y_train == c).sum() for c in classes_])
        class_counts_test = np.array([(y_test == c).sum() for c in classes_])

        def class_balance(classes_, class_counts_train, class_counts_test):
            class_dict = []
            dataset_dict = []
            count_dict = []
            for i in range(len(classes_)):
                # add class counts from training set
                class_dict.append(classes_[i])
                dataset_dict.append("train")
                count_dict.append(class_counts_train[i])
                # add class counts from test set
                class_dict.append(classes_[i])
                dataset_dict.append("test")
                count_dict.append(class_counts_test[i])
                if i >= chart_limit:
                    break

            if labels is not None and (isinstance(class_dict[0], int)
                                or isinstance(class_dict[0], np.integer)):
                class_dict = get_named_labels(labels, class_dict)
            return wandb.visualize(
                'wandb/class_balance/v1', wandb.Table(
                columns=['class', 'dataset', 'count'],
                data=[
                    [class_dict[i], dataset_dict[i], count_dict[i]] for i in range(len(class_dict))
                ]
            ))
        wandb.log({'class_balance': class_balance(classes_, class_counts_train, class_counts_test)})

def plot_calibration_curve(clf=None, X=None, y=None, clf_name='Classifier'):
    """Plot calibration curve for clf w/o and with calibration. """
    if (test_missing(clf=clf, X=X, y=y) and
        test_types(clf=clf, X=X, y=y) and
        test_fitted(clf)):
        # Create dataset of classification task with many redundant and few
        # informative features
        X, y = datasets.make_classification(n_samples=100000, n_features=20,
                                            n_informative=2, n_redundant=10,
                                            random_state=42)

        X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.99,
                                                            random_state=42)
        # Calibrated with isotonic calibration
        isotonic = CalibratedClassifierCV(clf, cv=2, method='isotonic')

        # Calibrated with sigmoid calibration
        sigmoid = CalibratedClassifierCV(clf, cv=2, method='sigmoid')

        # Logistic regression with no calibration as baseline
        lr = LogisticRegression(C=1.)

        model_dict = [] # color
        frac_positives_dict = [] # y axis
        mean_pred_value_dict = [] # x axis
        hist_dict = [] # barchart y
        edge_dict = [] # barchart x

        # Add curve for perfectly calibrated model
        # format: model, fraction_of_positives, mean_predicted_value
        model_dict.append('Perfectly calibrated')
        frac_positives_dict.append(0)
        mean_pred_value_dict.append(0)
        hist_dict.append(0)
        edge_dict.append(0)
        model_dict.append('Perfectly calibrated')
        hist_dict.append(0)
        edge_dict.append(0)
        frac_positives_dict.append(1)
        mean_pred_value_dict.append(1)

        X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.98,
                                                            random_state=42)

        # Add curve for LogisticRegression baseline and other models
        for clf, name in [(lr, 'Logistic'),
                          (clf, clf_name),
                          (isotonic, clf_name + ' + Isotonic'),
                          (sigmoid, clf_name + ' + Sigmoid')]:
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            if hasattr(clf, "predict_proba"):
                prob_pos = clf.predict_proba(X_test)[:, 1]
            else:  # use decision function
                prob_pos = clf.decision_function(X_test)
                prob_pos = \
                    (prob_pos - prob_pos.min()) / (prob_pos.max() - prob_pos.min())

            clf_score = brier_score_loss(y_test, prob_pos, pos_label=y.max())

            fraction_of_positives, mean_predicted_value = \
                calibration_curve(y_test, prob_pos, n_bins=10)
            hist, edges = np.histogram(
                            prob_pos,
                            bins=10,
                            density=False)

            # format: model, fraction_of_positives, mean_predicted_value
            for i in range(len(fraction_of_positives)):
                hist_dict.append(hist[i])
                edge_dict.append(edges[i])
                model_dict.append(name)
                frac_positives_dict.append(round_3(fraction_of_positives[i]))
                mean_pred_value_dict.append(round_3(mean_predicted_value[i]))
                if i >= (chart_limit-2):
                    break

            def calibration_curves(model_dict, frac_positives_dict, mean_pred_value_dict, hist_dict, edge_dict):
                return wandb.visualize(
                    'wandb/calibration/v1', wandb.Table(
                    columns=['model', 'fraction_of_positives', 'mean_predicted_value', 'hist_dict', 'edge_dict'],
                    data=[
                        [model_dict[i], frac_positives_dict[i], mean_pred_value_dict[i], hist_dict[i], edge_dict[i]] for i in range(len(model_dict))
                    ]
                ))
        wandb.log({'calibration_curve': calibration_curves(model_dict, frac_positives_dict, mean_pred_value_dict, hist_dict, edge_dict)})

def plot_outlier_candidates(regressor=None, X=None, y=None):
    if (test_missing(regressor=regressor, X=X, y=y) and
        test_types(regressor=regressor, X=X, y=y) and
        test_fitted(regressor)):
        # Fit a linear model to X and y to compute MSE
        regressor.fit(X, y)

        # Leverage is computed as the diagonal of the projection matrix of X
        leverage = (X * np.linalg.pinv(X).T).sum(1)

        # Compute the rank and the degrees of freedom of the OLS model
        rank = np.linalg.matrix_rank(X)
        df = X.shape[0] - rank

        # Compute the MSE from the residuals
        residuals = y - regressor.predict(X)
        mse = np.dot(residuals, residuals) / df

        # Compute Cook's distance
        residuals_studentized = residuals / np.sqrt(mse) / np.sqrt(1 - leverage)
        distance_ = residuals_studentized ** 2 / X.shape[1]
        distance_ *= leverage / (1 - leverage)

        # Compute the p-values of Cook's Distance
        p_values_ = sp.stats.f.sf(distance_, X.shape[1], df)

        # Compute the influence threshold rule of thumb
        influence_threshold_ = 4 / X.shape[0]
        outlier_percentage_ = (
            sum(distance_ >= influence_threshold_) / X.shape[0]
        )
        outlier_percentage_ *= 100.0

        distance_dict = []
        count = 0
        for d in distance_:
            distance_dict.append(d)
            count+=1
            if count >= chart_limit:
                break

        # Draw a stem plot with the influence for each instance
        # format: distance_, len(distance_), influence_threshold_, round_3(outlier_percentage_)
        def outlier_candidates(distance, outlier_percentage, influence_threshold):
            return wandb.visualize(
                'wandb/outliers/v1', wandb.Table(
                columns=['distance', 'instance_indicies', 'outlier_percentage', 'influence_threshold'],
                data=[
                    [distance[i], i, round_3(outlier_percentage_), influence_threshold_] for i in range(len(distance))
                ]
            ))
        wandb.log({'outlier_candidates': outlier_candidates(distance_dict, outlier_percentage_, influence_threshold_)})
        return

def plot_residuals(regressor=None, X=None, y=None):
    if (test_missing(regressor=regressor, X=X, y=y) and
        test_types(regressor=regressor, X=X, y=y) and
        test_fitted(regressor)):
        # Create the train and test splits
        X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2)

        # Store labels and colors for the legend ordered by call
        _labels, _colors = [], []
        regressor.fit(X_train, y_train)
        train_score_ = regressor.score(X_train, y_train)
        test_score_ = regressor.score(X_test, y_test)

        y_pred_train = regressor.predict(X_train)
        residuals_train = y_pred_train - y_train

        y_pred_test = regressor.predict(X_test)
        residuals_test = y_pred_test - y_test

        # format:
        # Legend: train_score_, test_score_ (play with opacity)
        # Scatterplot: dataset(train, test)(color), y_pred(x), residuals(y)
        # Histogram: dataset(train, test)(color), residuals(y), aggregate(residuals(x)) with bins=50
        def residuals(y_pred_train, residuals_train, y_pred_test, residuals_test, train_score_, test_score_):
            y_pred_dict = []
            dataset_dict = []
            residuals_dict = []
            datapoints = 0
            max_datapoints_train = 900
            max_datapoints_train = 100
            for pred, residual in zip(y_pred_train, residuals_train):
                # add class counts from training set
                y_pred_dict.append(pred)
                dataset_dict.append("train")
                residuals_dict.append(residual)
                datapoints += 1
                if(datapoints >= max_datapoints_train):
                    break
            datapoints = 0
            for pred, residual in zip(y_pred_test, residuals_test):
                # add class counts from training set
                y_pred_dict.append(pred)
                dataset_dict.append("test")
                residuals_dict.append(residual)
                datapoints += 1
                if(datapoints >= max_datapoints_train):
                    break

            return wandb.visualize(
                'wandb/residuals_plot/v1', wandb.Table(
                columns=['dataset', 'y_pred', 'residuals', 'train_score', 'test_score'],
                data=[
                    [dataset_dict[i], y_pred_dict[i], residuals_dict[i], train_score_, test_score_] for i in range(len(y_pred_dict))
                ]
            ))
        wandb.log({'residuals': residuals(y_pred_train, residuals_train, y_pred_test, residuals_test, train_score_, test_score_)})

def plot_decision_boundaries(binary_clf=None, X=None, y=None):
    if (test_missing(binary_clf=binary_clf, X=X, y=y) and
        test_types(binary_clf=binary_clf, X=X, y=y)):
        # plot high-dimensional decision boundary
        print("Shapes", X.shape, y.shape)
        db = DBPlot(binary_clf)
        db.fit(X, y)
        decision_boundary_x, decision_boundary_y, decision_boundary_color, train_x, train_y, train_color, test_x, test_y, test_color = db.plot()
        def decision_boundaries(decision_boundary_x, decision_boundary_y,
                                decision_boundary_color, train_x, train_y,
                                train_color, test_x, test_y, test_color):
            x_dict = []
            y_dict = []
            color_dict = []
            shape_dict = []
            for i in range(min(len(decision_boundary_x),100)):
                x_dict.append(decision_boundary_x[i])
                y_dict.append(decision_boundary_y[i])
                color_dict.append(decision_boundary_color)
            for i in range(300):
                x_dict.append(test_x[i])
                y_dict.append(test_y[i])
                color_dict.append(test_color[i])
            for i in range(min(len(train_x),600)):
                x_dict.append(train_x[i])
                y_dict.append(train_y[i])
                color_dict.append(train_color[i])

            return wandb.visualize(
                'wandb/decision_boundaries/v1', wandb.Table(
                columns=['x', 'y', 'color'],
                data=[
                    [x_dict[i], y_dict[i], color_dict[i]] for i in range(len(x_dict))
                ]
            ))
        wandb.log({'decision_boundaries': decision_boundaries(decision_boundary_x,
                                    decision_boundary_y, decision_boundary_color,
                                    train_x, train_y, train_color, test_x, test_y,
                                test_color)})