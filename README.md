# Introduction

This project implements a real-time wildfire risk analysis and visualization system that processes MODIS satellite data to identify and classify wildfire incidents across the United States. The system uses machine learning clustering to analyze fire patterns and presents risk assessments through an interactive dashboard.

If you are curious about this project even more, you can view the full project proposal at this [link](https://docs.google.com/document/d/1mJfcj2Yqdt3pFBDxfyTddpwHykLodA7CjMqltXxeUvA/edit?usp=sharing).

# Technical Architecture

![Wildfire Risk Prevention Technical Architecture](https://github.com/CS222-UIUC/team-92-project/blob/main/Architecture.png)

Although our project is not fully finished (the database has not yet been implemented), the above architecture would represent the final product of the Wildfire Risk Prevention system if a SQL database and API services were integrated into it in the future.

# Developers

- **Taran Sooranahalli**: Created interactive UI with tables representing Wildfire Data and found datasets
- **Adal Padilla**: Worked on K-Means Clustering ML Model development and training
- **Kevin Xu**: Implemented both frontend and backend test files
- **Varun Madhan**: Developed the heat map, uploaded dataset, and other niche features of the frontend UI

# Environment Setup

## Clone the Repository

In your source directory, run the following command.

```
git clone https://github.com/CS222-UIUC/team-92-project.git
```

## Install & Activate venv

Then after cloning the repo, navigate into the project directory and run the following to install venv.
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix/MacOS

source venv/bin/activate
```

## Running venv

Before running any code, run the following:

```
venv/Scripts/activate/
```

# Development


## Package Management

To prevent errors during compilation, run the following command to install all required packages:
```
pip install pandas numpy scikit-learn geopandas streamlit pydeck plotly matplotlib
```


# Viewing the Predictor

## Run the Application

To run the application, type in the following command
```
streamlit run frontend_risk_display.py
```

In another terminal window, run the following:
```
python3 backend_process.py
```

## Access the Dashboard

Open your web browser and navigate to the following URL:
```
http://localhost:8501
```

# Usage

## Data Source
The system uses MODIS C6.1 satellite data for the USA and Hawaii, tracking:
* Latitude/Longitude coordinates
* Brightness values
* Fire Radiative Power (FRP)
* Acquisition date/time

## Interacting with the Website
* Select data source (default file or URL)
* Adjust clustering parameters
* Filter risk levels and brightness ranges
* View interactive map and statistics
* Download processed data as needed
