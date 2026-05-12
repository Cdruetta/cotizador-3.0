from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID

def generar_csr(cuit: str, razon_social: str):
    """Genera clave privada + CSR. Retorna (key_pem, csr_pem) como bytes."""
    clave = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    clave_pem = clave.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    cuit_limpio = cuit.replace('-', '')
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "AR"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, razon_social),
            x509.NameAttribute(NameOID.COMMON_NAME, razon_social),
            x509.NameAttribute(NameOID.SERIAL_NUMBER, f"CUIT {cuit_limpio}"),
        ]))
        .sign(clave, algorithm=None, backend=default_backend())
    )
    csr_pem = csr.public_bytes(serialization.Encoding.PEM)
    return clave_pem, csr_pem