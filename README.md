# Sentry Vault

_A security-focused local password manager with optional sharded storage._

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/sentryvault?color=blue)](https://pypi.org/project/sentryvault/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🔐 About

Sentry Vault is an open-source, high-security password manager designed with privacy and security as its core principles. It provides a secure way to store and manage your credentials while ensuring that you remain in full control of your data.

### 🔑 Core Security Features

- **Strong Encryption**: Uses Argon2id for key derivation and Fernet for authenticated encryption
- **Sharded Storage**: Uses Shamir's Secret Sharing to split encrypted vault data into threshold-based shares
- **Zero-Knowledge Architecture**: Your master password never leaves your device
- **Passphrase Generation**: Create random, memorable, or PIN-style credentials from the CLI

## 🚀 Features

### 🔒 Core Functionality

- **Secure Credential Storage**: Store usernames and passwords in an encrypted local vault
- **Sharded Vaults**: Optional threshold-based sharding using Shamir's Secret Sharing
- **Rich CLI Interface**: Beautiful terminal interface with colorized output and progress bars
- **Password Generator**: Built-in tool for creating strong, random passwords
- **Secure File Encryption**: Encrypt/decrypt files using the same strong cryptography

### 🛡️ Security Features

- **Argon2** for key derivation (memory-hard and resistant to GPU/ASIC attacks)
- **Fernet authenticated encryption** for confidentiality and integrity
- **HMAC** for data integrity verification
- **Per-vault salt handling** persisted with encrypted vault payloads

## 🛠 Installation

### Prerequisites

- Python 3.10 or higher

### Quick Start (Recommended)

Install Sentry Vault directly from PyPI:

```bash
pip install sentryvault
```

### Installation from Source

If you prefer to build from source or contribute:

```bash
# Clone the repository
git clone https://github.com/agspades/sentry-vault.git
cd sentry-vault

# Install dependencies using Poetry
poetry install

# Run via poetry
poetry run sentryvault --help
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
sentryvault generate-password --length 20
```

### File Encryption

```bash
# Encrypt a file
sentryvault encrypt sensitive.txt sensitive.enc

# Decrypt a file
sentryvault decrypt sensitive.enc sensitive_decrypted.txt
```

## 🔧 Advanced Usage

### Password Generation Options

```bash
# Generate a random password with specific requirements
sentryvault generate-password --length 20

# Generate a memorable passphrase and copy to clipboard
sentryvault generate-password --type memorable -c
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

🔒 _"In a world of digital threats, your security is our mission."_
