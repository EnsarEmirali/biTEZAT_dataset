
#IMPORT PACKAGES---------------------------------------------------------------
import numpy as np
import torch


#VRANDOM SEEDS-----------------------------------------------------------------
np.random.seed(42)
torch.manual_seed(42)


#STATIC VALUES-----------------------------------------------------------------
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


CHARS = 'âabcçdefgğhıijklmnoöpqrsştuüvwxyzABCÇDEFGĞHIİJKLMNOÖPQRSŞTUÜVWXYZ'
PUNCTS = '!?()[]{}.,;:_-*\'"/\\|<>@#$%^&%~+-=₺'
DIGITS = '0123456789'
PUNCTS_DIGITS = PUNCTS + DIGITS


DAYS = "(1|2|3|4|5|6|7|8|9|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31){1}"
MONTHS = "(1|2|3|4|5|6|7|8|9|01|02|03|04|05|06|07|08|09|10|11|12){1}"
YEARS = "(1990|1991|1992|1993|1994|1995|1996|1997|1998|1999|2000|2001|2002|2003|2004|2005|2006|2007|2008|2009|2010|2011|2012|2013|2014|2015|2016|2017|2018|2019|2020|2021|2022|2023|2024|2025|2026|2027|2028|2029|2030){1}.*"
YEARS2 = "(90|91|92|93|94|95|96|97|98|99|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30){1}"


LABELS = ['DATE', 'TIME', 'DURATION', 'SET']
LABEL_PATTERN = '<['+'|'.join(LABELS)+']+>'


START_TOKEN = '<start>'
END_TOKEN = '<end>'
OOV_TOKEN = '<unk>'
PAD_TOKEN = '<pad>'
SPELL2INDEX= {0: 0,
              1 : 1,
              OOV_TOKEN : 2, 
              PAD_TOKEN:0}


#FILES PATH AND EXTENSION------------------------------------------------------
FILES_PATH = 'dataset'
FILE_EXTENT= 'xml'


#VALUES FOR DICTIONARIES AND PADDING-------------------------------------------
WORD_PAD_LEN = 300
CHAR_PAD_LEN = 30
MORPH_PAD_LEN = 20
SPELL_PAD_LEN = 15
NOWAY = 1000000
