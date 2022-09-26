"""
File containing all the preprocessing constants for a dataset to be customized.
Moreover you have the dictionaries storing the score metrics and the classification
pipeline in which you can pick for the main.py file
"""

from mne.decoding import CSP, Vectorizer

from sklearn.metrics import (accuracy_score, precision_score, roc_auc_score,
                             cohen_kappa_score)
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC, SVC
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline

from pyriemann.estimation import Covariances, ERPCovariances, XdawnCovariances
from pyriemann.tangentspace import TangentSpace, FGDA
from pyriemann.classification import MDM, FgMDM, KNearestNeighbor
from pyriemann.spatialfilters import CSP as covCSP

# Processing constants for the Clinical BCI Challenge WCCI-2020 dataset
"""
The signals were sampled at 512 Hz and initially filtered with 0.1 to 100 Hz pass-band 
filter and a notch filter at 50 Hz during data acquisition.
"""
default_sample_rate = 512
default_channel_names = ['F3', 'FC3', 'C3', 'CP3', 'P3', 'FCz', 'CPz', 'F4', 'FC4', 'C4',
                         'CP4', 'P4']
montage = "standard_1020"
default_cue_time = 3.0
event_id = {'left-hand': 1, 'right-hand': 2}

# bandpass filter parameters
low_freq = 8
high_freq = 24
# time segment (in seconds) used for the classification
default_t_clf = 3

# classification constants
return_train_score = True

### Scores metrics
# To choose : "https://scikit-learn.org/stable/modules/" \
 # "model_evaluation.html#common-cases-predefined-values"

# Score dict
all_score_dict = {
    'accuracy': accuracy_score,
    'precision': precision_score,
    'roc_auc': roc_auc_score,
    'kappa': cohen_kappa_score
}

## Classification pipeline dict containing all the classification methods
"""
Feature selection & extraction:
- Vect: Vectorisation
- Cov: Estimation of covariance
- ERPCov: Estimate special form covariance matrix for ERP [1]

Feature scaling:
- Scale: Standardize features by removing the mean and scaling to unit variance.

Spatial filtering:
- CSP: Signal decomposition using the Common Spatial Patterns (CSP) [2].
- TS: Project the data in the tangent (euclidian) space of the Riemannian manifold [3].
- covCSP: Common Spatial Pattern spatial filtering with covariance matrices as inputs [4]
- FGDA: Geodesic filtering. It consists in projecting first the data in the tangent 
space, filter them and project them back in the manifold [5]. 
- FgMDM: Geodesic filtering + classification with Minimum Distance to Mean [3].
- XdawnCov: Spatial filtering method designed to improve the signal to signal + noise 
ratio (SSNR) of the ERP responses [6].

Dimension reduction:
- PCA: Principal component analysis (PCA). Linear dimensionality reduction using Singular 
Value Decomposition of the data to project it to a lower dimensional space. 

Classifiers:
- KNN: K-nearest neighbors
- Log-reg or LR: Least squares Linear Regression
- kerSVM: Support Vector Machines using Radial Basis Function (RBF) kernel.
https://scikit-learn.org/stable/modules/svm.html#parameters-of-the-rbf-kernel
- linSVM: Support Vector Machines with (faster) implementation of Support Vector 
Classification for the case of a linear kernel.
- LDA: Linear Discriminant Analysis.
- regLDA: Linear Discriminant Analysis regularized with shrinkage (improve the 
estimation of covariance matrices in situations where the number of training samples is 
small).
- MDM: Minimum Distance to Mean algorithm (classification by nearest centroid).


[1] A. Barachant, M. Congedo ,”A Plug&Play P300 BCI Using Information Geometry”, 
arXiv:1409.0107, 2014.

[2] Zoltan J. Koles, Michael S. Lazar, Steven Z. Zhou. Spatial Patterns Underlying 
Population Differences in the Background EEG. Brain Topography 2(4), 275-284, 1990.

[3] A. Barachant, S. Bonnet, M. Congedo and C. Jutten, “Multiclass Brain-Computer 
Interface Classification by Riemannian Geometry,”” in IEEE Trans Biomed Eng, vol. 59, 
no. 4, p. 920-928, 2012

[4] A. Barachant, S. Bonnet, M. Congedo and C. Jutten, Common Spatial Pattern revisited 
by Riemannian geometry, IEEE International Workshop on Multimedia Signal Processing 
(MMSP), p. 472-476, 2010.

[5] A. Barachant, S. Bonnet, M. Congedo and C. Jutten, “Riemannian geometry applied to 
BCI classification”, 9th International Conference Latent Variable Analysis and Signal 
Separation (LVA/ICA 2010), LNCS vol. 6365, 2010, p. 629-636.

[6] Rivet, B., Souloumiac, A., Attina, V., & Gibert, G. (2009). xDAWN algorithm to 
enhance evoked potentials: application to brain-computer interface. Biomedical 
Engineering, IEEE Transactions on, 56(8), 2035-2043.
"""

all_clf_dict = {
    "Vect + KNN": make_pipeline(Vectorizer(), KNeighborsClassifier()),
    "Vect + Log-reg": make_pipeline(Vectorizer(), LogisticRegression(max_iter=100)),
    "Vect + Scale + LR": make_pipeline(Vectorizer(), StandardScaler(),
                                       LogisticRegression(max_iter=100)),
    "Vect + LinSVM": make_pipeline(Vectorizer(), LinearSVC(random_state=0)),
    "Vect + kerSVM": make_pipeline(Vectorizer(), SVC()),
    "Vect + LDA": make_pipeline(Vectorizer(), LinearDiscriminantAnalysis()),
    "Vect + RegLDA": make_pipeline(
        Vectorizer(),
        LinearDiscriminantAnalysis(shrinkage='auto', solver='eigen')
    ),
    "CSP + KNN": make_pipeline(CSP(n_components=4, log=True), KNeighborsClassifier()),
    "CSP + Log-reg": make_pipeline(CSP(n_components=4, log=True),
                                   LogisticRegression(max_iter=100)),
    "RegCSP + Log-reg": make_pipeline(CSP(n_components=4, reg='ledoit_wolf', log=True),
                                      LogisticRegression()),
    "CSP + LinSVM": make_pipeline(CSP(n_components=4, log=True),
                                  LinearSVC(random_state=0)),
    "CSP + kerSVM": make_pipeline(CSP(n_components=4, log=True), SVC()),
    "CSP + LDA": make_pipeline(CSP(n_components=4, log=True),
                               LinearDiscriminantAnalysis()),
    "CSP + RegLDA": make_pipeline(
        CSP(n_components=4, log=True),
        LinearDiscriminantAnalysis(shrinkage='auto', solver='eigen')
    ),
    "Cov + MDM": make_pipeline(Covariances(),
                               MDM(metric=dict(mean='riemann', distance='riemann'))),
    "Cov + FgMDM": make_pipeline(Covariances(),
                                 FgMDM(metric=dict(mean='riemann', distance='riemann'))),
    "Cov + TSLR": make_pipeline(Covariances(), TangentSpace(),
                                LogisticRegression()),
    "Cov + TSkerSVM": make_pipeline(Covariances(), TangentSpace(),
                                    SVC()),
    "Cov + TSLDA": make_pipeline(Covariances(), TangentSpace(),
                                 LinearDiscriminantAnalysis()),
    "CSP + TSLR": make_pipeline(Covariances(), covCSP(nfilter=4, log=False),
                                TangentSpace(), LogisticRegression()),
    "CSP + TS + PCA + LR": make_pipeline(Covariances(), covCSP(nfilter=4, log=False),
                                         TangentSpace(), PCA(n_components=2),
                                         LogisticRegression()),
    "ERPCov + TS": make_pipeline(ERPCovariances(estimator='oas'), TangentSpace(),
                                 LogisticRegression()),
    "ERPCov + MDM": make_pipeline(ERPCovariances(estimator='oas'), MDM()),  # default scm, lwf
    "XdawnCov + TS": make_pipeline(XdawnCovariances(estimator='oas'), TangentSpace(),
                                   LogisticRegression()),  # default scm, lwf
    "XdawnCov + MDM": make_pipeline(XdawnCovariances(estimator='oas'), MDM()),
}

# "Cov + TSFGDA": make_pipeline(Covariances(), FGDA(), PCA(n_components=2),
#                              LinearDiscriminantAnalysis()),
# "Cov + TSFGDA + PCA + SVM": make_pipeline(Covariances(), FGDA(), PCA(n_components=2),
#                               SVC()),