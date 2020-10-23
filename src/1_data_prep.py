import pandas as pd
from pathlib import Path
from datetime import datetime
import os
import numpy as np


project_id = "learning-agendas"


# Download data and save to a CSV. If data needs to be refreshed the CSV needs to be deleted.
filename = "./data/raw/test_attendance_data.csv"
table_name = "gathered_test_attendance_at_data"

if os.path.exists(filename):
    # Read from CSV if already written to avoid repeatedly transferring data from BigQuery
    df = pd.read_csv(filename)
    df = df.drop("Unnamed: 0", axis=1)
else:
    query = "SELECT * FROM `learning-agendas.math_tutoring_2020." + table_name + "`"
    df = pd.read_gbq(query, project_id=project_id)
    df.to_csv(filename)


sat_to_act_math = pd.read_csv("./data/raw/sat_to_act_math.csv")
sat_to_act_english_reading = pd.read_csv("./data/raw/sat_to_act_english_reading.csv")


def convert_sat_to_act(sat_score, conversion_file, act_score):

    try:
        conversion_score = (
            conversion_file[sat_score >= conversion_file.SAT]
            .reset_index()
            .iloc[0]["ACT"]
        )
        if pd.isna(act_score):
            return conversion_score
        elif conversion_score >= act_score:
            return conversion_score
        else:
            return act_score
    except:
        return act_score


df["max_converted_math"] = df.apply(
    lambda x: convert_sat_to_act(x["max_sat_math"], sat_to_act_math, x["max_act_math"]),
    axis=1,
)


df["max_converted_english_reading"] = df.apply(
    lambda x: convert_sat_to_act(
        x["max_sat_english"], sat_to_act_english_reading, x["max_act_english_reading"]
    ),
    axis=1,
)


df["max_converted_english"] = df.apply(
    lambda x: convert_sat_to_act(
        x["max_sat_english"], sat_to_act_math, x["max_act_english"]
    ),
    axis=1,
)


df["max_converted_reading"] = df.apply(
    lambda x: convert_sat_to_act(
        x["max_sat_english"], sat_to_act_math, x["max_act_reading"]
    ),
    axis=1,
)


df.loc[pd.isna(df.mod_duration), "mod_duration_filled"] = (
    df.loc[pd.isna(df.mod_duration), "Attendance_Numerator"] * 60
)


df.loc[~pd.isna(df.mod_duration), "mod_duration_filled"] = df.loc[
    ~pd.isna(df.mod_duration), "mod_duration"
]


def create_year_to_year_df(df, grades_num):
    grades = [str(i) + "th Grade" for i in grades_num]

    columns_to_check = [
        "attendance_rate_" + str(grades_num[0]) + "th Grade_Math Blast",
        "attendance_rate_" + str(grades_num[0]) + "th Grade_Tutoring",
        "attendance_rate_" + str(grades_num[0]) + "th Grade_Math",
    ]

    _df = df[(df.AT_Grade__c.isin(grades))]

    _df = _df[
        ~_df.ay_spring_status.isin(
            ["Did Not Finish CT HS Program", "Prior to joining CT HS Program"]
        )
    ]

    _df_academics = (
        _df[_df.AT_Grade__c == grades[1]][
            [
                "Contact_Id",
                "site_short",
                "AT_Grade__c",
                "GPA_semester_cumulative__c",
                "HS_11th_Cum_GPA",
                "max_converted_math",
                "max_converted_english_reading",
                "max_converted_english",
                "max_converted_reading",
            ]
        ]
        .groupby(["Contact_Id", "site_short", "AT_Grade__c"])
        .max()
        .unstack("AT_Grade__c")
    )

    _df_worksops = (
        _df[_df.AT_Grade__c == grades[0]][
            [
                "Contact_Id",
                "site_short",
                "AT_Grade__c",
                "mod_dosage_type",
                "Attendance_Numerator",
                "Attendance_Denominator",
                "attendance_rate",
                "mod_duration_filled",
            ]
        ]
        .groupby(["Contact_Id", "AT_Grade__c", "mod_dosage_type"])
        .sum()
        .unstack(["AT_Grade__c", "mod_dosage_type"])
    )

    _df_academics = rename_df_columns(_df_academics)

    _df_worksops = rename_df_columns(_df_worksops)

    combined_df = _df_academics.merge(
        _df_worksops, left_index=True, right_index=True, how="left"
    )

    combined_df.dropna(subset=columns_to_check, how="all", inplace=True)

    return combined_df.reset_index()


def rename_df_columns(_df):
    _df.columns = _df.columns.to_flat_index()

    new_col_names = ["_".join(i) for i in _df.columns]

    _df.columns = new_col_names
    return _df


ninth_grade = create_year_to_year_df(df, [9, 10])


tenth_grade = create_year_to_year_df(df, [10, 11])


eleventh_grade = create_year_to_year_df(df, [11, 12])


overall_df_prep = df[
    ~df.ay_spring_status.isin(
        ["Did Not Finish CT HS Program", "Prior to joining CT HS Program"]
    )
]

overall_df_prep = overall_df_prep[overall_df_prep.AT_Grade__c != "12th Grade"]


overall_df_prep_grouped = (
    overall_df_prep.groupby(["Contact_Id", "site_short", "mod_dosage_type"])
    .agg(
        {
            "HS_11th_Cum_GPA": "max",
            "Attendance_Numerator": "sum",
            "Attendance_Denominator": "sum",
            "mod_duration_filled": "sum",
            "max_converted_math": "max",
            "max_converted_english_reading": "max",
            "max_converted_english": "max",
            "max_converted_reading": "max",
        }
    )
    .reset_index()
)

overall_df_prep_grouped["attendance_rate"] = (
    overall_df_prep_grouped.Attendance_Numerator
    / overall_df_prep_grouped.Attendance_Denominator
)


overall_workshops = (
    overall_df_prep_grouped[
        [
            "Contact_Id",
            "site_short",
            "mod_dosage_type",
            "Attendance_Numerator",
            "attendance_rate",
            "mod_duration_filled",
        ]
    ]
    .groupby(["Contact_Id", "site_short", "mod_dosage_type"])
    .max()
    .unstack("mod_dosage_type")
)

overall_workshops = rename_df_columns(overall_workshops)


overall_df_academics = (
    overall_df_prep[
        [
            "Contact_Id",
            "High_School_Class__c",
            "HS_11th_Cum_GPA",
            "max_converted_math",
            "max_converted_english_reading",
            "max_converted_english",
        ]
    ]
    .groupby("Contact_Id")
    .max()
)


overall_df_final = overall_df_academics.merge(
    overall_workshops, left_index=True, right_index=True, how="left"
)


overall_df_final.reset_index(inplace=True)


overall_df_final.dropna(
    subset=[
        "attendance_rate_Tutoring",
        "attendance_rate_Math",
        "Attendance_Numerator_Math Blast",
    ],
    how="all",
    inplace=True,
)


overall_df_final = overall_df_final[overall_df_final.HS_11th_Cum_GPA > 0]


# ### Save output file into processed directory
#
# Save a file in the processed directory that is cleaned properly. It will be read in and used later for further analysis.


# Save File 1 Data Frame (Or master df)
ninth_grade.to_pickle("./data/processed/ninth_grade.pkl")
tenth_grade.to_pickle("./data/processed/tenth_grade.pkl")
eleventh_grade.to_pickle("./data/processed/eleventh_grade.pkl")
overall_df_final.to_pickle("./data/processed/overall.pkl")

