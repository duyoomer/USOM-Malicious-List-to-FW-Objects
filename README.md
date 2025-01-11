# Firewall Configuration Generator

Bu Python programı, USOM tarafından sağlanan zararlı URL listesini indirir ve bu listeyi kullanarak  firewall için konfigürasyon dosyası oluşturur. Program, IP adreslerini ve FQDN (Fully Qualified Domain Name) adreslerini ayırt eder ve zararlı olmayan IP aralıklarını hariç tutar.

## Gereksinimler

- Python 3.x
- `requests` modülü
- İnternet bağlantısı (URL listesini indirmek için)

## Kurulum

1. Python 3.x'in yüklü olduğundan emin olun.
2. Gerekli Python modüllerini yükleyin:

    ```sh
    pip install requests
    ```

3. Program dosyasını indirin veya kopyalayın.

## Kullanım

1. Program dosyasını çalıştırın:

    ```sh
    python fortigate.py
    ```

2. Program, USOM URL listesini indirecek veya mevcutsa yerel dosyayı kullanacak ve Fortigate firewall için `fortigate_objects.txt` adında bir konfigürasyon dosyası oluşturacaktır.

3. Programın sonunda, işlenen obje sayısı, mükerrer obje sayısı, FQDN ve IP nesne sayısı ve çalışma süresi gibi istatistikler görüntülenecektir.

## Program Açıklaması

- **URL Listesi İndirme veya Kullanma:** Program, `https://www.usom.gov.tr/url-list.txt` adresinden URL listesini indirir veya eğer dosya zaten mevcutsa yerel dosyayı kullanır.
- **URL Filtreleme:** URL listesindeki mükerrerleri filtreler ve orijinal sıralamayı korur.
- **IP ve FQDN Kontrolü:** Her bir URL'nin IP adresi mi yoksa FQDN mi olduğunu kontrol eder. Zararlı olmayan IP aralıklarını hariç tutar.
- **Fortigate Konfigürasyon Dosyası Oluşturma:** Her bir benzersiz URL için Fortigate address object oluşturur ve `fortigate_objects.txt` dosyasına yazar.
- **İstatistikler:** Programın sonunda, işlenen obje sayısı, mükerrer obje sayısı, FQDN ve IP nesne sayısı ve çalışma süresi gibi istatistikleri görüntüler.

## Örnek Çıktı

Program çalıştırıldıktan sonra aşağıdaki gibi bir çıktı alacaksınız:

```sh
URL listesi zaten mevcut: 'url_list.txt'
url_list.txt dosyası silindi.
Fortigate firewall konfigürasyon dosyası 'fortigate_objects.txt' oluşturuldu.
Girdi dosyasındaki toplam obje sayısı: 1000
İşlenen benzersiz obje sayısı: 950
Mükerrer obje sayısı: 50
Toplam FQDN nesne sayısı: 500
Toplam IP nesne sayısı: 450
Çalışma süresi: 12.34 saniye
