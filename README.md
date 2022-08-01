# bi-TEZAT: Dataset

Zaman ifadeleri etiketlenmiş/etiketlenmemiş Türkçe şikayet metinlerini içermektedir. 

Etiketleme şu formatta yapılmıştır:
``` 
**<ZAMAN_İFADESİ_TİPİ>** _zaman ifadesi_ **</ZAMAN_İFADESİ_TİPİ>**
```

Klasörler ve dosyaların detayları aşağıda belirtilmiştir:
- ***scrapping.py:*** İnternet ortamından şikayetleri indirmek için yazılan Python kodu
- ***labeled_dataset:*** İnternet ortamında indirilen ve etiketlenen 500 şikayet metni
- ***unlabeled_dataset:*** İnternet ortamında indirilen ve etiketlenmemiş 127 şikayet metni
- ***model:*** Şikayet metinlerini düzenlemek için Python kodları:
- - ***parameters.py:*** Ön işlemler sırasında ihtiyaç olan parametrelerin saklandığı dosya
- - ***preprocess.py:*** Ön işlemler sırasında ihtiyaç olan fonksiyonların saklandığı dosya
- - ***preparation.py:*** XML formatındaki metinler üzerinde ön işlemleri yapıp bir dataframe haline getiren dosya


> Önemli: Ön işlemlerin başarılı şekilde yapılabilmesi için [Zemberek-nlp](https://github.com/ahmetaa/zemberek-nlp)nin indirilmesi gerekmektedir.


## Çalışmalar:
Buradaki veriseti aşağıdaki çalışma kapsamında hazırlanmıştır:
```
E. Emirali ve M. E. Karslıgil, “Türkçe Metinlerde Zaman İfadelerinin Tespitinde Kelime Vektörlerinin Kullanılması,” 30. IEEE Sinya İşleme ve İletişim Uygulamaları Kurultayı, 2022.
```
