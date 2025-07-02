from __future__ import annotations
import logging
import inspect
import os


def get_logger():
    logger = logging.getLogger("django")  # nome logger comune
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Verifica se siamo in test cercando 'tests' nello stack
    stack = inspect.stack()
    is_test = any('tests' in getattr(frame, 'filename', '') for frame in stack)

    # Definisci i percorsi assoluti per i log file (modifica base_dir se serve)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tests_log_path = os.path.join(base_dir, '../logs/tests.log')
    django_log_path = os.path.join(base_dir, '../logs/django.log')

    # Scegli file di log in base al contesto
    log_file = tests_log_path if is_test else django_log_path

    # Rimuovi eventuali handler già presenti per evitare duplicati
    logger.handlers.clear()

    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
