# generate_cert.py
import os
from OpenSSL import crypto

def generate_self_signed_cert(cert_file="cert.pem", key_file="key.pem"):
    # Create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    
    # Create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "US"
    cert.get_subject().ST = "State"
    cert.get_subject().L = "City"
    cert.get_subject().O = "Organization"
    cert.get_subject().OU = "Organizational Unit"
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)  # 10 years validity
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')
    
    # Write cert and key to files
    with open(cert_file, "wb") as cf:
        cf.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open(key_file, "wb") as kf:
        kf.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    
    print(f"Certificate and key files created: {cert_file}, {key_file}")

if __name__ == "__main__":
    if not os.path.exists("cert.pem") or not os.path.exists("key.pem"):
        generate_self_signed_cert()
    else:
        print("Certificate files already exist. Remove them if you want to generate new ones.")
