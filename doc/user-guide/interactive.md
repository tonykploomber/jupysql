---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Interactive SQL queries

```{code-cell} ipython3
%load_ext sql
from pathlib import Path
from urllib.request import urlretrieve

if not Path("penguins.csv").is_file():
    urlretrieve(
        "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",
        "penguins.csv",
    )
%sql duckdb://
```

Give some simple query

```{code-cell} ipython3
%sql --interact-slider my_limit 20 SELECT * FROM penguins.csv LIMIT {{my_limit}}
```

```{code-cell} ipython3

```
