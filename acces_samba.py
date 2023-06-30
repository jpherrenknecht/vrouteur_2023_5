import smbclient
from smb.SMBConnection import SMBConnection

samba_server = '192.168.0.23'
samba_share = 'gribs'
samba_username = 'jp'
samba_password = 'Licois1000'


conn = SMBConnection(samba_username, samba_password, 'client', 'serveur')
conn.connect(samba_server)

file_path='exclusions570.txt'


file_obj = conn.open(samba_share, file_path, 'r')  # 'r' pour mode lecture

# Affichage du contenu du fichier
file_content = file_obj.read()
print(file_content.decode())




local_file_path = '/home/jp/vrouteur_2023_5/exclusionimporte2.txt'
with open(local_file_path, 'wb') as file_obj:
    conn.retrieveFile(samba_share, file_path, file_obj)

# Fermeture de la connexion Samba
conn.close()



