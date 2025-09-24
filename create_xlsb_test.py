import pandas as pd
import io
import msoffcrypto

file_path = "C:\\Users\\HomePC\\Downloads\\hi.xlsb"
password = "bbuk"

decrypted_wb = io.BytesIO()

with open(file_path, 'rb') as f:
    office_file = msoffcrypto.OfficeFile(f)
    
    if office_file.is_encrypted():
        office_file.load_key(password=password)
        office_file.decrypt(decrypted_wb)
        decrypted_wb.seek(0)
        df = pd.read_excel(decrypted_wb, engine='pyxlsb')
    else:
        print("File is not encrypted, reading directly")
        df = pd.read_excel(file_path, engine='pyxlsb')

print(f"{len(df)} rows, {len(df.columns)} columns")
print(df.head())