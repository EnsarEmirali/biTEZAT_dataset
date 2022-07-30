
#IMPORT PACKAGES---------------------------------------------------------------
from model.parameters import *
import glob
from collections import Counter
import re
import unicodedata
import pandas as pd


#PREPARE SENTENCES-------------------------------------------------------------
def __sentence_preprocess(s):
    """
    Cümlede bulunan anormal karakterler düzeltilir.
    Cümledeki fazladan bulunan boşluklar silinir.
    Yanlış şekilde bulunan Türkçe karakterler düzeltilir.
    
    Parameters
    ----------
    s : str
        cümlenin kendisi.

    Returns
    -------
    s : str
        düzenlenmiş halde cümle.
    """
    s = s.replace('&#160',' ').replace('&apos;','\'').replace('&quot;','"').replace('&gt;',' ').replace('&amp;','&').replace('®','').strip()
    s = s.replace("’", "'").replace("‘", "'").replace("”", "'").replace("“", "'")
    s = s.replace('</','<')
    # s = re.sub('(?=[a-zA-ZçğşıöüÇĞŞİÖÜ0-9\.:]*)<',' <',s)
    # s = re.sub('>(?=[a-zA-ZçğşıöüÇĞŞİÖÜ0-9\.:]*)','> ',s)
    # s = re.sub("\s*'\s*","'",s)
    s = re.sub("\s*:\s*",":",s)
    s = re.sub(' {2,}', ' ',s)
    s = s.replace('"',"'")
    s = re.sub("\'{2,}", "\'",s)
    
    s = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    
    return s.strip()


def __sentence_bound(file_body, sentence_extractor):
    """
    Paragrapfların cümlelere bölünmesi

    Parameters
    ----------
    file_body : str
        DESCRIPTION.
    sentence_extractor : zemberek.sentence_extractor
        paragrafı cümlelere bölmek için zemberek fonksiyonu.

    Returns
    -------
    sentences : List
        cümleler.
    """
    sentences = sentence_extractor.fromParagraph(file_body)
    return [str(s) for s in sentences]


def __label_list(s):
    """
    Cümle içerisinde bulunan etiketlerin bulunduğu konumların belirlenmesi

    Parameters
    ----------
    s : str
        etiketli cümle.

    Returns
    -------
    index_list : List
        etiketler ve konumlarının listesi.
    """
    p = re.compile(LABEL_PATTERN)
    
    #start_index, end_index, length, label
    index_list = [[m.start(), m.end(), m.end() - m.start(), re.sub('[\<\>]','',m.group())] for m in p.finditer(s)]
    return index_list


def load_sentence(files_path, file_extent, sentence_extractor, extract_sentence=False):
    """
    file_extent formatında bulunan cümlelerin files_path dizininden düzeltilerek bir dataframe halinde yüklenmesi
    
    Parameters
    ----------
    files_path : str
        cümlelerin bulunduğu klasörün adresi.
    file_extent : str
        içeri aktarılacak dosyaların uzantısı.
    extract_sentence : boolean
        metinlerin cümlelere bölünüp bölünmeyeceği

    Returns
    -------
    files_df : DataFrame
        dataframe halinde cümleler.
    """
    files_list = glob.glob(files_path+'/*.'+file_extent)
    
    files_df = pd.DataFrame(columns = ['file_ix', 'file_body'])
    for file in files_list: 
        with open(file, 'r', encoding='utf-8-sig') as f:
            line = f.read()
            line = line.replace('\n', ' ')
            files_df = files_df.append({'file_ix' : int(re.findall('\d+',file)[0]) #dosya isminden cümle IDsinin çıkarılması
                                        ,'file_body' : __sentence_preprocess(line) #etiketlenmiş haliyle cümlenin kendisi
                                        }
                                       ,ignore_index = True)
    
    files_df.sort_values(by='file_ix', inplace=True)
    files_df.reset_index(drop=True, inplace=True)

    if extract_sentence:
        files_df['sentence'] = files_df['file_body'].apply(lambda x: __sentence_bound(x, sentence_extractor))
        files_df = files_df.explode('sentence')
        files_df.reset_index(drop=True, inplace=True)
        files_df['sentence_ix'] = files_df.groupby('file_ix')['sentence'].cumcount()+1
        files_df['index_list'] = files_df['sentence'].map(__label_list)

        # Eğer cümle üzerinde çalışacak isek training aşamasında yanlış bölünen cümleleri sileceğiz,
        # çünkü bu cümleler maalesef yanlış etiketlemeye sebep oluyor.
        files_df['filt'] = files_df['index_list'].map(len)
        files_df['filt'] = files_df['filt']%2
        files_df = files_df[files_df['filt']==0]
        
        files_df['pure'] = files_df['sentence'].apply(lambda x: len(re.sub('[^\d\w]','',x)))
        files_df = files_df[files_df['pure']>0]
        
        files_df.drop(columns=['index_list','filt','pure'], inplace=True)

    else:
        files_df['sentence'] = files_df['file_body']
        files_df['sentence_ix'] = files_df.groupby('file_ix')['sentence'].cumcount()+1

    files_df['unqiue_ID'] = files_df.apply(lambda x: x['file_ix']*1000+x['sentence_ix'], axis=1)
    
    return files_df


def labeled2unlabeled(s):
    """
    Etiketli cümleden etiketlerin silinmesi

    Parameters
    ----------
    s : str
        etiketli cümle.

    Returns
    -------
    s : str
        etiketsiz cümle.
    """
    s = re.sub(LABEL_PATTERN,'',s).strip()
    s = re.sub(' {2,}', ' ',s)
    return s


#TOKENIZATION AND MORPHOLOGICAL ANALYZER---------------------------------------
def __label_index(s):
    """
    Etiketli cümle içerisindeki etiketlerin başlagıç ve bitiş indekslerinin etiketsiz haline göre belirlenmesi
    
    Parameters
    ----------
    s : str
        etiketli cümle.

    Returns
    -------
    last_list : List
        cümle içerisinde başlangıç ve bitiş indeksleriyle etiketler.
    """
    index_list = __label_list(s)
    
    if len(index_list)>1:
        last_list = [[index_list[0][0],index_list[1][0]-index_list[0][2]-1,index_list[0][3]]]
        l = index_list[0][2]+index_list[1][2]
        for i in range(1,int(len(index_list)/2)):
            last_list.append([index_list[2*i][0]-l, #etiketin baslangıc indeksi
                              index_list[2*i+1][0]-l-index_list[2*i][2]-1, #etiketin bitis indeksi
                              index_list[2*i][3] #etiket
                              ])
            l = l+index_list[2*i][2]+index_list[2*i+1][2]
        return last_list
    else:
        return []


def tokenizer_morphologizer(s, tokenizer, morphologizer, converter):
    """
    Cümlede yer alan kelimelerin özelliklerinin listelenmesi
    Modelin eğitilmesi için etiket listesi girilmesi gerekir.
    Model tahmini için etiket listesi gerekmemektedir.
    
    Parameters
    ----------
    s : str
        cümle.
    tokenizer : zemberek.tokenizer
        cümleyi kelimelere ayırmak için zemberek fonksiyonu.
    morphologizer : zemberek.morphologizer
        cümledeki kelimelerin biçimbilimsel analizi yapmak için zemberek fonksiyonu.
    converter : zemberek.converter
        cümlede yanlış yazımlı kelimeleri düzeltmek için zemberek fonksiyonu.

    Returns
    -------
    ss : Dict
        cümledeki kelimelerin özelliklerini içeren sözlük:
            token: kelimenin kendisi
            token_type: kelimenin tipi
            morph_analysis: kelimenin biçimbilimsel analizi
            morph_token: biçimbilimsel analiz için kelimenin düzenlenmiş hali
            morph_lemma: düzenlenmiş kelimenin kökü
            morph_type: düzenlenmiş kelimenin tipi
            token_label: kelimenin etiketi
    """
    sent = labeled2unlabeled(s)
    labels = __label_index(s)
    
    if len(s)>0:
        st = [[str(token.getText()),str(token.getType()),int(token.getStart()),int(token.getEnd())] for token in tokenizer.tokenize(sent)]
        sm = [str(converter.convert(morp.surfaceForm(),morp)) for morp in morphologizer.analyzeAndDisambiguate(sent).bestAnalysis()]
    
        ss = []
        for i,j in zip(st,sm):
            ss.append({'token' : i[0]
                       ,'token_type' : i[1]
                       # ,'token_start' : i[2]
                       # ,'token_end' : i[3]
                       ,'morph_analysis' : j.split()[1]
                       ,'morph_token' : j.split('-')[0]
                       ,'morph_lemma' : re.findall( r'\[(.*?):', j)[0]
                       ,'morph_type' : re.findall( r':(.*?)\]', j)[0]
                       ,'token_label' : ''.join(x[2] for x in labels if x[0]<=i[2] and x[1]>=i[3]) #if len(labels)>0 else ''
                       })
        return ss


#FEATURE LISTS-----------------------------------------------------------------
def __normalize_token(w):
    """
    feature_list fonksiyonunda kullanılır.
    Kelime vektörlerinde daha fazla kelimeye ulaşabilmek için kelimeler belli formatta düzeltilir:
        Kelimedeki harfler küçültülür.
        Numaralar sıfır ile değiştirilir.
        # Kelimede yer alan ve tarih bildirmeyen sayılar sıfırlanır.
        # Tarih ifadeleri 01.01.2010 ile değiştirilir (fasttext ve glove vektörlerinde bu tarih yer alıyor).

    Parameters
    ----------
    w : str
        kelime.

    Returns
    -------
    w : str
        kelimenin düzeltilmiş hali.
    """
    w = w.lower()
    w = re.sub('\d', '0', w)
    
    # punc = '[\.\-\/]+'
    # p = DAYS+punc+MONTHS+punc+YEARS
    # p = re.compile(p)
    # w = re.sub(p, 'DD.DD.DDDD', w)
    
    # p = MONTHS+punc+DAYS+punc+YEARS
    # p = re.compile(p)
    # w = re.sub(p, 'DD.DD.DDDD', w)
    
    # p = YEARS+punc+MONTHS+punc+DAYS
    # p = re.compile(p)
    # w = re.sub(p, 'DD.DD.DDDD', w)
    
    # p = YEARS+punc+DAYS+punc+MONTHS
    # p = re.compile(p)
    # w = re.sub(p, 'DD.DD.DDDD', w)
    
    # p = DAYS+punc+MONTHS+punc+YEARS2
    # p = re.compile(p)
    # w = re.sub(p, 'DD.DD.DDDD', w)
    
    # p = MONTHS+punc+DAYS+punc+YEARS2
    # p = re.compile(p)
    # w = re.sub(p, 'DD.DD.DDDD', w)
    
    # p = YEARS2+punc+MONTHS+punc+DAYS
    # p = re.compile(p)
    # w = re.sub(p, 'DD.DD.DDDD', w)
    
    # p = YEARS2+punc+DAYS+punc+MONTHS
    # p = re.compile(p)
    # w = re.sub(p, 'DD.DD.DDDD', w)
    
    # w = re.sub('^\d+[\.\,\/]+\d+$', '0', w)
    # w = re.sub('DD.DD.DDDD', '01.01.2010', w)
    # # w = re.sub('\d{2}[\.\-\/]\d{2}[\.\-\/]\d{2}', '01.01.2010', w)
    # # w = re.sub('\d{2}[\.\-\/]\d{2}[\.\-\/]\d{4,}', '01.01.2010', w)
    # # w = re.sub('\d{4}[\.\-\/]\d{2}[\.\-\/]\d{2}', '01.01.2010', w)
    # # w = re.sub('\d{5,8}', '0', w)
    # # w = re.sub('\d{9,}', '0', w)
    # # w = re.sub('^\d+[\.\,\/]+\d+$', '0', w)
    
    return w


def __morph_pattern(w, root=False):
    """
    Biçimbilimsel analiz sonucunun listelenmesi

    Parameters
    ----------
    w : str
        biçimbilimsel analiz sonucu.
    root : boolean
        listeye kelime kökünün analiz sonucunun da eklenip eklenmemesi.

    Returns
    -------
    wl : List
        liste halinde biçimbilimsel analiz sonucu.
    """
    if root:
        i = re.split('\+|\→|\|', w)[0]
        wl = [i.split(':')[0] if ':' in i else '']
        w = re.split('\+|\→|\|', w)
        wl += [i.split(':')[1] if ':' in i else i for i in w if len(w)>0]
    else:
        # wl = re.split('\+|\→|\|', w)[1:]
        wl = re.split('\+|\→|\|', w)
        wl = [i.split(':')[1] if ':' in i else i for i in wl if len(wl)>0]
    return wl


def __orth_char_list(w):
    """
    Kelime karakterler, yazımsal olarak kodlanır:
        büyük harfler -> C
        küçük harfler -> c
        rakamlar -> n
        işaretlemeler -> p
        yukarıdakilerin dışındakiler -> x

    Parameters
    ----------
    w : str
        kelime.

    Returns
    -------
    w : str
        kodlanmış kelime.
    """
    w = re.sub('[A-ZIİÖÜÇŞĞ]', 'C', w)
    w = re.sub('[a-zıiöüçşğâ]', 'c', w)
    w = re.sub('[0-9]', 'n', w)
    w = re.sub('[!\?()\[\]{}\.\,\;\:\_\-\*\'\"\/\\\|<>@#$%\^&%~+-=₺]', 'p', w)
    w = re.sub(' ', 's', w)
    w = re.sub('[^Ccnps]', 'x', w)
    w = re.sub('s', ' ', w)
    return w


def feature_list(s, feature, char_opt=False, morph_opt=False):
    """
    tokenizer_morphologizer çıktısı olan her bir özelliğin liste haline getirilmesi
    Cümlede yer alan işaretlemeler hariç tutulur.

    Parameters
    ----------
    s : str
        tokenizer_morphologizer çıktısı.
    feature : str
        tokenizer_morphologizer çıktısı olan sözlükte yer alan ve listelenecek özellik.
    char : boolean
        listelenmek özelliğin karakter bazlı listelenip listelenmemesi
    opt : boolean
        kullanılacak fonksiyondaki boolean değer

    Returns
    -------
    wl : List
        liste halinde özellik.
    """
    wl = [w if w['token_type'] != 'Punctuation' else '' for w in s]
    wl = list(filter(None, wl))
    
    if feature == 'morph_analysis':
        wl = [__morph_pattern(w['morph_analysis'], morph_opt) for w in wl]
    
    elif feature == 'morph_token':
        wl = [__normalize_token(w['morph_token']) for w in wl]
    
    elif feature == 'orth_token':
        wl = [__orth_char_list(w['token']) for w in wl]
    
    else:
        wl = [w[feature] for w in wl]    
    
    if char_opt:
        cl = []
        for c in wl:
            cl.append(list(c))
        return cl
    else:
        return wl


#ITEM DICTIONARIES-------------------------------------------------------------
def item_mapping(df, field, freq=0):
    """
    Tekrar sıklıklarına göre öğeleri sıralayıp sözlük haline getirir.
    Özel değerler:
        PAD_TOKEN: uzunluk tamamlamada kullanılacak öğe
        OOV_TOKEN: sözlükte yer almayan değerler için kullanılacak öğe
        start: başlangıç öğesi
        end: bitiş öğesi
    
    Parameters
    ----------
    df : DataFrame
        öğelerin bulunduğu dataframe.
    field : str
        öğelerin dataframede bulunduğu sütun ismi.
    freq : int
        değerin en az kaç defa olması gerektiği.

    Returns
    -------
    index2item : Dict
        ID bazlı sözlük.
    item2index : Dict
        Öğe bazlı sözlük.
    """
    if any(isinstance(i, list) for i in df[field][0]):
        item_list = [item for i in df[field] for it in i for item in it if len(item)>0]
    else:
        item_list = [item for i in df[field] for item in i if len(item)>0]
    item2dict = Counter(item_list)
    item2dict = dict(filter(lambda x: x[1] > freq, item2dict.items()))
    
    item2dict[PAD_TOKEN] = NOWAY+1
    item2dict[OOV_TOKEN] = NOWAY
    item2dict[START_TOKEN] = -1
    item2dict[END_TOKEN] = -2
    
    sorted_items = sorted(item2dict.items(), key=lambda x: (-x[1], x[0]))
    index2item = {i: v[0] for i, v in enumerate(sorted_items)}
    item2index = {v: k for k, v in index2item.items()}
    return item2dict, index2item, item2index


def token_index_pad(wl, item2index, max_len=300):
    """
    Özelliğin değerlerinin sözlükteki indeks değerlerini getirir.   

    Parameters
    ----------
    wl : List
        değer listesi.
    item2index : Dict
        değer sözlüğü.
    max_len : int
        eşitlenmek istenilen toplam kelime sayısı.
    
    Returns
    -------
    item_list : List
        değerlerin indeks listesi.
    """
    oov_index = item2index[OOV_TOKEN]
    pad_index = item2index[PAD_TOKEN]

    max_len = max_len if max_len>0 else len(wl)
    item_list = [item2index.get(item, oov_index) for item in wl[:max_len]]
    item_list.extend([pad_index] * max((max_len - len(item_list)),0))
    
    return item_list


def char_index_pad(wl, item2index, max_len=300, max_char_len=30):
    """
    Özelliğin değerlerinin sözlükteki indeks değerlerini getirir.    

    Parameters
    ----------
    wl : List
        değer listesi.
    item2index : Dict
        değer sözlüğü.
    max_len : int
        eşitlenmek istenilen toplam kelime sayısı.
    max_len : int
        eşitlenmek istenilen toplam karakter sayısı.

    Returns
    -------
    item_list : List
        değerlerin indeks listesi.
    """
    oov_index = item2index[OOV_TOKEN]
    pad_index = item2index[PAD_TOKEN]
    
    max_len = max_len if max_len>0 else len(wl)
    item_list = []
    
    for wlw in wl[:max_len]:
        sublist = [item2index.get(item, oov_index) for item in wlw[:max_char_len]]
        sublist.extend([pad_index] * max((max_char_len - len(sublist)),0))
        item_list.append(sublist)
    
    ext_pad = [pad_index] * max_char_len
    
    for i in range(max((max_len - len(item_list)),0)):
        item_list.append(ext_pad)

    return item_list


def exclude_pad_index(wl, item2index):
    pad_index = item2index[PAD_TOKEN]
    pad_len = wl.index(pad_index) if pad_index in wl else len(wl)
    return wl[:pad_len]


#SPELLING FEATURES: USE FOR CRF------------------------------------------------
def __ispunct(w):
    if all(i in PUNCTS for i in w): return True
    else: return False

def __isdigitpunc(w):
    if all(i in PUNCTS_DIGITS for i in w): return True
    else: return False

def __isalphpunct(w):
    if any(i in PUNCTS for i in w) and all(i not in DIGITS for i in w): return True
    else: return False

def __isalphdigitpunc(w):
    if any(i in PUNCTS for i in w) and any(i in DIGITS for i in w) and any(i not in PUNCTS_DIGITS for i in w): return True
    else: return False

def __numbervalue(w):
    w = re.sub('[^\d\.\,]', '', w)
    w = re.split('\.|\,', w.strip())
    w = list(filter(None, w))
    l = []
    for i in w:
         i = int(i)
         if i >= 0 and i <=12: l.append(1)
         elif i >= 13 and i <=31: l.append(2)
         elif i >= 32 and i <=60: l.append(3)
         elif i >= 61 and i <=1989: l.append(5)
         elif i >= 1990 and i <=2020: l.append(4)
         else: l.append(5)

    if len(l)>0: return int(''.join(str(j) for j in l[::-1]))
    else: return 0

def __has_term(x):
    terms = ['saniye','sanıye','dakika','dakıka','saat','gün','gun','hafta','ay','yıl','yil','yüzyıl','yüzyil','yuzyıl','yuzyil']
    if any(t in x for t in terms): return 1
    else: return 0
    
    
def spell_features(wl):
    """
    Kelimenin yazım özelliklerinin listelenmesi

    Parameters
    ----------
    wl : List
        cümlede yer alan kelimelerin listesi.

    Returns
    -------
    spell_list : List
        kelimelerin özellikleri.
    """
    spell_list = []
    
    for w in wl:
        is_alph = 1  if w.isalpha() else 0 # whether is all characters
        is_digit = 1 if w.isdigit() else 0 # whether is all digits
        is_punc = 1 if __ispunct(w) else 0 # whether all punctuations
        
        is_alphdigit = 1 if not w.isalpha() and not w.isdigit() and w.isalnum() else 0 # whether is mix with letters and digits
        is_alphpunct = 1 if not __isdigitpunc(w) and __isalphpunct(w) else 0 # whether is mix with letters and punctuation
        is_digitpunc = 1 if not w.isdigit() and not __ispunct(w) and __isdigitpunc(w) else 0 # whether is mix with digits and punctuation
        is_alphdigitpunc = 1 if __isalphdigitpunc(w) else 0 # whether is mix with letters, digits and punctuation
    
        is_title = 1 if w.istitle() else 0 # whether start with a capital letter
        is_upper = 1 if w.isupper() else 0 # whether has all uppercase letters
        is_lower = 1 if w.islower() else 0 # whether has all lowercase letters
        number_value = __numbervalue(w) # numeric value: 1 ofr 1-12, 2 for 13-31, 3 for 31-60, 4 for 60-2020, 5 for other integers
        has_term = __has_term(w) # whether has time term; saniye, dakika, saat, gün, hafta, ay, yıl, yüzyıl
        has_colon = 1 if ':' in w else 0 # whether has punctuations :
        has_hyphen = 1 if '-' in w else 0 # whether has punctuations -
        has_period = 1 if '.' in w else 0 # whether has punctuations .
        
        spell_list.append([is_alph,is_digit,is_punc,is_alphdigit,is_alphpunct,is_digitpunc,is_alphdigitpunc,is_title,is_upper,is_lower,number_value,has_term,has_colon,has_hyphen,has_period])
        
    return spell_list
