import os
import requests
import socket
import ipaddress
import time

# URL listesinin bulunduğu dosya URL'si
url = "https://www.usom.gov.tr/url-list.txt"

# URL listesini kaydedeceğimiz yerel dosya adı
local_filename = "url_list.txt"

# Palo Alto config dosyası adı
output_filename = "paloalto_objects.txt"

# Zararlı olmayan IP aralıkları (localhost, private IP'ler ve APIPA)
private_ip_ranges = [
    ipaddress.ip_network("127.0.0.0/8"),         # Localhost
    ipaddress.ip_network("10.0.0.0/8"),          # Private IP: 10.0.0.0/8
    ipaddress.ip_network("172.16.0.0/12"),       # Private IP: 172.16.0.0/12
    ipaddress.ip_network("192.168.0.0/16"),      # Private IP: 192.168.0.0/16
    ipaddress.ip_network("169.254.0.0/16"),      # APIPA
]

# Sayaçlar
fqdn_count = 0
ip_count = 0
input_object_count = 0
processed_object_count = 0

# Çalışma süresini ölçmeye başla
start_time = time.time()

# URL listesini indir veya mevcut dosyayı kullan
if not os.path.exists(local_filename):
    print("URL listesi mevcut değil, indiriliyor...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_filename, "w") as f:
            f.write(response.text)
        print(f"URL listesi indirildi ve '{local_filename}' olarak kaydedildi.")
    else:
        print("URL listesi indirilemedi.")
        exit(1)
else:
    print(f"URL listesi zaten mevcut: '{local_filename}'")

# URL listesini okuma ve orijinal sıralamayı koruyarak mükerrerleri filtreleme
with open(local_filename, "r") as f:
    url_list = f.read().splitlines()

# Girdi dosyasındaki toplam obje sayısı
input_object_count = len(url_list)

# Mükerrer URL'leri filtrele ve orijinal sıralamayı koru
unique_urls = list(dict.fromkeys(url_list))  # Orijinal sıralamayı koru ve mükerrerleri filtrele

# Eğer paloalto_objects.txt dosyası mevcutsa, sil
if os.path.exists(output_filename):
    os.remove(output_filename)
    print(f"{output_filename} dosyası silindi.")

# Palo Alto firewall için konfigürasyon dosyası oluştur
with open(output_filename, "w") as f:
    # URL listesindeki her bir benzersiz URL için Palo Alto address object oluştur
    for i, url in enumerate(unique_urls):
        if url.strip():  # Boş satırları atla
            # IP adresi mi yoksa FQDN mi olduğunu kontrol et
            try:
                # Eğer URL bir IP adresiyse (IPv4 veya IPv6)
                socket.inet_aton(url.strip())  # IPv4 için kontrol
                ip = ipaddress.ip_address(url.strip())

                # Eğer IP, zararlı olmayan IP aralıklarında ise, geç
                if any(ip in network for network in private_ip_ranges):
                    continue

                object_type = "ip-netmask"
                ip_count += 1  # IP nesnesi sayacını artır

            except socket.error:
                try:
                    socket.inet_pton(socket.AF_INET6, url.strip())  # IPv6 için kontrol
                    ip = ipaddress.ip_address(url.strip())

                    # Eğer IP, zararlı olmayan IP aralıklarında ise, geç
                    if any(ip in network for network in private_ip_ranges):
                        continue

                    object_type = "ip-netmask"
                    ip_count += 1  # IP nesnesi sayacını artır

                except socket.error:
                    # URL bir IP adresi değilse, o zaman FQDN
                    object_type = "fqdn"
                    fqdn_count += 1  # FQDN nesnesi sayacını artır

            # İşlenen obje sayısını artır
            processed_object_count += 1

            # Object ismi
            object_name = f"Zararlı_Web_{i + 1}"

            # Palo Alto nesnesi ekleme (FQDN veya IP türüne göre)
            if object_type == "fqdn":
                f.write(f"set address \"{object_name}\" type fqdn fqdn \"{url.strip()}\"\n")
            elif object_type == "ip-netmask":
                f.write(f"set address \"{object_name}\" type ip-netmask ip-netmask \"{url.strip()}/32\"\n")
    
# Çalışma süresini hesapla
end_time = time.time()
elapsed_time = end_time - start_time

# Mükerrer obje sayısını hesapla
duplicate_object_count = input_object_count - processed_object_count

# Sonuçları yazdır
print(f"Palo Alto firewall konfigürasyon dosyası '{output_filename}' oluşturuldu.")
print(f"Girdi dosyasındaki toplam obje sayısı: {input_object_count}")
print(f"İşlenen benzersiz obje sayısı: {processed_object_count}")
print(f"Mükerrer obje sayısı: {duplicate_object_count}")
print(f"Toplam FQDN nesne sayısı: {fqdn_count}")
print(f"Toplam IP nesne sayısı: {ip_count}")
print(f"Çalışma süresi: {elapsed_time:.2f} saniye")