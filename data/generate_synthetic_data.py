import json
import random
from datetime import datetime, timedelta
from faker import Faker
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env
load_dotenv()


# --- Configuration ---
INDEX_NAME = "patients"
NUM_PATIENTS = 100
DAYS_OF_DATA = 30

# --- Intialize Libraries ---
fake = Faker()

# --- Patient Profile Definitions ---
PATIENT_PROFILES = {
    "stable": {"weight": 0.7, "risk_factor": "none"},
    "high_risk_weight_gain": {"weight": 0.2, "risk_factor": "weight_gain"},
    "non_adherent": {"weight": 0.1, "risk_factor": "medication"}
}

def choose_profile():
    """Choose a patient profile based on predefined weights"""
    profiles = list(PATIENT_PROFILES.keys())
    weights = [p["weight"] for p in PATIENT_PROFILES.values()]
    return random.choices(profiles, weights=weights, k=1)[0]

# --- Main Data Generation Logic ---
def generate_all_patient_data():
    """Generates a complete dataset for all patients over 30 days"""
    all_patients_records = []

    for _ in range(NUM_PATIENTS):
        # Create a base profile for the patient
        patient_id = fake.uuid4()
        profile_type = choose_profile()

        base_patient_info = {
            "patient_id": patient_id,
            "age": random.randint(65, 95),
            "gender": random.choice(["Male", "Female"]),
            "comorbidities": random.sample(["Diabetes", "Hypertension", "Chronic Kidney Disease", "COPD"], k=random.randint(0,3)),
            "previous_readmissions": random.randint(0,5),
            "discharge_date": (datetime.now() - timedelta(days=random.randint(30, 90))).isoformat(),
            "profile_type": profile_type
        }

        # 2. Generate 30 days of time-series data for this patient
        daily_records = generate_daily_time_series(base_patient_info)
        all_patients_records.extend(daily_records)
    
    return all_patients_records

def generate_daily_time_series(base_info):
    """Generates 30 days of data for a single patient based on their profile"""
    records = []
    daily_weights = []
    daily_adherence = []
    current_weight = random.uniform(150.0, 250.0)
    discharge_date = datetime.fromisoformat(base_info["discharge_date"])

    # Specific setup for high-risk profiles
    weight_gain_start_day = random.randint(5, 20) if base_info["profile_type"] == "high_risk_weight_gain" else -1
    non_adherent_start_day = random.randint(5, 20) if base_info["profile_type"] == "non_adherent" else -1

    for day in range(DAYS_OF_DATA):
        record_date = discharge_date + timedelta(days=day)
        daily_record = base_info.copy()
        daily_record["date"] = record_date.isoformat()
        days_since_discharge = (record_date - discharge_date).days

        # --- Simulate Data Based on Profile
        medication_adherence = True

        # Stable patient fluctuations
        current_weight += random.uniform(-0.5, 0.5)
        symptoms = {
                "symptom_shortness_of_breath": random.randint(1, 3),
            "symptom_fatigue": random.randint(1, 4),
            "symptom_swelling": random.randint(1, 3)
        }

        # High-Risk: Sudden Weight Gain
        if base_info["profile_type"] == "high_risk_weight_gain" and day >= weight_gain_start_day:
            current_weight += random.uniform(1.0, 2.5) # Simulate rapid gain
            symptoms["symptom_shortness_of_breath"] = random.randint(4, 8)
            symptoms["symptom_swelling"] = random.randint(4,8)
        
        # High-Risk: Medication Non_Adherence
        if base_info["profile_type"] == "non_adherent" and day >= non_adherent_start_day:
            medication_adherence = False # Miss medication for 3 consecutive days
            symptoms["symptom_fatigue"] = random.randint(5, 9)

        daily_weights.append(current_weight)
        daily_adherence.append(medication_adherence)

        # --- Pre-calculate rolling metrics ---
        weight_gain_over_3_days = 0
        if day >= 3:
            weight_3_days_ago = daily_weights[day - 3]
            weight_gain_over_3_days = current_weight - weight_3_days_ago

        consecutive_missed_meds = 0
        if not medication_adherence and day >= 1 and not daily_adherence[day - 1]:
            consecutive_missed_meds = 2

        # --- Populate final record ---
        daily_record.update({
            "weight": round(current_weight, 2),
            "blood_pressure_systolic": random.randint(110, 160),
            "blood_pressure_diastolic": random.randint(70, 100),
            "heart_rate": random.randint(60, 100),
            "oxygen_saturation": round(random.uniform(92, 99), 2),
            "medication_adherence": medication_adherence,
            "weight_gain_over_3_days": round(weight_gain_over_3_days, 2),
            "consecutive_missed_meds": consecutive_missed_meds,
            "days_since_discharge": days_since_discharge
        })

        daily_record.update(symptoms)

        records.append(daily_record)

    return records

# --- Elasticsearch Ingestion
def ingest_data(es_client, index, data):
    """Deletes, creates, and ingests data into the specified index"""
    try:
        if es_client.indices.exists(index=index):
            print(f"Deleting old index '{index}'...")
            es_client.indices.delete(index=index)
        
        print(f"Creating new index '{index}'...")
        mapping_path = os.path.join(os.path.dirname(__file__), "..", "elasticsearch", "index_mapping.json")
        with open(mapping_path) as f:
            mapping = json.load(f)
        es_client.indices.create(index=index, body=mapping)

        print(f"Ingesting {len(data)} documents...")
        actions = [
            {
                "_index": index,
                "_source": record
            }
            for record in data
        ]

        success, _ = bulk(es_client, actions, raise_on_error=True)
        print(f"Successfully ingested {success} documents")
    except Exception as e:
        print(f"An error occurred: {e}")
    

# --- Main Excution Block
if __name__ == "__main__":
    print("Starting synthetic data generation...")
    all_data = generate_all_patient_data()
    print(f"Generated {len(all_data)} total records for {NUM_PATIENTS} patients")

    # Connect to Elasticsearch
    if not (os.getenv("ELASTICSEARCH_ENDPOINT") and os.getenv("API_KEY")):
        print("\nWARNING: ELASTICSEARCH_ENDPOINT and API_KEY must be set in your environment (.env or exported). Skipping ingestion.")
        sys.exit(0)
    else:
        print("\nConnecting to Elasticsearch...")
        es = Elasticsearch(
            os.getenv("ELASTICSEARCH_ENDPOINT"),
            api_key=os.getenv("API_KEY")
        )
        ingest_data(es, INDEX_NAME, all_data)
