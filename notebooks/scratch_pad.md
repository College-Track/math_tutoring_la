---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.5.2
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

## math_tutoring_2020

Project to determine the impact math and tutoring workshops have on student outcomes.

### Data Sources
- file1 : Link to SF Report
- file2:  Link to SF Report (As Needed)
- file3:  Link to SF Report (As Needed)

### Changes
- 10-07-2020 : Started project

```python
# ALWAYS RUN
# General Setup 

%load_ext dotenv
%dotenv

import pandas as pd
from pathlib import Path
from datetime import datetime
import os
import numpy as np

```

```python

project_id = "learning-agendas"


```

```python

# Download data and save to a CSV. If data needs to be refreshed the CSV needs to be deleted.
filename = '../data/raw/test_attendance_data.csv'
table_name = 'gathered_test_attendance_at_data'

if os.path.exists(filename):
    # Read from CSV if already written to avoid repeatedly transferring data from BigQuery
    df = pd.read_csv(filename)
    df = df.drop('Unnamed: 0', axis=1)
else:      
    query = 'SELECT * FROM `learning-agendas.math_tutoring_2020.' + table_name + '`'
    df = pd.read_gbq(query, project_id=project_id)
    df.to_csv(filename)
```

```python
df.columns
```

```python
print((df.notnull().sum()/df.shape[0]).sort_values(ascending=False).to_string())
(df.notnull().sum()/df.shape[0]).hist()
```

```python
df.max_act_reading.hist()
```

```python
sat_to_act_math = pd.read_csv('../data/raw/sat_to_act_math.csv')
sat_to_act_english_reading = pd.read_csv('../data/raw/sat_to_act_english_reading.csv')
```

```python
def convert_sat_to_act(sat_score, conversion_file, act_score):

    try: 
        conversion_score = conversion_file[sat_score >= conversion_file.SAT].reset_index().iloc[0]['ACT']
        if pd.isna(act_score):
            return conversion_score
        elif conversion_score >= act_score:
            return conversion_score
        else:
            return act_score
    except:
        return act_score
     
```

```python
df["max_act_english_reading"] = df.max_act_english + df.max_act_reading
```

```python
df["max_converted_math"] = df.apply(lambda x: convert_sat_to_act(
    x['max_sat_math'], sat_to_act_math, x['max_act_math']), axis=1)

```

```python
df["max_converted_english_reading"] = df.apply(lambda x: convert_sat_to_act(
    x['max_sat_english'], sat_to_act_english_reading, x['max_act_english_reading']), axis=1)

```

```python
df["max_converted_english"] = df.apply(lambda x: convert_sat_to_act(
    x['max_sat_english'], sat_to_act_math, x['max_act_english']), axis=1)

```

```python
df["max_converted_reading"] = df.apply(lambda x: convert_sat_to_act(
    x['max_sat_english'], sat_to_act_math, x['max_act_reading']), axis=1)

```

```python
df.loc[pd.isna(df.mod_duration), "mod_duration_filled"] = df.loc[pd.isna(
    df.mod_duration), "Attendance_Numerator"] * 60
```

```python
df.loc[~pd.isna(df.mod_duration), "mod_duration_filled"] = df.loc[~pd.isna(df.mod_duration), "mod_duration"]
```

### Save output file into processed directory

Save a file in the processed directory that is cleaned properly. It will be read in and used later for further analysis.

```python
# Save File 1 Data Frame (Or master df)
df.to_pickle(summary_file)
```
