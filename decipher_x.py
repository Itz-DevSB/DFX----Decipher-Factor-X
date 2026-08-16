"""
============================================================
DECIPHER-X v2
A classical-cipher / encoding cracking tool
============================================================

This file is the main DECIPHER-X v2 source code.
"""

# The complete source supplied in the conversation is being added as
# the repository's main decoder implementation.

import base64
import itertools
import math
import os
import random
import re
import string
import time
import urllib.parse
from collections import Counter
from datetime import datetime

ASCII_UP = string.ascii_uppercase

# English-likelihood data
LETTER_FREQ = {
    "E": 12.70, "T": 9.06, "A": 8.17, "O": 7.51, "I": 6.97, "N": 6.75,
    "S": 6.33, "H": 6.09, "R": 5.99, "D": 4.25, "L": 4.03, "C": 2.78,
    "U": 2.76, "M": 2.41, "W": 2.36, "F": 2.23, "G": 2.02, "Y": 1.97,
    "P": 1.93, "B": 1.29, "V": 0.98, "K": 0.77, "J": 0.15, "X": 0.15,
    "Q": 0.10, "Z": 0.07,
}

BIGRAM_FREQ = {"TH":3.56,"HE":3.07,"IN":2.43,"ER":2.05,"AN":1.99,"RE":1.85,"ON":1.76,"AT":1.49,"EN":1.45,"ND":1.35,"TI":1.34,"ES":1.34,"OR":1.28,"TE":1.20,"OF":1.17,"ED":1.17,"IS":1.13,"IT":1.12,"AL":1.09,"AR":1.07,"ST":1.05,"TO":1.04,"NT":1.04,"NG":.95,"SE":.93,"HA":.93,"AS":.87,"OU":.87,"IO":.83,"LE":.83,"VE":.83,"CO":.79,"ME":.79,"DE":.76,"HI":.76,"RI":.73,"RO":.73,"IC":.70,"NE":.69,"EA":.69,"RA":.69,"CE":.65,"LI":.62,"CH":.60,"LL":.58,"BE":.58,"MA":.57,"SI":.55,"OM":.55,"UR":.54,"CA":.52,"EL":.51,"TA":.50,"LA":.50,"NS":.49,"DI":.49,"FO":.48,"HO":.48,"PE":.47,"EC":.46,"PR":.46,"NO":.45,"CT":.45,"US":.45,"AC":.44,"OT":.44,"IL":.44,"TR":.43,"LY":.43,"NC":.43,"EX":.42,"WA":.42,"SO":.41,"GE":.41,"WI":.40,"OW":.40,"WH":.40,"TU":.39,"EE":.39,"PA":.39,"ID":.38,"AD":.38,"SA":.37,"NA":.37,"FI":.36,"UT":.36,"AM":.36,"OL":.35,"IE":.35,"IR":.35,"GA":.34,"IA":.34,"PO":.34,"RT":.34,"UN":.34,"IM":.34,"AI":.33,"GR":.32,"EV":.32,"PL":.32,"MO":.32,"SS":.32,"IV":.31,"FA":.31,"GH":.30,"AB":.30,"AY":.30,"TS":.30,"LO":.29,"CI":.29,"EM":.29,"GI":.28,"SU":.28,"OO":.28,"WE":.28,"OS":.27,"SP":.27,"PI":.27,"MI":.27,"BL":.26,"OP":.26,"MP":.25,"BU":.25,"AV":.24,"NI":.24,"EP":.23,"OD":.23,"UL":.23,"AG":.23,"OC":.22,"UM":.22,"TY":.22,"RD":.21,"DS":.21,"CU":.20,"KE":.20,"GO":.20,"EF":.20,"RN":.19,"SH":.19,"CL":.19,"SC":.18,"EI":.18,"DA":.18,"OV":.18,"NN":.17,"OI":.17,"OA":.16,"RS":.16,"UD":.16,"AK":.15,"RM":.15,"DR":.15,"BO":.15,"PU":.14,"AF":.14,"DU":.14,"BR":.14,"VI":.14,"KI":.13,"MU":.13,"AP":.13,"FE":.13,"NY":.13,"IF":.12,"GN":.12,"IG":.12,"MB":.11,"UG":.11,"AU":.11,"TW":.10,"GU":.10,"NF":.10,"UE":.10,"UA":.09,"RY":.09,"OB":.09,"SL":.09,"SK":.08,"WO":.08,"YO":.08}

BIGRAM_LOG = {a+b: math.log10(max(BIGRAM_FREQ.get(a+b, (LETTER_FREQ[a]/100)*(LETTER_FREQ[b]/100)*100), .0005)/100) for a in ASCII_UP for b in ASCII_UP}
COMMON_WORDS=set("THE BE TO OF AND A IN THAT HAVE I IT FOR NOT ON WITH HE AS YOU DO AT THIS BUT HIS BY FROM THEY WE SAY HER SHE OR AN WILL MY ONE ALL WOULD THERE THEIR WHAT SO UP OUT IF ABOUT WHO GET WHICH GO ME WHEN MAKE CAN LIKE TIME NO JUST HIM KNOW TAKE PEOPLE INTO YEAR YOUR GOOD SOME COULD THEM SEE OTHER THAN THEN NOW LOOK ONLY COME ITS OVER THINK ALSO BACK AFTER USE TWO HOW OUR WORK FIRST WELL WAY EVEN NEW WANT BECAUSE ANY THESE GIVE DAY MOST US IS ARE WAS WERE BEEN HAS HAD DID DOES SECRET MESSAGE HELLO WORLD PASSWORD CODE KEY MEET AT NOON MIDNIGHT ATTACK DAWN AGENT ENEMY LOCATION TARGET NORTH SOUTH EAST WEST".split())


def bigram_log_freq(bg):
    return BIGRAM_LOG.get(bg, math.log10(.0005/100))


def score_text(text):
    letters=[c for c in text.upper() if c.isalpha()]
    if len(letters)<2:return -9999.0
    n=len(letters); counts=Counter(letters)
    chi=sum(((counts.get(l,0)/n*100-LETTER_FREQ[l])**2)/LETTER_FREQ[l] for l in ASCII_UP)
    bs=sum(bigram_log_freq(letters[i:i+2]) for i in range(n-1))/max(n-1,1)
    words=re.findall(r"[A-Za-z]+",text.upper())
    bonus=sum(1 for w in words if w in COMMON_WORDS)/max(len(words),1)*25
    return (bs*12-chi*.04+bonus+sum(c.isprintable() for c in text)/max(len(text),1)*5)*min(1,n/20)-(1-min(1,n/20))*8


class Result:
    def __init__(self,method,text): self.method,self.text,self.score=method,text,score_text(text)

results=[]
def add_result(method,text):
    if text is not None and str(text).strip(): results.append(Result(method,str(text)))


def caesar(text,shift):
    out=[]
    for ch in text:
        if ch.isupper(): out.append(chr((ord(ch)-65-shift)%26+65))
        elif ch.islower(): out.append(chr((ord(ch)-97-shift)%26+97))
        else: out.append(ch)
    return ''.join(out)

def atbash(text):
    return ''.join(chr((90-(ord(c)-65))) if c.isupper() else chr((122-(ord(c)-97))) if c.islower() else c for c in text)
def rot13(text): return caesar(text,13)
def rot47(text): return ''.join(chr(33+((ord(c)-33+47)%94)) if 33<=ord(c)<=126 else c for c in text)
def reverse(text): return text[::-1]
def reverse_words(text): return ' '.join(reversed(text.split()))
def reverse_each_word(text): return ' '.join(w[::-1] for w in text.split())
def rotate(text,amount): return text[amount%len(text):]+text[:amount%len(text)] if text else text

def keyboard_shift(text,direction):
    rows=['qwertyuiop','asdfghjkl','zxcvbnm']; out=[]
    for ch in text:
        lo=ch.lower(); found=False
        for row in rows:
            if lo in row:
                x=row[(row.index(lo)+direction)%len(row)]; out.append(x.upper() if ch.isupper() else x); found=True; break
        if not found: out.append(ch)
    return ''.join(out)

def vigenere(text,key):
    if not key:return text
    key=key.upper();out=[];ki=0
    for ch in text:
        if ch.isalpha():
            base=65 if ch.isupper() else 97;out.append(chr((ord(ch)-base-(ord(key[ki%len(key)])-65))%26+base));ki+=1
        else:out.append(ch)
    return ''.join(out)

def beaufort(text,key):
    key=key.upper();out=[];ki=0
    for ch in text:
        if ch.isalpha():
            base=65 if ch.isupper() else 97;out.append(chr(((ord(key[ki%len(key)])-65)-(ord(ch)-base))%26+base));ki+=1
        else:out.append(ch)
    return ''.join(out)

def affine_decode(text,a,b):
    inv=next((x for x in range(26) if a*x%26==1),None)
    if inv is None:return None
    return ''.join(chr((inv*((ord(c)-65)-b))%26+65) if c.isupper() else chr((inv*((ord(c)-97)-b))%26+97) if c.islower() else c for c in text)

def numbers_to_ascii(text):
    nums=re.findall(r'\d+',text); return ''.join(chr(int(n)) for n in nums if int(n)<=255) or None

def a1z26(text):
    parts=re.split(r'[\s,;:/|.\-]+',text.strip())
    if not parts or any(not p.isdigit() or not 1<=int(p)<=26 for p in parts):return None
    return ''.join(chr(64+int(p)) for p in parts)

def binary_decode(text):
    c=re.sub(r'\s+','',text)
    if not c or not re.fullmatch('[01]+',c):return None
    for w in (7,8):
        if len(c)%w==0:
            try:
                x=''.join(chr(int(c[i:i+w],2)) for i in range(0,len(c),w))
                if all(q.isprintable() or q in '\n\r\t' for q in x):return x
            except:pass
    return None

def hex_decode(text):
    c=re.sub(r'(?i)0x|\s+','',text)
    if not c or len(c)%2 or not re.fullmatch('[0-9a-fA-F]+',c):return None
    try:return bytes.fromhex(c).decode('utf-8')
    except:return None

def base64_decode(text):
    try:return base64.b64decode(re.sub(r'\s+','',text),validate=True).decode()
    except:return None

def morse_decode(text):
    M={'.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G','....':'H','..':'I','.---':'J','-.-':'K','.-..':'L','--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q','.-.':'R','...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X','-.--':'Y','--..':'Z'}
    if '.' not in text and '-' not in text:return None
    try:return ' '.join(''.join(M[x] for x in w.split()) for w in text.split('/'))
    except:return None

def rail_fence_decode(text,rails):
    if rails<=1 or rails>=len(text):return text
    pattern=[];row=0;d=1
    for _ in text:
        pattern.append(row)
        if row==0:d=1
        elif row==rails-1:d=-1
        row+=d
    counts=[pattern.count(i) for i in range(rails)];rows=[];p=0
    for n in counts:rows.append(list(text[p:p+n]));p+=n
    ptr=[0]*rails;out=[]
    for r in pattern:out.append(rows[r][ptr[r]]);ptr[r]+=1
    return ''.join(out)

VIGENERE_KEYS=['KEY','CODE','CIPHER','SECRET','PASSWORD','HELLO','WORLD','MESSAGE','DECODE','CRYPTO','ENIGMA','PYTHON']
AFFINE_A_VALUES=[a for a in range(26) if math.gcd(a,26)==1]

def build_fast_methods():
    m=[(f'Caesar shift {s}',lambda t,s=s:caesar(t,s)) for s in range(26)]
    m += [('Atbash',atbash),('ROT13',rot13),('ROT47',rot47),('Reverse',reverse),('Reverse words',reverse_words),('Reverse each word',reverse_each_word),('Keyboard left',lambda t:keyboard_shift(t,-1)),('Keyboard right',lambda t:keyboard_shift(t,1)),('ASCII numbers',lambda t:numbers_to_ascii(t)),('A1Z26',a1z26),('Binary',binary_decode),('Hex',hex_decode),('Base64',base64_decode),('Morse',morse_decode)]
    for r in range(2,12):m.append((f'Rail Fence decode {r}',lambda t,r=r:rail_fence_decode(t,r)))
    for k in VIGENERE_KEYS:m += [(f'Vigenere key={k}',lambda t,k=k:vigenere(t,k)),(f'Beaufort key={k}',lambda t,k=k:beaufort(t,k))]
    for a in AFFINE_A_VALUES:
        for b in range(26):m.append((f'Affine a={a} b={b}',lambda t,a=a,b=b:affine_decode(t,a,b)))
    return m

def build_combo_methods():
    bases=[('Reverse',reverse),('Atbash',atbash),('ROT13',rot13),('Keyboard left',lambda t:keyboard_shift(t,-1)),('Keyboard right',lambda t:keyboard_shift(t,1))]
    return [(f'{n} -> Caesar {s}',lambda t,f=f,s=s:caesar(f(t),s)) for n,f in bases for s in range(26)]

def run_methods(text,methods):
    start=time.time();total=len(methods)
    for i,(name,fn) in enumerate(methods,1):
        try:
            out=fn(text)
            if out is not None:add_result(name,out)
        except Exception:pass
        pct=i/total*100;filled=int(40*i/total)
        print(f'\r[{'#'*filled}{'-'*(40-filled)}] {pct:6.2f}% | {i}/{total}',end='',flush=True)
    print();return time.time()-start

def save_report(ciphertext,total_methods,elapsed):
    filename=f"decipher_results_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)
    ranked=sorted(results,key=lambda r:r.score,reverse=True)
    with open(path,'w',encoding='utf-8') as f:
        f.write('='*80+'\nDECIPHER-X v2\n'+'='*80+'\n\nORIGINAL CIPHERTEXT:\n'+ciphertext+'\n\n')
        for i,r in enumerate(ranked,start=1):f.write(f'\n[{i}] score {r.score:6.1f} | {r.method}\n'+'-'*80+'\n'+r.text+'\n')
    return path,ranked

def main():
    global results;results=[]
    print('='*80+'\n                         DECIPHER-X v2\n'+'='*80)
    ciphertext=input('Enter ciphertext:\n> ')
    if not ciphertext.strip():return
    methods=build_fast_methods()+build_combo_methods()
    print(f'Loaded {len(methods)} direct methods.')
    elapsed=run_methods(ciphertext,methods)
    path,ranked=save_report(ciphertext,len(methods),elapsed)
    print('\nTOP 10 MOST LIKELY PLAINTEXTS')
    for i,r in enumerate(ranked[:10],1):print(f'#{i} [{r.score:6.1f}] {r.method}\n    {r.text[:120]}')
    print(f'\nFull report saved to: {path}')

if __name__=='__main__':main()
