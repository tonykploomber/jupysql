---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  notebook_metadata_filter: myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
myst:
  html_meta:
    description lang=en: Export results from a SQL query to a CSV file from Jupyter
    keywords: jupyter, sql, jupysql, csv
    property=og:locale: en_US
---

# Interactive ggplot

+++

The ggplot API allows us to build different types of of graphics

+++

## Examples

+++

### Setup

```{code-cell} ipython3
%load_ext sql
%sql duckdb://
```

```{code-cell} ipython3
from sql.ggplot import ggplot, aes, geom_boxplot, geom_histogram, facet_wrap
import ipywidgets as widgets
from ipywidgets import interact
```

```{code-cell} ipython3
from pathlib import Path
from urllib.request import urlretrieve

url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet"

if not Path("yellow_tripdata_2021-01.parquet").is_file():
    urlretrieve(url, "yellow_tripdata_2021-01.parquet")
```

### Basic Usage (with Dropdown and Slider widgets)

```{code-cell} ipython3
dropdown = widgets.Dropdown(
    options=['red', 'blue', 'green', 'magenta'],
    value='red',
    description='Color:',
    disabled=False,
)
b = widgets.IntSlider(
    value=5,
    min=1,
    max=10,
    step=1,
    description='Bin:',
    orientation='horizontal',
)
```

```{code-cell} ipython3
def plot_fct(color, b):
    (ggplot(table="yellow_tripdata_2021-01.parquet", mapping=aes(x="trip_distance", fill=color))
    + geom_histogram(bins=b))
    
interact(plot_fct, color=dropdown, b = b)
```

### Categorical histogram (with Select widget)

+++

#### Prepare dataset

We also use `ggplot2` diamonds to demostrate

```{code-cell} ipython3
from pathlib import Path
from urllib.request import urlretrieve

if not Path("diamonds.csv").is_file():
    urlretrieve(
        "https://raw.githubusercontent.com/tidyverse/ggplot2/main/data-raw/diamonds.csv",  # noqa
        "diamonds.csv",
    )
```

```{code-cell} ipython3
%%sql
CREATE TABLE diamonds AS SELECT * FROM diamonds.csv
```

#### Multiple Columns

```{code-cell} ipython3
columns = widgets.SelectMultiple(
    options=["cut", "color"],
    value=['cut'],
    description='Columns',
    disabled=False
)
```

```{code-cell} ipython3
def plot(columns):
    (ggplot("diamonds", aes(x=columns)) + geom_histogram())

interact(plot, columns=columns)
```

```{code-cell} ipython3
cmap = widgets.Dropdown(
    options=['viridis', 'plasma', 'inferno', 'magma', 'cividis'],
    value='plasma',
    description='Colormaps:',
    disabled=False,
)
```

```{code-cell} ipython3
def plot(cmap):
    (
        ggplot("diamonds", aes(x="price"))
        + geom_histogram(bins=10, fill="cut", cmap=cmap)
    )
    
interact(plot, cmap=cmap)
```

#### Facet wrap (Complete Example)

```{code-cell} ipython3
b = widgets.IntSlider(
    value=5,
    min=1,
    max=10,
    step=1,
    description='Bin:',
    orientation='horizontal',
)
cmap = widgets.Dropdown(
    options=['viridis', 'plasma', 'inferno', 'magma', 'cividis'],
    value='plasma',
    description='Colormaps:',
    disabled=False,
)
show_legend = widgets.ToggleButton(
    value=False,
    description='Show legend',
    disabled=False,
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Is show legend',
)
```

```{code-cell} ipython3
def plot(b, cmap, show_legend):
    (ggplot("diamonds", aes(x="price"))
    + geom_histogram(bins=b, fill="cut", cmap=cmap)
    + facet_wrap("color", legend=show_legend))
    
interact(plot, b=b, cmap=cmap, show_legend= show_legend)
```

```{code-cell} ipython3

```

```{code-cell} ipython3

```
