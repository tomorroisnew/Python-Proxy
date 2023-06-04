import OpenSSL.crypto as crypto
import datetime
import os
import sys
import argparse

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta
import ipaddress

def main():
    parser = argparse.ArgumentParser(
                    prog='GenerateCertificates',
                    description='Generate Certificates for a hostname, to be installed in your root certificates to support ssl mitm')

    parser.add_argument('-H', dest='HOSTNAME', type=str, required=True, help="Hostname of the server")
    parser.add_argument("-I", dest='IP', type=str, required=True, help="Ip of the proxy server")
    parser.add_argument("-o", dest='OUTDIR', type=str, required=True, help="Directory to store the certificates")

    args = parser.parse_args()

    print(args.OUTDIR)

    # Generate a private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Create a self-signed certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, f"{args.HOSTNAME}")
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(f"{args.HOSTNAME}"),
            x509.DNSName(u"localhost"),
            x509.IPAddress(ipaddress.ip_address(f"{args.IP}")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    # Save the certificate and private key to files
    if(not os.path.exists(f'{args.OUTDIR}')):
        os.mkdir(f'{args.OUTDIR}')

    with open(f"{args.OUTDIR}/server.crt", "wb") as crt_file:
        crt_file.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(f"{args.OUTDIR}/server.key", "wb") as key_file:
        key_file.write(private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        ))

    # Generate DER file for importing into the root CA
    with open(f"{args.OUTDIR}/server.crt", "rb") as crt_file:
        cert_data = crt_file.read()

    cert = x509.load_pem_x509_certificate(cert_data)
    der_data = cert.public_bytes(serialization.Encoding.DER)

    with open(f"{args.OUTDIR}/server.der", "wb") as der_file:
        der_file.write(der_data)

if __name__ == "__main__":
    main()