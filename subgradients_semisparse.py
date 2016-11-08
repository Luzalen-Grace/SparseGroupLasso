import numpy
from utils import S, norm_non0

__author__ = 'Romain Tavenard romain.tavenard[at]univ-rennes2.fr'


class SGL:
    def __init__(self, groups, alpha, lbda, ind_sparse, max_iter=10000, rtol=1e-6):
        self.ind_sparse = ind_sparse
        self.groups = groups
        self.alpha = alpha
        self.lbda = lbda
        self.max_iter = max_iter
        self.rtol = rtol
        self.coef_ = None

    def fit(self, X, y):
        # Assumption: group ids are between 0 and max(groups)
        # Other assumption: ind_sparse is of dimension X.shape[1] and has 0 if the dimension should not be pushed
        # towards sparsity and 1 otherwise
        n_groups = numpy.max(self.groups) + 1
        n, d = X.shape
        alpha_lambda = self.alpha * self.lbda * self.ind_sparse
        self.coef_ = numpy.random.randn(d)
        for iter in range(self.max_iter):
            beta_old = self.coef_.copy()
            for gr in range(n_groups):
                # 1- Should the group be zero-ed out?
                indices_group_k = self.groups == gr
                X_k = X[:, indices_group_k]
                r_no_k = y - numpy.dot(X, self.coef_) + numpy.dot(X_k, self.coef_[indices_group_k])
                norm_2 = numpy.linalg.norm(S(numpy.dot(X_k.T, r_no_k) / n, alpha_lambda[indices_group_k]))
                p_l = numpy.sqrt(numpy.sum(indices_group_k))
                if norm_2 <= (1 - self.alpha) * self.lbda * p_l:
                    self.coef_[indices_group_k] = 0.
                else:
                    # 2- If the group is not zero-ed out, update each component
                    for i in range(d):
                        if self.groups[i] == gr:
                            norm2_beta_k = norm_non0(self.coef_[indices_group_k])
                            X_i_k = X[:, i]
                            r_no_i = y - numpy.dot(X, self.coef_) + self.coef_[i] * X_i_k
                            denom = numpy.dot(X_i_k.T, X_i_k) / n + (1 - self.alpha) * self.lbda * p_l / norm2_beta_k
                            self.coef_[i] = S(numpy.dot(X_i_k.T, r_no_i) / n, alpha_lambda[i]) / denom
            norm_beta = norm_non0(self.coef_)
            if numpy.linalg.norm(self.coef_ - beta_old) / norm_beta < self.rtol:
                break
        return self
