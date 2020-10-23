import seaborn as sns
import matplotlib.pyplot as plt


def create_regression_plots_row(
    df, grade, x_data, y_variable, row, fig, axs, y_label, x_label_addition, colors
):
    x_variables = ["Tutoring", "Math_Blast", "Math", "Other_Workshop"]
    x_data_columns = [x_data + "_" + str(grade) + "th Grade_" + i for i in x_variables]

    y_label_exta = str(grade + 1) + "th Grade " + y_label

    y_column = y_variable + "_" + str(grade + 1) + "th Grade"

    for i in range(len(x_data_columns)):
        x_label = str(grade) + "th Grade " + x_variables[i] + " " + x_label_addition
        sns.regplot(
            data=df,
            x=x_data_columns[i],
            y=y_column,
            ax=axs[row, i],
            line_kws={"color": "#666666"},
            color=colors[i],
            lowess=False,
            robust=False,
            order=1,
        )
        if i == 0:
            axs[row, i].set(xlabel=x_label, ylabel=y_label_exta)
        else:
            axs[row, i].set(xlabel=x_label, ylabel="")


def create_regression_grid(df, grade):
    fig, axs = plt.subplots(4, 4, figsize=(8, 10), sharey="row")

    fig.suptitle(str(grade) + "th Grade Plots")
    create_regression_plots_row(
        df,
        grade,
        "Attendance_Numerator",
        "GPA_semester_cumulative__c",
        0,
        fig,
        axs,
        "GPA",
        "(Sessions)",
        colors,
    )

    create_regression_plots_row(
        df,
        grade,
        "Attendance_Numerator",
        "max_converted_math",
        1,
        fig,
        axs,
        "Math Test Score",
        "(Sessions)",
        colors,
    )

    create_regression_plots_row(
        df,
        grade,
        "mod_duration_filled",
        "GPA_semester_cumulative__c",
        2,
        fig,
        axs,
        "Math Test Score",
        "(Minutes)",
        colors,
    )

    create_regression_plots_row(
        df,
        grade,
        "mod_duration_filled",
        "max_converted_math",
        3,
        fig,
        axs,
        "Math Test Score",
        "(Minutes)",
        colors,
    )
    plt.show()


def create_regression_plots_overall(
    df, x_data, y_variable, fig, axs, y_label, x_label_addition, colors, row
):
    x_variables = ["Tutoring", "Math_Blast", "Math", "Other_Workshop"]
    x_data_columns = [x_data + "_" + i for i in x_variables]

    for i in range(len(x_data_columns)):
        _df_sub = df[df[x_data_columns[i]] > 0]
        x_label = x_variables[i] + " " + x_label_addition
        sns.regplot(
            data=_df_sub,
            x=x_data_columns[i],
            y=y_variable,
            ax=axs[row, i],
            line_kws={"color": "#666666"},
            color=colors[i],
        )
        if i == 0:
            axs[row, i].set(xlabel=x_label, ylabel=y_label)
        else:
            axs[row, i].set(xlabel=x_label, ylabel="")


def create_overall_chart(
    df_1,
    df_2,
    x_1,
    x_2,
    y_1,
    y_2,
    x_1_label,
    x_2_label,
    y_1_label,
    y_2_label,
    title,
    colors,
):

    fig, axs = plt.subplots(4, 4, figsize=(7, 8), sharey="row")
    fig.suptitle(title)

    create_regression_plots_overall(
        df_1, x_1, y_1, fig, axs, y_1_label, x_1_label, colors, 0
    )
    create_regression_plots_overall(
        df_2, x_2, y_2, fig, axs, y_2_label, x_2_label, colors, 1
    )
    create_regression_plots_overall(
        df_1, x_1, y_1, fig, axs, y_1_label, x_1_label, colors, 2
    )
    create_regression_plots_overall(
        df_2, x_2, y_2, fig, axs, y_2_label, x_2_label, colors, 3
    )

