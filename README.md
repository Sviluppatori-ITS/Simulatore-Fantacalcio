# Simulatore-Fantacalcio

## Sito per Simulare un campionato di Fantacalcio

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
