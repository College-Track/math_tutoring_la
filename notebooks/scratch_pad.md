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
# print((df.notnull().sum()/df.shape[0]).sort_values(ascending=False).to_string())
# (df.notnull().sum()/df.shape[0]).hist()
```

```python
# df.mod_dosage_type.value_counts()
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

```python
df.to_pickle("../data/interim/data_converted.pkl")
```

```python
df = pd.read_pickle("../data/interim/data_converted.pkl")
```

```python
def create_year_to_year_df(df, grades_num):
    grades = [str(i) + "th Grade" for i in grades_num]

    columns_to_check = ["attendance_rate_" + str(grades_num[0]) + "th Grade_Math Blast", "attendance_rate_" + str(
        grades_num[0]) + "th Grade_Tutoring", "attendance_rate_" + str(grades_num[0]) + "th Grade_Math"]

    _df = df[(df.AT_Grade__c.isin(grades))]

    _df = _df[~_df.ay_spring_status.isin(
        ["Did Not Finish CT HS Program", "Prior to joining CT HS Program"])]

    _df_academics = _df[_df.AT_Grade__c == grades[1]][
        ['Contact_Id',
         'site_short',
         'AT_Grade__c',
         'GPA_semester_cumulative__c',
         'HS_11th_Cum_GPA',
         'max_converted_math',
         'max_converted_english_reading',
         'max_converted_english',
         'max_converted_reading',
         'first_gpa',
         'gpa_growth',
         'first_gpa_grade',
         "highest_math_score",
         "first_math_score",
         'highest_math_score_grade',
         'math_test_growth',
         "first_math_grade"
         ]
    ].groupby(
        ['Contact_Id', 'site_short', 'AT_Grade__c', 'first_gpa', 'HS_11th_Cum_GPA']).max().unstack('AT_Grade__c')

    _df_worksops = _df[_df.AT_Grade__c == grades[0]][['Contact_Id', 'site_short', 'AT_Grade__c', 'mod_dosage_type', 'Attendance_Numerator',
                                                      'attendance_rate', 'mod_duration_filled']].groupby(['Contact_Id', 'AT_Grade__c', 'mod_dosage_type']).sum().unstack(['AT_Grade__c', 'mod_dosage_type'])

    _df_academics = rename_df_columns(_df_academics)

    _df_worksops = rename_df_columns(_df_worksops)

    combined_df = _df_academics.merge(
        _df_worksops, left_index=True, right_index=True, how='left')

    combined_df.dropna(subset=columns_to_check, how='all', inplace=True)
    combined_df.columns = combined_df.columns.str.replace(' ', '_')
    return combined_df.reset_index()
```

```python
def rename_df_columns(_df):
    _df.columns = _df.columns.to_flat_index()
    
    new_col_names = ['_'.join(i) for i in _df.columns]

    _df.columns = new_col_names
    return _df
```

```python
df = df.sort_values(['Contact_Id','AY_Name'], ascending=True)

```

```python
first_gpa = df[['Contact_Id', 'GPA_semester_cumulative__c', "AT_Grade__c"]].groupby(
    'Contact_Id', as_index=False).first(numeric_only=False)

first_gpa.rename(columns={'GPA_semester_cumulative__c': 'first_gpa',
                          "AT_Grade__c": "first_gpa_grade"}, inplace=True)
```

```python
first_math_test = df[['Contact_Id', 'max_converted_math', "AT_Grade__c"]].groupby(
    'Contact_Id', as_index=False).first(numeric_only=False)

first_math_test.rename(columns={'max_converted_math': 'first_math_score',
                          "AT_Grade__c": "first_math_grade"}, inplace=True)
```

```python
max_math_test = df[['Contact_Id', 'max_converted_math', "AT_Grade__c"]].groupby(
    'Contact_Id', as_index=False).max()

max_math_test.rename(columns={'max_converted_math': 'highest_math_score',
                          "AT_Grade__c": "highest_math_score_grade"}, inplace=True)
```

```python
df = df.merge(first_gpa, on='Contact_Id')

```

```python
df = df.merge(first_math_test, on='Contact_Id')
```

```python
df = df.merge(max_math_test, on='Contact_Id')
```

```python
df['gpa_growth'] = df.HS_11th_Cum_GPA - df.first_gpa 
```

```python
df['math_test_growth'] = df.highest_math_score - df.first_math_score 
```

```python
df.columns =  df.columns.str.replace(' ', '_')
```

```python
ninth_grade = create_year_to_year_df(df, [9, 10])
```

```python
tenth_grade = create_year_to_year_df(df, [10, 11])
```

```python
eleventh_grade = create_year_to_year_df(df, [11, 12])
```

```python
overall_df_prep = df[~df.ay_spring_status.isin(
        ["Did Not Finish CT HS Program", "Prior to joining CT HS Program"])]

overall_df_prep= overall_df_prep[overall_df_prep.AT_Grade__c != "12th Grade"]
```

```python
overall_df_prep_grouped = overall_df_prep.groupby(['Contact_Id', 'site_short', 'mod_dosage_type']).agg(
    {'HS_11th_Cum_GPA': 'max', 
     'Attendance_Numerator': 'sum',
     'Attendance_Denominator': 'sum',
     'mod_duration_filled': 'sum',
     'max_converted_math': 'max',
     'max_converted_english_reading': 'max',
     'max_converted_english': 'max',
     'max_converted_reading': 'max'
    }
).reset_index()

overall_df_prep_grouped['attendance_rate'] = overall_df_prep_grouped.Attendance_Numerator / overall_df_prep_grouped.Attendance_Denominator
```

```python
overall_workshops = overall_df_prep_grouped[["Contact_Id", "site_short", "mod_dosage_type", "Attendance_Numerator", "attendance_rate", "mod_duration_filled"]].groupby(
        ['Contact_Id', 'site_short', 'mod_dosage_type']).max().unstack('mod_dosage_type')

overall_workshops = rename_df_columns(overall_workshops)
```

```python
overall_df_academics = overall_df_prep[
    ['Contact_Id',
     "High_School_Class__c",
     "HS_11th_Cum_GPA",
     "max_converted_math",
     "max_converted_english_reading",
     "max_converted_english",
     "first_gpa",
     'gpa_growth',
     'first_gpa_grade',
     "highest_math_score",
     "first_math_score",
     'highest_math_score_grade',
     'first_math_grade',
     'math_test_growth']
].groupby("Contact_Id").max()
```

```python
overall_df_final = overall_df_academics.merge(
    overall_workshops, left_index=True, right_index=True, how='left')
```

```python
overall_df_final.reset_index(inplace=True)
overall_df_final.columns =  overall_df_final.columns.str.replace(' ', '_')
```

```python
overall_df_final.dropna(subset=['attendance_rate_Tutoring', 'attendance_rate_Math',
                                'Attendance_Numerator_Math_Blast'], how='all', inplace=True)
```

```python
overall_df_final = overall_df_final[overall_df_final.HS_11th_Cum_GPA > 0 ]
```

```python
overall_df_final[overall_df_final.highest_math_score <= 15][['highest_math_score','first_math_score', 'first_math_grade']]
```

### Save output file into processed directory

Save a file in the processed directory that is cleaned properly. It will be read in and used later for further analysis.

```python
# Save File 1 Data Frame (Or master df)
ninth_grade.to_pickle("../data/processed/ninth_grade.pkl")
tenth_grade.to_pickle("../data/processed/tenth_grade.pkl")
eleventh_grade.to_pickle("../data/processed/eleventh_grade.pkl")
overall_df_final.to_pickle("../data/processed/overall.pkl")
```

```python

```
