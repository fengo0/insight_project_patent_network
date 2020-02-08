#!/usr/bin/env python2
import pandas as pd

def split_seq(seq, size):
        newseq = []
        splitsize = 1.0/size*len(seq)
        for i in range(size):
                newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
        return newseq

### function to cut long text into chunk_size you defined

def text_chunk(text,chunk_size):
    df = pd.DataFrame([])
    text_map = {}
    
    keys = ['text_'+str(i) for i in range(0, int(chunk_size))]
     
    for i in range(0,len(brf_text)):
        brf_text_chunk = split_seq(brf_text[i:i+1].values[0][0],int(chunk_size))
        
        k = 0
        for j in keys:
            text_case = {j:brf_text_chunk[k]}
            text_map.update(text_case)
            k = k + 1
      
        data = pd.DataFrame(text_map.items())
        data = data.transpose()
        data.columns = data.iloc[0]
        data = data.drop(data.index[[0]])
        df = df.append(data)

    df = df.reset_index(drop=True)
    return df