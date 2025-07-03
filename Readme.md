# 🛠️ Raw HTML Data to Cleaned & Formatted Data Pipeline

## Overview

This project is designed to build an end-to-end pipeline for extracting raw HTML data from e-commerce websites, storing it, cleaning and formatting it, and ultimately visualizing it on a dashboard. The architecture leverages AWS EC2 instances, MongoDB for storage, and AWS SageMaker for data processing and visualization.

---

## 📊 Architecture

![System Architecture](docs/architecture.png)

*Image: High-level architecture showing the flow from Scraper Instance to Dashboard via MongoDB and SageMaker.*

---

## ✅ What’s Completed

- **Architecture Designed:**  
  Clear visual and logical flow established for the data pipeline, from scraping to dashboard visualization (see image above).

- **Scraper Instance (EC2):**
  - Develops and deploys a scraper capable of extracting raw HTML from target URLs.
  - Saves scraped raw HTML directly to a MongoDB instance.

- **MongoDB Instance:**
  - Set up for storing the scraped raw HTML data.
  - Configured to be accessible by the SageMaker processing instance.

---

## 🚀 Implemented Features

This repository now contains working examples for each component in the architecture.

1. **SageMaker Data Processing (Instance 1)**
   - `sagemaker/process_raw_html.py` pulls raw HTML from MongoDB and extracts basic fields such as product title and price.
   - Cleaned documents are written to a second MongoDB instance.

2. **User Preference Handling & Analysis (Instance 2)**
   - `sagemaker/analyze_data.py` exposes a simple function for querying the processed data with optional price filters.
   - `sagemaker/api.py` provides a FastAPI endpoint so the dashboard can request analyses.

3. **Dashboard**
   - `dashboard/main.py` lets users submit URLs for scraping and request aggregated results from SageMaker.

4. **Automation and Scaling**
   - A root `docker-compose.yaml` spins up the scraper, two MongoDB instances, both SageMaker services and the dashboard for local testing.

5. **Logging & Monitoring**
   - Each component prints progress to the console and can easily be extended with more robust logging.

---

## 🏗️ Next Steps

- Expand the HTML parser to extract additional fields and handle more websites.
- Add authentication and better error handling across services.
- Explore autoscaling strategies for production workloads.
- Improve documentation and provide deployment scripts for cloud environments.

---

## 💬 How to Contribute

If you’d like to help or have ideas, please open an issue or pull request!

---

## 📁 Project Structure

```

project/
│
├── Scraper/               # Scraper service
├── sagemaker/             # Data processing & analysis services
├── dashboard/             # Simple frontend API
├── mongodb/               # (placeholder for DB configs)
├── docs/                  # Documentation and diagrams
├── docker-compose.yaml    # Local orchestration
└── README.md

```

---

**Contact:**  
For queries or collaboration, feel free to open an issue or contact the maintainer.


