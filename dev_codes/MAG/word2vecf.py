import heapq
# from itertools import izip
import numpy as np
import torch.nn as nn
import torch

def ugly_normalize(vecs):
   normalizers = np.sqrt((vecs * vecs).sum(axis=1))
   normalizers[normalizers==0]=1
   return (vecs.T / normalizers).T

class Embeddings:
   def __init__(self, vecsfile, vocabfile=None, normalize=True):
      if vocabfile is None: vocabfile = vecsfile.replace("npy","vocab")
      self._vecs = np.load(vecsfile)
      self._vocab = open(vocabfile).read().split()
      if normalize:
         self._vecs = ugly_normalize(self._vecs)
      self._w2v = {w:i for i,w in enumerate(self._vocab)}
    
   @classmethod
   def load(cls, vecsfile, vocabfile=None):
      return Embeddings(vecsfile, vocabfile)

   def word2vec(self, w):
      return self._vecs[self._w2v[w]]

   def similar_to_vec(self, v, N=10):
      sims = self._vecs.dot(v)
      sims = heapq.nlargest(N, zip(sims,self._vocab,self._vecs))
      return sims

   def similar_to_target_vec(self, w1, w2, dc=6):
      idx1 = self._vocab.index(w1)
      v1 = torch.tensor(self._vecs[idx1])
    
      idx2 = self._vocab.index(w2)
      v2 = torch.tensor(self._vecs[idx2])
    
      cos = nn.CosineSimilarity(dim=0, eps=1e-6)
      return round(float(cos(v1, v2)), dc)

   def most_similar(self, word, N=10):
      w = self._vocab.index(word)
      sims = self._vecs.dot(self._vecs[w])
      sims = heapq.nlargest(N+1, zip(sims,self._vocab))
      sims = [s for s in sims if s[1] != word]
      return sims[:N]

   def analogy(self, pos1, neg1, pos2,N=10,mult=True):
      wvecs, vocab = self._vecs, self._vocab
      p1 = vocab.index(pos1)
      p2 = vocab.index(pos2)
      n1 = vocab.index(neg1)
      if mult:
         p1,p2,n1 = [(1+wvecs.dot(wvecs[i]))/2 for i in (p1,p2,n1)]
         if N == 1:
            return max(((v,w) for v,w in zip((p1 * p2 / n1),vocab) if w not in [pos1,pos2,neg1]))
         return heapq.nlargest(N,((v,w) for v,w in zip((p1 * p2 / n1),vocab) if w not in [pos1,pos2,neg1]))
      else:
         p1,p2,n1 = [(wvecs.dot(wvecs[i])) for i in (p1,p2,n1)]
         if N == 1:
            return max(((v,w) for v,w in zip((p1 + p2 - n1),vocab) if w not in [pos1,pos2,neg1]))
         return heapq.nlargest(N,((v,w) for v,w in zip((p1 + p2 - n1),vocab) if w not in [pos1,pos2,neg1]))
    
   def getw2v_txt(self):
      vectors = []
      for w, vec in zip(self._vocab, self._vecs):
         line = " ".join(vec.astype(str))
         line = w+" "+line
         vectors += [line]
#       ln, size = self._vecs.shape
#       vectors = [str(ln)+" "+str(size)] + vectors
      return np.array(vectors)
