import torch
import numpy as np
from .FL import *
from sklearn.preprocessing import minmax_scale
from scipy.stats import entropy
from scipy.spatial.distance import cdist, jaccard

def Prox(X, x=None, **kwargs):
    if x is None:
        return .0

    y = kwargs['y']
    prox = cdist(X[y==0], torch.unsqueeze(x, 0), 'jaccard')
    return(1.-float(np.mean(prox[:, 0])))

def EntBug(X, x=None, **kwargs):
    N, M = X.shape

    X = X.type(torch.uint8)
    if x is not None:
        if x.dim() > 1:
            x = torch.squeeze(x, 0)
        X = torch.cat([X, torch.unsqueeze(x.type(torch.uint8), 0)], dim=0)

    if torch.cuda.is_available():
        X = X.cuda()

    density = torch.sum(X) / torch.tensor(N * M, dtype=torch.float32)
    value = torch.abs(0.5 - density)
    return float(value)


def FLINT(X, x=None, **kwargs):
    N, M = X.shape

    if 'y' in kwargs:
        y = kwargs['y']
    else:
        y = torch.zeros(N, dtype=torch.uint8)
    if 'spectrum' in kwargs:
        spec = kwargs['spectrum']
    else:
        spec = spectrum(X, y)

    ts = tarantula(*spec)# tarantula score
    e_p, n_p, e_f, n_f = spec
    norm_ts = ts/torch.sum(ts)
    curr_entropy = entropy(norm_ts, base=2)

    if x is None:
        return float(curr_entropy)

    pass_ts = tarantula(e_p + x, n_p + (1 - x), e_f, n_f)
    norm_pass_ts = pass_ts/torch.sum(pass_ts)
    fail_ts = tarantula(e_p, n_p, e_f + x, n_f + (1 - x))
    norm_fail_ts = fail_ts/torch.sum(fail_ts)
    alpha = 1 - torch.sum(y)/torch.tensor(N, dtype=torch.float32)
    prob_ts = norm_fail_ts * alpha + norm_pass_ts * (1 - alpha)
    lookahead_entropy = entropy(prob_ts, base=2)
    """
    print("               tau_pass  (PS):" , pass_ts)
    print("    normalized tau_pass (nPS):", norm_pass_ts)
    print("               tau_fail  (FS):", fail_ts)
    print("    normalized tau_fail (nFS):", norm_fail_ts)
    print("                        alpha:", alpha)
    print("nFS * alpha + nPS * (1-alpha):", prob_ts)
    print(" FS * alpha +  PS * (1-alpha):", tmp_ts)
    print(" FS * alpha +  PS * (1-alpha):", tmp_ts/torch.sum(tmp_ts), "(normalized)")
    print("            lookahead entropy:", lookahead_entropy)
    """
    #print(lookahead_entropy, curr_entropy - lookahead_entropy)
    return float(lookahead_entropy) #float(curr_entropy - lookahead_entropy)

def TfD(X, x=None, **kargs):
    N, M = X.shape

    X = X.type(torch.uint8)
    if x is not None:
        if x.dim() > 1:
            x = torch.squeeze(x, 0)
        X = torch.cat([X, torch.unsqueeze(x.type(torch.uint8), 0)], dim=0)

    if torch.cuda.is_available():
        X = X.cuda()

    unique_elems = torch.unique(X, sorted=False, dim=1)
    num_DBBs = unique_elems.shape[1]
    return float(num_DBBs)

def EE(X, x=None, **kwargs):
    _, M = X.shape

    X = X.type(torch.uint8)
    if x is not None:
        if x.dim() > 1:
            x = torch.squeeze(x, 0)
        X = torch.cat([X, torch.unsqueeze(x.type(torch.uint8), 0)], dim=0)

    if 'w' not in kwargs:
        # Initialize w.
        w = torch.ones(M, dtype=torch.float32)
    else:
        w = torch.tensor(minmax_scale(kwargs['w']), dtype=torch.float32)

    if torch.all(w == 0):
        w = 1. - w

    if torch.cuda.is_available():
        X = X.cuda()
        w = w.cuda()

    u, indices = torch.unique(X, sorted=False, return_inverse=True, dim=1)
    value = .0
    tw = torch.sum(w)
    for j in range(u.shape[1]):
        gm = (indices == j).type(w.dtype)
        gw = torch.dot(w, gm)/tw
        value += gw * (torch.sum(gm) - 1)
    #value /= torch.sum(w)
    value = 1 - value / (M - 1)
    assert 0 <= value <= 1
    return float(value)

def cEE(X, x=None, **kwargs):
    _, M = X.shape

    X = X.type(torch.uint8)
    if x is not None:
        if x.dim() > 1:
            x = torch.squeeze(x, 0)
        X = torch.cat([X, torch.unsqueeze(x.type(torch.uint8), 0)], dim=0)
    else:
        x = torch.any(X, dim=0)

    if 'w' not in kwargs:
        # Initialize w.
        w = torch.ones(M, dtype=torch.float32)
    else:
        w = torch.tensor(minmax_scale(kwargs['w']), dtype=torch.float32)

    if torch.all(w == 0):
        w = 1. - w

    if torch.cuda.is_available():
        X = X.cuda()
        x = x.cuda()
        w = w.cuda()

    u, indices = torch.unique(X, sorted=False, return_inverse=True, dim=1)
    value = .0
    tw = torch.sum(w)
    for j in range(u.shape[1]):
        gm = (indices == j).type(w.dtype)
        gw = torch.dot(w, gm)/tw
        value += gw * (torch.sum(gm) - 1)
    value = 1 - (value / (M - 1))
    #assert 0 <= value <= 1
    coverage = torch.dot(x.type(w.dtype), w)/M
    value += coverage
    return float(value)

def C(X, x=None, **kwargs):
    _, M = X.shape

    X = X.type(torch.uint8)
    if x is None:
        x = torch.any(X, dim=0)

    if 'w' not in kwargs:
        # Initialize w.
        w = torch.ones(M, dtype=torch.float32)
    else:
        w = torch.tensor(minmax_scale(kwargs['w']), dtype=torch.float32)

    if torch.cuda.is_available():
        x = x.cuda()
        w = w.cuda()

    coverage = torch.dot(x.type(w.dtype), w)/M
    return float(coverage)

def S3(X, x=None, **kwargs):
    if x is None:
        #x = torch.sum(X, dim=0)
        #covered = torch.sum(x == .0)
        #assert X.shape[0] == 1
        #return min(int(torch=sum(x == .0)(, int(x > .0))
        return .0

    target = kwargs['target']
    X = X[:, target]
    x = x[target]
    y = kwargs['y']

    if torch.sum(x) == .0 or torch.sum(x) == x.shape[0]:
        return .0

    if torch.cuda.is_available():
        X = X.cuda()
        x = x.cuda()

    spec = torch.stack((torch.sum(X[y==0], dim=0), torch.sum(X[y==1], dim=0)))
    u, indices, counts = torch.unique(spec, sorted=False, return_counts=True,
                                      return_inverse=True, dim=1)
    value = 0
    total_fail = torch.sum(1 - y)
    for j in range(u.shape[1]):
        ep = x[indices == j]
        div = min(int(torch.sum(ep==0)), int(torch.sum(ep==1)))
        p = u[0, j]
        value += div*p
    return float(value/total_fail)

def RAPTER(X, x=None, **kwargs):
    _, M = X.shape

    X = X.type(torch.uint8)
    if x is not None:
        if x.dim() > 1:
            x = torch.squeeze(x, 0)
        X = torch.cat([X, torch.unsqueeze(x.type(torch.uint8), 0)], dim=0)

    if torch.cuda.is_available():
        X = X.cuda()

    u, counts = torch.unique(X, sorted=False, return_counts=True, dim=1)
    value = torch.sum(counts * (counts - 1))
    value /= 2*M
    #assert 0 <= value <= 1
    return float(value)

def diversity(X, **kwargs):
    N, M = X.shape
    unique_tests, counts = torch.unique(X, sorted=False, return_counts=True, dim=0)
    if N > 1:
        value = torch.sum(counts * (counts - 1))
        value /= N * (N - 1)
        value = 1 - value
    else:
        value = 1.
    assert 0 <= value <= 1
    return float(value)

def density(X, **kwargs):
    N, M = X.shape
    value = torch.sum(X) / (N * M)
    value = 1 - abs(1 - 2*value)
    assert 0 <= value <= 1
    return float(value)

def uniqueness(X, **kwargs):
    N, M = X.shape
    unique_elems = torch.unique(X, sorted=False, dim=1)
    value = unique_elems.shape[1] / M
    assert 0 <= value <= 1
    return float(value)

def DDU(X, x=None, **kwargs):
    X = X.type(torch.uint8)
    if x is not None:
        if x.dim() > 1:
            x = torch.squeeze(x, 0)
        X = torch.cat([X, torch.unsqueeze(x.type(torch.uint8), 0)], dim=0)

    if torch.cuda.is_available():
        X = X.cuda()

    value = diversity(X, **kwargs) * density(X, **kwargs) * uniqueness(X, **kwargs)
    del X
    return value

def DDU_fast(X, x=None, **kwargs):
    X = X.type(torch.uint8)
    if x is not None:
        if x.dim() > 1:
            x = torch.squeeze(x, 0)
        X = torch.cat([X, torch.unsqueeze(x.type(torch.uint8), 0)], dim=0)

    if torch.cuda.is_available():
        X = X.cuda()

    N, M = X.shape
    unique_tests, counts = torch.unique(X, sorted=False, return_counts=True, dim=0)
    if N > 1:
        diversity = torch.sum(counts * (counts - 1))
        diversity /= diversity * (diversity - 1)
        diversity = 1 - diversity
    else:
        diversity = 1.

    density = torch.sum(X) / torch.tensor(N * M, dtype=torch.float32)
    density = 1 - torch.abs(1 - 2*density)

    unique_elems = torch.unique(X, sorted=False, dim=1)
    uniqueness = unique_elems.shape[1] / M

    return float(diversity * density * uniqueness)

if __name__ == "__main__":
    X = torch.tensor([
        [1,1,1,1,1,0,0,0,1],
        [0,0,0,0,0,1,1,1,1]], dtype=torch.float32)
    x = torch.tensor([1,1,1,0,1,0,1,0,0], dtype=torch.float32)
    print(FLINT(X, x=x, **{'y': torch.tensor([1, 0], dtype=torch.float32)}))
