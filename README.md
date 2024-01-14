# Combine multiple consuption profiles and select the solar panel needed
https://cer-configurator.onrender.com
This project is a web-based dashboard that provides visualizations and analysis of energy consumption and production data. It utilizes the Dash framework for creating interactive data visualization applications.

# Project Overview
The Energy Consumption and Production Dashboard aims to assist users in analyzing and understanding energy consumption and production patterns. It provides insights into hourly and monthly energy consumption and production data.

The dashboard retrieves data from CSV files containing hourly consumption and production records. It uses the Pandas library for data manipulation and analysis, as well as the Plotly and Dash libraries for creating interactive visualizations and building the web application.

# Key Features
The Energy Consumption and Production Dashboard offers the following features:

✅ Hourly Consumption Visualization: The dashboard displays line charts that represent the hourly energy consumption for different consumer profiles. Users can select specific consumer profiles to compare their energy consumption patterns over time.

✅ Monthly Consumption Visualization: The dashboard provides bar charts that illustrate the monthly energy consumption for each consumer profile. Users can explore the trends and variations in energy consumption across different months and years.

✅ Hourly Production Visualization: The dashboard includes line charts that depict the hourly energy production for different energy modules. Users can select specific energy modules to analyze their production patterns and identify peak production hours.

✅ Monthly Production Visualization: The dashboard presents bar charts that show the monthly energy production for each energy module. Users can examine the variations in energy production across different months and years.

✅ Interactive Selection: Users can interact with the dashboard by selecting specific energy modules, consumer profiles, and years to visualize the corresponding data. The dashboard dynamically updates the charts based on the user's selections.

# How to Use
To run the Energy Consumption and Production Dashboard locally, follow these steps:

Install the required dependencies by running pip install dash dash_bootstrap_components pandas pandasql plotly requests numpy in your command line.

Download the CSV files containing the hourly consumption and production data and place them in the same directory as the project files.

Open the Python script and run it. This will launch a local web server and display the dashboard in your web browser.

Use the dropdown menus to select the desired energy modules, consumer profiles, and years to visualize the corresponding data. The charts will update dynamically based on your selections.

Explore the visualizations and analyze the energy consumption and production patterns.

# Repository Structure
The repository for the Energy Consumption and Production Dashboard contains the following files:

dashboard.py: The main Python script that defines the dashboard layout, callbacks, and data processing functions.
hourly_consumption - 2022.csv: CSV file containing hourly consumption data for the year 2022.
hourly_prod - 2022.csv: CSV file containing hourly production data for the year 2022.
README.md: Documentation file explaining the project and its features (this file).
Other necessary files and directories for running the Dash application.
