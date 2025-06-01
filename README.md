# Sentry Vault

![Sentry Vault](assets/sentry-vault-logo.png)  
_A security-focused password manager with decentralized storage and quantum-resistant encryption._

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🔐 About

Sentry Vault is an open-source, high-security password manager designed with privacy and security as its core principles. It provides a secure way to store and manage your credentials while ensuring that you remain in full control of your data.

### 🔑 Core Security Features

- **Military-Grade Encryption**: Combines Argon2 for key derivation with AES-128 in Fernet mode for encryption
- **Decentralized Storage**: Implements Shamir's Secret Sharing to split your vault across multiple locations
- **Zero-Knowledge Architecture**: Your master password never leaves your device
- **Semantic Passphrase Generation**: Create memorable yet secure passphrases
- **Quantum-Resistant Design**: Ready for the post-quantum era with forward-thinking architecture

## 🚀 Features

### 🔒 Core Functionality

- **Secure Credential Storage**: Store usernames and passwords with military-grade encryption
- **Sharded Vaults**: Optional Shamir's Secret Sharing for decentralized storage
- **Rich CLI Interface**: Beautiful terminal interface with colorized output and progress bars
- **Password Generator**: Built-in tool for creating strong, random passwords
- **Secure File Encryption**: Encrypt/decrypt files using the same strong cryptography

### 🛡️ Security Features

- **Argon2** for key derivation (memory-hard and resistant to GPU/ASIC attacks)
- **AES-128** in Fernet mode for authenticated encryption
- **HMAC** for data integrity verification
- **Secure Memory Management**: Sensitive data is wiped from memory when no longer needed
- **Time-Constant String Comparison**: Prevents timing attacks

## 🛠 Installation

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- OpenSSL (for cryptographic operations)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/agspades/sentry-vault.git
cd sentry-vault

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell

# Run the CLI
sentryvault --help
```

## 📜 Usage

### Basic Commands

```bash
# Add a new credential
sentryvault add example.com username

# Retrieve a credential
sentryvault get example.com

# List all stored entries
sentryvault list

# Remove a credential
sentryvault delete example.com

# Change your master passphrase
sentryvault change-passphrase

# Generate a secure password
sentryvault generate-password --type=random --length=16
```

### Using Sharded Vaults

```bash
# Create a sharded vault (3 out of 5 shares required to recover)
sentryvault add example.com username --total-shares=5 --threshold=3

# Access a sharded vault
sentryvault get example.com --total-shares=5 --threshold=3
```

### File Encryption

```bash
# Encrypt a file
sentryvault encrypt sensitive.txt sensitive.enc

# Decrypt a file
sentryvault decrypt sensitive.enc sensitive_decrypted.txt
```

## 🔧 Advanced Usage

### Environment Variables

- `SENTRY_VAULT_PATH`: Default path for the vault file
- `SENTRY_VAULT_SHARES`: Default number of shares for sharding
- `SENTRY_VAULT_THRESHOLD`: Default threshold for shard recovery

### Password Generation Options

```bash
# Generate a random password with specific requirements
sentryvault generate-password --type=random --length=20 --no-upper --no-special

# Generate a memorable passphrase
sentryvault generate-password --type=passphrase --words=6
```

## 🛡️ Security Best Practices

1. **Use a Strong Master Password**: Choose a long, random passphrase
2. **Enable Sharding**: Distribute shards across multiple secure locations
3. **Regular Backups**: Keep regular backups of your vault in secure locations
4. **Secure Environment**: Only run Sentry Vault on trusted, secure systems
5. **Keep Software Updated**: Regularly update to the latest version for security patches

## 🧑‍💻 Contributing

We welcome contributions! Please read our [Contribution Guidelines](CONTRIBUTING.md) and sign the [Contributor License Agreement](CONTRIBUTOR_LICENSE_AGREEMENT.md) before submitting pull requests.

### Development Setup

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black .

# Check types
poetry run mypy .
```

## 📄 License

Sentry Vault is licensed under the [GNU Affero General Public License v3.0](LICENSE). This is a strong copyleft license that ensures any modifications to the software must be released under the same license.

## ⭐ Support the Project

If you find Sentry Vault useful, please consider:

- Giving us a ⭐ on GitHub
- Reporting bugs or suggesting features
- Contributing code or documentation
- Spreading the word to others who might find it useful

---

🔒 *"In a world of digital threats, your security is our mission."*
