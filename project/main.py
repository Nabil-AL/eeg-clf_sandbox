

from project.constants import *
from project.preprocessing_utils import (load_data_from_mat, butter_bandpass_filter,
                                         prepare_data)
from project.classify_utils import cross_val, manual_cross_val, evaluate
from project.model_utils import *
from project.display_result_utils import print_results, save_barplot, write_report

import os
import mne
from scipy.io import loadmat
import glob


data_path = "./data/"
fig_dir = "./results/"
number_of_subject = 1  # 10
plot_erp = False
# See constants.py
clf_selection = ["CSP + Log-reg", "CSP + LDA", "Cov + TSLR", "Cov + TSLDA",
                 "Cov + FgMDM", "CSP + TS + PCA + LR"]
score_selection = ['accuracy', 'roc_auc']

clf_dict = {}
for clf in clf_selection:
    for pipeline_name, pipeline_value in all_clf_dict.items():
        if clf == pipeline_name:
            clf_dict[pipeline_name] = pipeline_value

score_dict = {}
for score in score_selection:
    for score_name, scorer in all_score_dict.items():
        if score == score_name:
            score_dict[score_name] = scorer

# train_files = glob.glob(data_path + '/*[1-8]T.mat')
# eval_files = glob.glob(data_path + '/*[1-8]E.mat')
# if not len(train_files) or (len(train_files) != len(eval_files)):
# print(f"Error when fetched the training and evaluation .mat files from {data_path}")

# Get the channel location file if it exists
channel_file = glob.glob(data_path + '/*.locs')
if channel_file:
    if len(channel_file) > 1:
        print("error several .locs files in the folder")
    else:
        print("channel file found")
        montage = mne.channels.read_custom_montage(channel_file[0])
else:
    print("no channel file found")
    montage = default_channel_names

if not os.path.exists(fig_dir):
    try:
        os.mkdir(fig_dir)
        print(f"folder '{fig_dir}' created")
    except OSError:
        print(f"creation of the directory {fig_dir} failed")

for i in range(0, number_of_subject):
    if i < 9:
        subj_nbr = f"0{i+1}"
    else:
        subj_nbr = i+1
    train_file = str(f"{data_path}parsed_P{subj_nbr}T.mat")
    eval_file = str(f"{data_path}parsed_P{subj_nbr}E.mat")
    print(f"treating subject {i+1}")

    # get the eeg info if they exist
    if i == 0:
        try:
            # ndarray (1,1)
            cue_time = loadmat(train_file)["cueAt"][0][0]
        except KeyError as e:
            print("No cue time found") #verbose
            cue_time = default_cue_time
        try:
            # ndarray (1,1)
            sample_rate = loadmat(train_file)["sampRate"][0][0]
        except KeyError as e:
            print("No sample rate found")  # verbose
            sample_rate = default_sample_rate
    try:
        raw_train_data, labels_train = load_data_from_mat(train_file)
        raw_eval_data, labels_eval = load_data_from_mat(eval_file)
    except KeyError:
        print("error")
        exit(1)

    raw_train_filtered = butter_bandpass_filter(raw_train_data, low_freq, high_freq,
                                                sample_rate, order=5)
    raw_eval_filtered = butter_bandpass_filter(raw_eval_data, low_freq, high_freq,
                                               sample_rate, order=5)
    #if plot_erp:
        # Transpose EEG data and convert from uV to Volts ?
        # raw_training[:-1] *= 1e-6
        # function plot_erp
    X, y = prepare_data(raw_train_filtered,
                        labels_train,
                        sample_rate,
                        t_low=-default_t_clf)
    X_eval, y_eval = prepare_data(raw_eval_filtered,
                                  labels_eval,
                                  sample_rate,
                                  t_low=-default_t_clf)

    # results_dict_cv = cross_val(clf_dict, X, y, score_selection, 5, return_train_score)

    # results_dict_manualcv = manual_cross_val(clf_dict, X, y, score_dict, 5)

    results_dict_eval = evaluate(clf_dict, X, y, score_dict, X_eval, y_eval)

    write_report(results_dict_eval, f"{fig_dir}patient{subj_nbr}.json")

    scores_results_dict, methods = print_results(subj_nbr,
                                                 results_dict_eval,
                                                 mode="eval",
                                                 return_train_score=False)

    save_barplot(scores_results_dict, methods, subj_nbr, fig_dir, mode="eval")
