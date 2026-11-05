# AccuKnox Django Trainee Assignment

This standalone Django project demonstrates Django signal execution and a custom
iterable `Rectangle` class.

## Setup

Python 3.10+ is recommended.

```bash
python -m venv venv
# Windows PowerShell:
venv\Scripts\Activate.ps1


pip install -r requirements.txt
python manage.py migrate
python manage.py run_demo
python manage.py test
```

## Django Signals: conclusions

1. **Synchronous:** `post_save.send()` invokes receivers before returning. The
   demo records the order `before save -> receiver -> after save`.
2. **Same thread:** the receiver records `threading.get_ident()` and compares
   it with the caller's thread ID.
3. **Database transaction:** signals do not create a transaction themselves.
   - Under normal autocommit, the model save and receiver's database write are
     not enclosed in one shared transaction (`connection.in_atomic_block`
     is `False`).
   - Inside `transaction.atomic()`, the receiver runs inside the caller's
     transaction. The demo deliberately raises an exception and verifies that
     both the model row and receiver-created row are rolled back.

The third answer is conditional: a signal receiver participates in an
already-active transaction on the same database connection; it does not
automatically make every save operation transactional.

## Project structure

- `config/`: Django settings and URL configuration
- `demo/`: model, signal receiver, management command, tests
- `rectangle.py`: custom iterable class
