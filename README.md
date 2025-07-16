# Simulatore-Fantacalcio

## Sito per Simulare un campionato di Fantacalcio

### CI Status

- React CI:
  ![React CI](https://github.com/Sviluppatori-ITS/Simulatore-Fantacalcio/actions/workflows/react-ci.yml/badge.svg)

- Django CI:
  ![Django CI](https://github.com/Sviluppatori-ITS/Simulatore-Fantacalcio/actions/workflows/django.yml/badge.svg)

- Python Lint & Test:
  ![Python Lint & Test](https://github.com/Sviluppatori-ITS/Simulatore-Fantacalcio/actions/workflows/python-lint-test.yml/badge.svg)

- CodeQL Security Scan:
  ![CodeQL](https://github.com/Sviluppatori-ITS/Simulatore-Fantacalcio/actions/workflows/codeql.yml/badge.svg)

---

## INSTALLAZIONE

```bash
# 1 - crea e attiva un virtualvenv
$ python -m venv .venv
$ source .venv/bin/activate #su Linux
$ .venv/Scripts/activate #su Windows

# 2 – installa i requirements o i dev-requirements, se in modalità DEBUG
$ pip install -r requirements.txt
```

---

## PREPARAZIONE DEL PROGETTO

```bash
# 1 - prepara ed esegui le migrazioni del database
$ python manage.py makemigrations
$ python manage.py migrate

# 2 - se sei in produzione colleziona i file statici
$ python manage.py collectstatic
```

---

## TESTA IL PROGETTO

```bash
# 1 - testa se il progetto è stato installato correttamente
$ python manage.py test
```
