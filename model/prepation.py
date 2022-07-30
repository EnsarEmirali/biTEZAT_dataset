import os
import pickle
from pathlib import Path
import jpype as jp

os.chdir('PATH THAT INCLUDES KEEP FILES/FOLDERS YOU HAVE DOWNLOADED YET')

from model.parameters import *
from model.utils import *

# -----------------------------------------------------------------------------

def zemberek_init():
    """
    Zemberek.jar dosyasının başlatılması
    """
    if jp.isJVMStarted():
        return
    jp.startJVM(jp.getDefaultJVMPath(), '-ea', '-Djava.class.path=%s' % ('zemberek/zemberek-full.jar'))

zemberek_init()
zemberek = {}

TurkishTokenizer = jp.JClass('zemberek.tokenization.TurkishTokenizer')
Token = jp.JClass('zemberek.tokenization.Token')
zemberek['tokenizer'] = TurkishTokenizer.DEFAULT

TurkishMorphology = jp.JClass('zemberek.morphology.TurkishMorphology')
RootLexicon = jp.JClass('zemberek.morphology.lexicon.RootLexicon')
AnalysisFormatters = jp.JClass('zemberek.morphology.analysis.AnalysisFormatters')
zemberek['morphologizer'] = TurkishMorphology.builder().setLexicon(RootLexicon.getDefault()).ignoreDiacriticsInAnalysis().useInformalAnalysis().build()

InformalAnalysisConverter = jp.JClass('zemberek.morphology.analysis.InformalAnalysisConverter')
zemberek['converter'] = InformalAnalysisConverter(zemberek['morphologizer'].getWordGenerator())

TurkishSentenceNormalizer = jp.JClass('zemberek.normalization.TurkishSentenceNormalizer')
zemberek['lookupRoot'] = Path('zemberek/normalization')
zemberek['lmFile'] = Path('zemberek/lm/lm.2gram.slm')
zemberek['norm_morphology'] = TurkishMorphology.createWithDefaults()
zemberek['normalizer'] = TurkishSentenceNormalizer(zemberek['norm_morphology'], zemberek['lookupRoot'], zemberek['lmFile'])

TurkishSentenceExtractor = jp.JClass('zemberek.tokenization.TurkishSentenceExtractor')
zemberek['sentence_extractor'] = TurkishSentenceExtractor.DEFAULT


# -----------------------------------------------------------------------------

from model.preprocess import *

files_df = load_sentence(FILES_PATH, 
                         FILE_EXTENT, 
                         extract_sentence=False,
                         sentence_extractor=zemberek['sentence_extractor'])

files_df['tokenized_morphologized'] = files_df['sentence'].apply(lambda x: tokenizer_morphologizer(x, 
                                                                                                   tokenizer=zemberek['tokenizer'], 
                                                                                                   morphologizer=zemberek['morphologizer'], 
                                                                                                   converter=zemberek['converter']))


files_df['label_list']           = files_df['tokenized_morphologized'].apply(lambda x: feature_list(x, 'token_label'))
files_df['word_list']            = files_df['tokenized_morphologized'].apply(lambda x: feature_list(x, 'token'))
files_df['normalized_word_list'] = files_df['tokenized_morphologized'].apply(lambda x: feature_list(x, 'morph_token')) 
files_df['char_list']            = files_df['tokenized_morphologized'].apply(lambda x: feature_list(x, 'token', char_opt=True))
files_df['orth_list']            = files_df['tokenized_morphologized'].apply(lambda x: feature_list(x, 'orth_token', char_opt=True))
files_df['morphWR_list']         = files_df['tokenized_morphologized'].apply(lambda x: feature_list(x, 'morph_analysis', morph_opt=True))
files_df['morphWOR_list']        = files_df['tokenized_morphologized'].apply(lambda x: feature_list(x, 'morph_analysis'))
files_df['spelling_list']        = files_df['word_list'].map(spell_features)


_,         index2label, label2index = item_mapping(files_df, field='label_list')
word2dict, _,           word2index  = item_mapping(files_df, field='normalized_word_list')
_,         _,           char2index  = item_mapping(files_df, field='char_list')
_,         _,           orth2index  = item_mapping(files_df, field='orth_list')
_,         _,           morph2index = item_mapping(files_df, field='morphWOR_list', freq=3)


files_df['label_index']    = files_df['label_list'].apply(lambda x:            token_index_pad(x, label2index,         max_len=WORD_PAD_LEN))
files_df['word_index']     = files_df['normalized_word_list'].apply(lambda x:  token_index_pad(x, word2index,          max_len=WORD_PAD_LEN))
files_df['char_index']     = files_df['char_list'].apply(lambda x:             char_index_pad(x,  char2index,          max_len=WORD_PAD_LEN, max_char_len=CHAR_PAD_LEN))
files_df['orth_index']     = files_df['orth_list'].apply(lambda x:             char_index_pad(x,  orth2index,          max_len=WORD_PAD_LEN, max_char_len=CHAR_PAD_LEN))
files_df['morph_index']    = files_df['morphWOR_list'].apply(lambda x:         char_index_pad(x,  morph2index,         max_len=WORD_PAD_LEN, max_char_len=MORPH_PAD_LEN))
files_df['spelling_index'] = files_df['spelling_list'].apply(lambda x:         char_index_pad(x,  SPELL2INDEX,         max_len=WORD_PAD_LEN, max_char_len=SPELL_PAD_LEN))

pickle.dump(files_df, open('files_df.pkl', 'wb'))
