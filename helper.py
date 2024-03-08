import sys

def endEN(t, n) :
    return t + n

def rLMxL(t, n):
    return t < n

def VHtgA (t, n) :
    return t % n


def dec2(t, n) :
    o=[]
    s=[]
    u=0
    h=''
    for e in range(256):
        s.append(e)

    for e in range(256):
        u = endEN(u + s[e],ord(t[e % len(t)])) % 256
        o = s[e];
        s[e] = s[u];
        s[u] = o;
    e=0
    u=0
    c=0
    for c in range(len(n)):
        e = (e + 1) % 256
        o = s[e]
        u = VHtgA(u + s[e], 256)
        s[e] = s[u];
        s[u] = o;
        try:
            h += chr((n[c]) ^ s[(s[e] + s[u]) % 256]);
        except:
            h += chr(ord(n[c]) ^ s[(s[e] + s[u]) % 256]);
    return h

import base64
STANDARD_ALPHABET = CUSTOM_ALPHABET =  b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
ENCODE_TRANS = bytes.maketrans(STANDARD_ALPHABET, CUSTOM_ALPHABET)
DECODE_TRANS = bytes.maketrans(CUSTOM_ALPHABET, STANDARD_ALPHABET)

def encode2(input):
	return base64.b64encode(input).translate(ENCODE_TRANS)

def getVerid(id):
    def convert_func(matchobj):
        m =  matchobj.group(0)
    
        if m <= 'Z':
            mx = 90
        else:
            mx = 122
        mx2 = ord( m)+ 13  
        if mx>=mx2:
            mx = mx2
        else:
            mx = mx2-26
        gg = chr(mx)
        return gg
    
    
    def but(t):
    
        o=''
        for s in range(len(t)):
            u = ord(t[s]) 
            if u==0:
                u=0
            else:
                if s%8 ==2:
                    u -= 2
                else:
                    if (s % 8 == 4 or s % 8 == 7):
                        u += 2
                    else:
                        if s % 8 == 0 :
                            u += 4
                        else:
                            if (s % 8 == 5 or s % 8 == 6):
                                u -= 4
                            else:
                                if (s % 8 == 1):
                                    u += 3
                                else:
                                    if (s % 8 == 3):
                                        u += 5
    
            o += chr(u)
                    
    
    
        if sys.version_info >= (3,0,0):
            o=o.encode('Latin_1')
    
        if sys.version_info >= (3,0,0):
            o=(o.decode('utf-8'))
    
        return o
    ab = 'DZmuZuXqa9O0z3b7' #####stare
    ab = 'MPPBJLgFwShfqIBx'
    ab = 'rzyKmquwICPaYFkU'
    ab = 'FWsfu0KQd9vxYGNB'
    
    ab = 'Ij4aiaQXgluXQRs6'

    hj = dec2(ab,id) 
    if sys.version_info >= (3,0,0):
        hj=hj.encode('Latin_1')  
    id = encode2(hj)
    
    if sys.version_info >= (3,0,0):
        id = id.decode('utf-8')
    id = id.replace('/','_').replace('+','-')
    
    if sys.version_info >= (3,0,0):
        id = id.encode('Latin_1')  
        
    id = encode2(id)    
    if sys.version_info >= (3,0,0):
        id = id.decode('utf-8')
    id = id.replace('/','_').replace('+','-')   

    if sys.version_info >= (3,0,0):
        id=(''.join(reversed(id)))
        id = id.encode('Latin_1') 
    else:
        id=(''.join((id)[::-1]))
    id = encode2(id)
    if sys.version_info >= (3,0,0):
        id = id.decode('utf-8')
    id = id.replace('/','_').replace('+','-')
    
    
    xc= but(id) 
    
    return xc

from urllib.parse import unquote

def DecodeLink(mainurl):
	mainurl = mainurl.replace('_', '/').replace('-', '+')
	#
	ab=mainurl[0:6]
	ab= 'hlPeNwkncH0fq9so'
	ab = '8z5Ag5wgagfsOuhz'
	
	ac= decode2(mainurl)
	
	link = dekoduj(ab,ac)
	link = unquote(link)
	return link


def dekoduj(r,o):

    t = []
    e = []
    n = 0
    a = ""
    for f in range(256): 
        e.append(f)

    for f in range(256):

        n = (n + e[f] + ord(r[f % len(r)])) % 256
        t = e[f]
        e[f] = e[n]
        e[n] = t

    f = 0
    n = 0
    for h in range(len(o)):
        f = f + 1
        n = (n + e[f % 256]) % 256
        if not f in e:
            f = 0
            t = e[f]
            e[f] = e[n]
            e[n] = t

            a += chr(ord(o[h]) ^ e[(e[f] + e[n]) % 256])
        else:
            t = e[f]
            e[f] = e[n]
            e[n] = t
            if sys.version_info >= (3,0,0):
                a += chr((o[h]) ^ e[(e[f] + e[n]) % 256])
            else:
                a += chr(ord(o[h]) ^ e[(e[f] + e[n]) % 256])

    return a


def decode2(input):
	try:	
		xx= input.translate(DECODE_TRANS)
	except:
		xx= str(input).translate(DECODE_TRANS)
	return base64.b64decode(xx)
