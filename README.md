
---

# THE-AI-MAVERICKS  
**AI-Driven and Blockchain-Enabled Disaster Relief: An Integrated Framework for Real-Time Route Optimization, Transparent Supply Chain Management, and Remote Connectivity**

## Overview

This project is an AI-powered dashboard designed to assist with real-time disaster response and planning. The tool leverages machine learning models to predict supply needs (such as food, water, medicines, and clothing) based on disaster details, and integrates with the Google Maps API for route planning and visualization.

## Features

- **Supply Prediction**: Predicts the amount of food, water, medicine, and clothing needed during a disaster based on its severity, affected population, and other factors.
- **Route Planner**: Helps plan efficient delivery routes for disaster relief supplies, optimized for traffic and distance using the Google Maps API.
- **Interactive User Interface**: Built with Streamlit for easy interaction and visualization, allowing for real-time updates and decision-making.

## Prerequisites

- Python 3.7+
- Google Maps API key for route planning
- Mediastack API key for accessing real-time news and updates

## Installation

### 1. Clone the Repository

Open your terminal and run the following command:

```bash
git clone https://github.com/DebarghaSamanta/THE-AI-MAVERICKS.git
```

### 2. Navigate to the Project Directory

```bash
cd Disaster-Relief-AI-Dashboard
```

### 3. Set Up the Virtual Environment

- If you’re using `venv`:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Google Maps API

- Create a `.env` file in the project root and add your Google Maps API key:

```
GOOGLE_API_KEY=your_google_api_key_here
```

Replace `your_google_api_key_here` with your actual Google Maps API key.

### 6. Set Up Mediastack API

- In the same `.env` file, add your Mediastack API key:

```
MEDIASTACK_API_KEY=your_mediastack_api_key_here
```

Replace `your_mediastack_api_key_here` with your actual Mediastack API key.

### 7. Run the Application

```bash
streamlit run app.py
```

This will start the dashboard on your local machine. You can view it in your browser at `http://localhost:8501`.

## Folder Structure

```
Disaster-Relief-AI-Dashboard/
│
├── app.py                    ← Main Streamlit dashboard script
├── pages/
│   ├── 1_Supply_Prediction.py
│   └── 2_Route_Planner.py
├── images/                   ← Folder for storing images like logos
│   └── image.png
├── models/                   ← Folder for storing trained models
│   ├── food_water_model.pkl
│   └── supply_model.pkl
├── data/                     ← Folder for storing input data files (CSV, etc.)
│   ├── synthetic_food_water_data.csv
│   └── synthetic_medicine_clothing_data.csv
├── .gitignore                ← Git ignore file
├── requirements.txt          ← Project dependencies
├── readme.md                 ← This README file
└── .env                      ← Environment variables (add your API keys here)
```

## Usage

- **Supply Prediction**: Navigate to the "📦 Predict Supplies" tab to enter disaster details and predict the necessary supplies.
- **Route Planner**: Navigate to the "🗺️ Plan Delivery Route" tab to enter start and end locations, and the tool will generate an optimized route using the Google Maps API.

## Contributing

We welcome contributions! To contribute, please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes and commit them (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-name`)
5. Create a new pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io) for the framework
- [Google Maps API](https://developers.google.com/maps/documentation) for route planning functionality
- [Mediastack](https://mediastack.com) for real-time news updates
- [Pandas](https://pandas.pydata.org) and [Scikit-learn](https://scikit-learn.org) for machine learning and data processing

---
