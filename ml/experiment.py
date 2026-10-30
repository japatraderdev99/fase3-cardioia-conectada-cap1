"""Comparação didática reproduzível. Todas as séries são sintéticas; sem uso clínico."""
from pathlib import Path
import csv, hashlib, json, platform, sys, time
import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

SEED = 568506
ROOT = Path(__file__).resolve().parent

def generate(n=1200, steps=180):
    """Uma janela por indivíduo sintético independente; 1 Hz, 3 minutos.
    Label é o cenário latente de elevação sustentada/intermitente, não diagnóstico.
    Há sobreposição intencional com exercício sintético na classe 0.
    """
    rng = np.random.default_rng(SEED)
    y = np.tile([0, 1], n // 2)
    rng.shuffle(y)
    x = np.zeros((n, steps))
    for i, label in enumerate(y):
        baseline = rng.normal(85, 13)
        noise = rng.normal(0, 3, steps)
        for t in range(1, steps):
            noise[t] += .65 * noise[t - 1]
        start = int(rng.integers(15, 90))
        duration = int(rng.integers(45, 100) if label else rng.integers(5, 55))
        amplitude = rng.normal(34 if label else 20, 13)
        envelope = np.zeros(steps)
        envelope[start:min(start + duration, steps)] = amplitude
        x[i] = np.clip(baseline + noise + envelope + 3*np.sin(np.arange(steps)/12), 35, 200)
    return x, y

def statistics(x):
    """Mesma série original; resumos fixados antes da avaliação."""
    return np.column_stack([x.mean(1), x.std(1), x.min(1), x.max(1),
        np.quantile(x, .9, axis=1), (x > 120).mean(1),
        np.abs(np.diff(x, axis=1)).mean(1), x[:, -30:].mean(1)-x[:, :30].mean(1)])

def lif(x, return_spikes=False):
    """Banco de 24 neurônios LIF sem recorrência, pesos fixos.
    Euler: v += dt/tau * (-v + I), limiar 1, reset 0.
    dt=1 é um passo normalizado por amostra, não simulação biofísica em ms.
    Corrente recebe três canais BPM normalizados e três ganhos; dois taus.
    O banco não aprende; readout logístico supervisionado aprende no treino.
    """
    channels = np.stack([np.clip((x-50)/100,0,2), np.clip((x-90)/60,0,2),
                         np.clip(np.abs(np.diff(x, prepend=x[:, :1], axis=1))/10,0,2)], -1)
    # 3 canais x 4 ganhos x 2 constantes = 24 unidades.
    currents = (channels[..., :, None, None] * np.array([1.5,2.5,4.,6.])[None,None,None,:,None])
    currents = np.broadcast_to(currents, (len(x), x.shape[1], 3,4,2)).reshape(len(x), x.shape[1],24)
    tau = np.tile([3.,10.],12)
    v = np.zeros((len(x),24))
    spikes = np.zeros_like(currents, dtype=np.uint8)
    for t in range(x.shape[1]):
        v += (-v + currents[:,t])/tau
        fire = v >= 1.
        spikes[:,t] = fire
        v[fire] = 0.
    features = np.concatenate([part.mean(1) for part in np.array_split(spikes, 3, axis=1)],1)
    return (features,spikes) if return_spikes else features

def scores(y,p):
    pred = p >= .5
    return {"accuracy":accuracy_score(y,pred),"precision":precision_score(y,pred,zero_division=0),
      "recall":recall_score(y,pred,zero_division=0),"f1":f1_score(y,pred,zero_division=0),
      "roc_auc":roc_auc_score(y,p),"confusion_matrix_tn_fp_fn_tp":confusion_matrix(y,pred).ravel().tolist()}

def run(out=None):
    out = Path(out or ROOT/'results'); out.mkdir(parents=True,exist_ok=True)
    x,y = generate(); ids = np.arange(len(y))
    train, rest = train_test_split(ids,test_size=.4,stratify=y,random_state=SEED)
    val,test = train_test_split(rest,test_size=.5,stratify=y[rest],random_state=SEED+1)
    assert not (set(train)&set(test) or set(train)&set(val) or set(val)&set(test))
    results = {"seed":SEED,"synthetic":True,"sampling_hz":1,"window_seconds":180,
      "split_sizes":{"train":len(train),"validation":len(val),"test":len(test)},
      "split_ids":{k:v.tolist() for k,v in [('train',train),('validation',val),('test',test)]},
      "environment":{"python":sys.version.split()[0],"numpy":np.__version__,"sklearn":sklearn.__version__,
                     "platform":platform.platform()},"models":{}}
    predictions=[]
    for name, transform in [('logistic_statistics',statistics),('lif_logistic_readout',lif)]:
        features=transform(x)
        candidates=[]
        for c in [.1,1.,10.]:
            model=make_pipeline(StandardScaler(),LogisticRegression(C=c,solver="liblinear",max_iter=2000,random_state=SEED))
            t=time.perf_counter(); model.fit(features[train],y[train]); fit=time.perf_counter()-t
            score=f1_score(y[val],model.predict(features[val]))
            candidates.append((score,c,model,fit))
        best=max(candidates,key=lambda item:item[0]); _,c,model,fit=best
        # Sem retreino em validação: avaliação única da configuração selecionada.
        p=model.predict_proba(features[test])[:,1]
        timings=[]
        for _ in range(7):
            t=time.perf_counter(); model.predict_proba(transform(x[test])); timings.append(time.perf_counter()-t)
        m=scores(y[test],p)
        m.update({"selected_C":c,"validation_f1":best[0],"feature_count":features.shape[1],
          "fit_seconds_selected":fit,"inference_batch_seconds_median":float(np.median(timings)),
          "inference_batch_size":len(test),"validation_candidates":[{"C":z[1],"f1":z[0]} for z in candidates]})
        results['models'][name]=m
        predictions.extend({'model':name,'synthetic_id':int(i),'label':int(y[i]),'probability':float(q),'prediction':int(q>=.5)} for i,q in zip(test,p))
    np.savez_compressed(out/'synthetic_series.npz',bpm=x,labels=y,synthetic_ids=ids)
    results['dataset_sha256']=hashlib.sha256((out/'synthetic_series.npz').read_bytes()).hexdigest()
    with (out/'predictions.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(predictions[0]));w.writeheader();w.writerows(predictions)
    (out/'metrics.json').write_text(json.dumps(results,indent=2)+'\n')
    return results

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
