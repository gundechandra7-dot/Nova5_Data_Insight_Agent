# Nova5_Data_Insight_Agent
#This Nova5_Data_Insight_Agent is my personal Data analyzing and visualizing ai agent.

# Nova5 — AI Data Insight Agent

**Nova5** is an AI-powered data analysis agent designed to help users explore, understand, and visualize datasets using natural language.

Instead of manually performing every step of data analysis, users can upload a dataset and interact with Nova5 to generate meaningful insights, statistical summaries, data-quality reports, and visualizations.

## 🚀 Features

 **Multi-format Data Support**
  Supports CSV, Excel, JSON, Parquet, and SQLite datasets.

 **AI-Powered Data Analysis**
  Ask questions about your dataset using natural language and receive data-driven answers.

 **Automated Data Profiling**
  Analyzes dataset structure, data types, missing values, duplicates, statistical summaries, correlations, and potential outliers.

 **Smart Visualizations**
  Automatically generates suitable charts and visualizations based on the dataset and user's questions.

 **Data Quality & Health Analysis**
  Identifies missing data, duplicate records, unusual values, and other potential data-quality issues.

 **Code-Assisted Analysis**
  Nova5 can generate and execute Python-based analysis for more complex analytical questions.

 **AI + Offline Analysis**
  Provides AI-powered analysis when an API is configured and supports heuristic analysis when AI services are unavailable.

 **Report Generation**
  Generate analysis reports containing insights, statistics, and visualizations.

 **Sample Datasets**
  Includes sample datasets for testing different analysis capabilities.

## 🛠️ Technology Stack

* **Python**
* **Streamlit**
* **Pandas**
* **NumPy**
* **Plotly**
* **Google Gemini API**
* **DuckDB**
* **PyArrow**
* **SQLite**

## 🔄 How Nova5 Works

Upload Dataset
      ↓
Data Ingestion
      ↓
Data Profiling & Quality Checks
      ↓
AI Analysis
      ↓
Insight Generation
      ↓
Visualization
      ↓
Report Generation



## 💡 Example Questions
After uploading a dataset, users can ask questions such as:

* What are the main insights from this dataset?
* Which category has the highest sales?
* Are there any missing values?
* Find unusual or outlier records.
* Show the trend over time.
* Which variables are strongly correlated?
* Create a visualization for this data.
* Give me a summary of the dataset.

## 🎯 Project Goal
The goal of Nova5 is to make data analysis more accessible by combining **AI, Python-based analytics, automated profiling, and visualization** into a single interactive application.
It is designed as a learning and portfolio project demonstrating how an AI agent can assist with practical data-analysis workflows.

## ⚙️ Getting Started
Clone the repository:

```bash
git clone https://github.com/gundechandra7-dot/Nova5_Data_Insight_Agent.git
cd Nova5_Data_Insight_Agent

Install dependencies:

```bash
pip install -r requirements.txt

Configure your API key using an environment variable:

```text
GEMINI_API_KEY=your_api_key_here

Run the application:

```bash
streamlit run app.py

## 🔐 Security
Do not commit API keys or other secrets to GitHub.
Use a `.env` file for local development and keep it excluded through `.gitignore`.

## 📌 Project Status
Nova5 is an actively developing project. Future improvements may include more advanced AI reasoning, richer dashboards, improved conversational memory, additional data sources, and expanded analytical capabilities.

**Nova5 — Upload your data. Ask questions. Discover insights.**
