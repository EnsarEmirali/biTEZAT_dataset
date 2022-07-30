# bi-TEZAT: Dataset

**"bi-TEZAT: biLSTM YÖNTEMİYLE TÜRKÇE ŞİKAYET METİNLERİNDE ZAMAN İFADELERİNİN TESPİT EDİLMESİ"** yüksek lisans tez çalışması kapsamında TIMEX3 standartlarında zaman ifadeleri etiketlenmiş Türkçe şikayet metinlerini içermektedir.

Klasörler ve dosyaların detayları aşağıda belirtilmiştir:

- ***scrapping.py:*** İnternet ortamından şikayetleri indirmek için yazılan Python kodu
- ***labeled_dataset:*** İnternet ortamında indirilen ve etiketlenen 500 şikayet metni
- ***unlabeled_dataset:*** İnternet ortamında indirilen ve etiketlenmemiş 127 şikayet metni
- ***model:*** Şikayet metinlerini düzenlemek için Python kodları:
- - ***parameters.py:*** Ön işlemler sırasında ihtiyaç olan parametrelerin saklandığı dosya
- - ***preprocess.py:*** Ön işlemler sırasında ihtiyaç olan fonksiyonların saklandığı dosya
- - ***preparation.py:*** XML formatındaki metinler üzerinde ön işlemleri yapıp bir dataframe haline getiren dosya

Ön işlemlerin başarılı şekilde yapılabilmesi için [Zemberek-nlp](https://github.com/ahmetaa/zemberek-nlp)nin indirilmesi gerekmektedir.

## Alıntı:
Eğer akademik çalışmanızda buradaki kaynaklardan faydalandıysanız lütfen aşağıdaki çalışmaya atıf yapınız:
> Yazar = {**Ensar Emirali, M. Elif Karslıgil**},
> Başlık = {**bi-TEZAT: biLSTM YÖNTEMİYLE TÜRKÇE ŞİKAYET METİNLERİNDE ZAMAN İFADELERİNİN TESPİT EDİLMESİ**},
> 
> Ay = Temmuz,
> 
> Yıl = 202022,
> 
> URL = {*eklenecek*}
