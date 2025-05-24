# Real-time Air Quality Index (AQI) Prediction System with DevOps Integration

## Project Overview

This project is a **real-time Air Quality Monitoring and Forecasting System** that integrates live environmental data ingestion, machine learning forecasting, and DevOps automation. Users can view real-time AQI, get 7-day AQI forecasts, receive health-based recommendations, and interact with a full-stack system powered by modern DevOps practices.

## Key Features

- **Live AQI Monitoring**: Fetches real-time air quality data from government APIs every hour using Kubernetes CronJobs.
- **AQI Forecasting**: LSTM-based machine learning model predicts AQI for the next 7 days based on historical pollutant data.
- **Smart Health Recommendations**: Uses Google GenAI to provide dynamic health suggestions based on AQI trends and user health data.
- **Automated Data Pipeline**: Hourly CronJob to ingest and update AQI data.
- **DevOps Integration**: Full CI/CD pipeline using Jenkins, Docker, Ansible, and Kubernetes (Minikube) with Ingress routing and log visualization via the ELK Stack.

## Tech Stack

- **Frontend**: Flask (HTML Templates)
- **Backend**: Flask APIs
- **ML Model**: LSTM (Keras), trained on 10 years of AQI data
- **Database**: PostgreSQL
- **DevOps**:
  - CI/CD: Jenkins
  - Containerization: Docker
  - Configuration Management: Ansible
  - Orchestration: Kubernetes + Minikube
  - Monitoring: ELK Stack
  - Secrets/Config Management: Kubernetes Secrets, ConfigMaps
  - Auto-scaling: HPA
  - Scheduled Jobs: CronJobs

## Folder Structure

- `frontend/`: Flask app serving the UI with authentication and data visualization
- `backend/`: Flask API handling user requests and data communication
- `model/`: LSTM model served as a microservice
- `k8s/`: Kubernetes manifests for deployments, services, HPA, PVs, secrets, etc.
- `jenkins/`: Jenkinsfile for CI/CD pipeline
- `scripts/`: Data ingestion and initialization scripts

## ML Model Overview

- **Input Features**: PM10, PM2.5, NO2, NH3, SO2, CO, OZONE, city_encoded, dayofyear, month
- **Model**: LSTM (1 hidden layer), trained on 30-day sliding window
- **Output**: AQI predictions for next 7 days
- **Accuracy**: >80% on test data
- **Artifacts**: `lstm_model.h5`, `scaler_x.pkl`, `scaler_y.pkl`, `city_encoder.pkl`


## DevOps Details

- **Docker**: All services containerized for consistency
- **Jenkins**: Automates code build, testing, and deployment
- **Kubernetes**:
  - Backend, frontend, model, DB, and CronJobs deployed as pods
  - HPA for backend autoscaling
  - Ingress for routing (e.g., `http://aqi.spe/`)
  - Secrets, PV/PVC for secure and persistent data handling
- **ELK Stack**: Visualizes logs and system metrics (CronJob stats, app logs)

## Innovations

- Embedded temporal and city metadata into the LSTM for better trend learning
- GenAI-based dynamic health recommendations based on user profile and AQI levels
- Auto-retraining future scope based on prediction drift

## Future Scope

- Automate model retraining via Jenkins when accuracy drops
- Integrate real-time notifications for AQI alerts
- Expand to more cities and pollutants

## Conclusion

This project demonstrates a robust blend of machine learning, real-time data processing, and DevOps to build a scalable, maintainable, and impactful AQI monitoring system. It serves as a blueprint for environmental applications that require end-to-end automation and intelligence.