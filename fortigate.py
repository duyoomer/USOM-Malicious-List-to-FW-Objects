import os
import requests
import socket
import ipaddress
import time

# URL listesinin bulunduğu dosya URL'si
url = "https://www.usom.gov.tr/url-list.txt"

# URL listesini kaydedeceğimiz yerel dosya adı
local_filename = "url_list.txt"

# Fortigate config dosyası adı
output_filename = "fortigate_objects.txt"

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

# Eğer fortigate_objects.txt dosyası mevcutsa, sil
if os.path.exists(output_filename):
    os.remove(output_filename)
    print(f"{output_filename} dosyası silindi.")

# Fortigate firewall için konfigürasyon dosyası oluştur
with open(output_filename, "w") as f:
    # Fortigate konfigürasyon başlangıcı
    f.write("config firewall address\n")

    # URL listesindeki her bir benzersiz URL için Fortigate address object oluştur
    for i, url in enumerate(unique_urls):
        if url.strip():  # Boş satırları atla
            # IP adresi mi yoksa FQDN mi olduğunu kontrol et
            try:
                # Eğer URL bir IP adresiyse (IPv4 veya IPv6)
                socket.inet_aton(url.strip())  # IPv4 için kontrol
                object_type = "ipmask"  # IP adresi türü
                subnet = "255.255.255.255"  # IP için varsayılan subnet mask
                ip = ipaddress.ip_address(url.strip())

                # Eğer IP, zararlı olmayan IP aralıklarında ise, geç
                if any(ip in network for network in private_ip_ranges):
                    continue

                ip_count += 1  # IP nesnesi sayacını artır

            except socket.error:
                try:
                    socket.inet_pton(socket.AF_INET6, url.strip())  # IPv6 için kontrol
                    object_type = "ipmask"  # IP adresi türü
                    subnet = "255.255.255.255"  # IP için varsayılan subnet mask
                    ip = ipaddress.ip_address(url.strip())

                    # Eğer IP, zararlı olmayan IP aralıklarında ise, geç
                    if any(ip in network for network in private_ip_ranges):
                        continue

                    ip_count += 1  # IP nesnesi sayacını artır

                except socket.error:
                    # URL bir IP adresi değilse, o zaman FQDN
                    object_type = "fqdn"
                    subnet = None  # FQDN için subnet yok
                    fqdn_count += 1  # FQDN nesnesi sayacını artır

            # Processed object sayısını artır
            processed_object_count += 1

            # Object ismi
            object_name = f"Zararlı_Web_{i + 1}"

            # Object ekleme (FQDN veya IP türüne göre)
            f.write(f"    edit \"{object_name}\"\n")
            f.write(f"        set type {object_type}\n")
            
            if object_type == "fqdn":
                f.write(f"        set fqdn \"{url.strip()}\"\n")
            elif object_type == "ipmask":
                f.write(f"        set subnet {url.strip()} {subnet}\n")
            
            f.write("    next\n")
    
    f.write("end\n")

# Çalışma süresini hesapla
end_time = time.time()
elapsed_time = end_time - start_time

# Mükerrer obje sayısını hesapla
duplicate_object_count = input_object_count - processed_object_count

# Sonuçları yazdır
print(f"Fortigate firewall konfigürasyon dosyası '{output_filename}' oluşturuldu.")
print(f"Girdi dosyasındaki toplam obje sayısı: {input_object_count}")
print(f"İşlenen benzersiz obje sayısı: {processed_object_count}")
print(f"Mükerrer obje sayısı: {duplicate_object_count}")
print(f"Toplam FQDN nesne sayısı: {fqdn_count}")
print(f"Toplam IP nesne sayısı: {ip_count}")
print(f"Çalışma süresi: {elapsed_time:.2f} saniye")