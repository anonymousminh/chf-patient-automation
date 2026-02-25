# CHF Patient Monitoring Agent - Elasticsearch Hackathon 2026

An AI-powered agent using Elasticsearch to proactively monitor high-risk Congestive Heart Failure (CHF) patients and help clinical teams prevent hospital readmissions.

---

## 💡 The Problem

Congestive Heart Failure (CHF) is a leading cause of hospital readmissions. After being discharged, patients require close monitoring, but nursing teams can often only contact a small percentage of their patient population daily. This leaves a significant gap in care, where high-risk individuals can decline rapidly, leading to costly and often preventable emergency room visits. Our project tackles this problem head-on.

## 🚀 Our Solution

We have built an intelligent monitoring system on the Elastic Stack that acts as a "virtual nurse," watching over the entire discharged patient population 24/7. The system consists of two main components:

1.  **The AI Agent ("Florence")**: A natural-language interface where nurses can ask for a daily risk assessment. The agent uses a powerful ES|QL tool to analyze patient data and identify individuals who are at high risk based on clinical indicators.

2.  **The Clinical Dashboard**: A real-time Kibana dashboard that provides an at-a-glance overview of the entire patient cohort, including key metrics, population trends, and a clear, actionable list of high-risk patients who require immediate follow-up.

## ✨ Key Features

*   **AI-Powered Risk Stratification**: Uses an Elastic AI Agent with a custom ES|QL tool to analyze time-series data for risk factors like rapid weight gain and medication non-adherence.
*   **Natural Language Interface**: Nurses can interact with the system by simply asking, "Who are my highest-risk patients today?"
*   **Real-Time Clinical Dashboard**: A comprehensive Kibana dashboard provides a single-pane-of-glass view of patient status, population trends, and actionable alerts.
*   **Proactive Monitoring**: Shifts the care model from reactive to proactive, allowing clinical teams to focus their limited resources on the patients who need it most.

## 🛠️ Technical Implementation

*   **Backend**: Elasticsearch Serverless
*   **Data**: Synthetic patient data generated with a Python script (Faker library).
*   **Core Logic**: ES|QL query for risk stratification, pre-calculated metrics for performance.
*   **AI Agent**: Built using Elastic's Agent Builder with a custom tool.
*   **Dashboard**: Created in Kibana Lens.

## 🏃‍♀️ How to Run This Project

1.  **Set up Elastic Cloud**: Create a Serverless project on Elastic Cloud.
2.  **Update Credentials**: Modify the connection details in `data/generate_synthetic_data.py`.
3.  **Run the Script**: Execute `python data/generate_synthetic_data.py` to create the index and ingest the data.
4.  **Import Kibana Objects**: Import the `kibana/dashboard_export.ndjson` file to create the agent, dashboard, and all associated visualizations.
5.  **Interact**: Go to the Agent chat or the Dashboard to see the system in action!

## CHF Patient Monitoring Dashboard
<img width="1502" height="859" alt="Patient Monitoring Dashboard" src="https://github.com/user-attachments/assets/f3948309-4de5-436c-bc87-e3bf44e35b65" />


---

*This project was created for the Elasticsearch Hackathon 2026.*
