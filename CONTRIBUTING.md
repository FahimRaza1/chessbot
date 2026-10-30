# Contributing

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run checks

```powershell
python -m pytest
```

Keep changes focused, add tests for behavior changes, and never commit `.env` or API tokens.
