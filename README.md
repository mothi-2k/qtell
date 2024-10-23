
# Qtell: Chatbot with Retrieval-Augmented Generation (RAG) Powered by Gemini

## Overview
[**Qtell**](https://qtell-latest.onrender.com/) is an intelligent chatbot designed to answer general questions and handle user-uploaded PDFs. By leveraging a **Retrieval-Augmented Generation (RAG)** approach integrated with **Gemini**, Qtell provides accurate responses, retrieves contextually relevant information, and analyzes documents for users. It is suitable for a wide range of use cases, including resume analysis for recruiters and document processing.

## Features
- **General Question Answering**: Powered by **Gemini** to provide accurate answers based on general knowledge.
- **PDF Upload and Analysis**: Users can upload PDFs, and Qtell will intelligently extract and respond to queries based on the document contents.
- **Resume Analysis for Recruiters**: Qtell can quickly analyze resumes, highlighting relevant qualifications to streamline the hiring process.
- **Document Summarization and Extraction**: Summarizes and retrieves key information from uploaded documents for easier reference.
- **Secure User Authentication**: Utilizes **JWT** for secure sign-up and login.
- **Chat History Maintenance**: Stores chat history in **MongoDB** to provide continuity in conversations.

## Tech Stack
- **Frontend**: Modern UI with dynamic design for both desktop and mobile devices.
- **Backend**: Developed using **Flask**, with the chatbot powered by **Gemini**.
- **Database**: 
  - **PostgreSQL** for managing structured user details.
  - **PGVector** for handling PDF file embeddings.
  - **MongoDB** for storing and retrieving dynamic chat histories.
- **CI/CD**: Automated pipeline with **GitHub Actions** for continuous integration and delivery. Builds Docker images, pushes them to **GitHub Container Registry**, and deploys to **Render.io**.
- **Deployment**: Hosted on **Render.io** to provide seamless and reliable performance.

## Getting Started

### Prerequisites
1. **Python 3.8+**
2. **Docker**
3. **Flask** and necessary Python libraries from `requirements.txt`
4. **PostgreSQL** and **MongoDB** instances
5. **Render.io** account for deployment

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/mothi-2k/qtell.git
    cd qtell
    ```

2. Install the necessary dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up PostgreSQL and MongoDB:
    - Configure your PostgreSQL database for user details and embeddings.
    - Configure MongoDB for chat history storage.

4. Add environment variables for **JWT** secret, **PostgreSQL**, and **MongoDB** credentials in `.env` file:
    ```bash
    JWT_SECRET_KEY=your_jwt_secret_key
    POSTGRESQL_URI=your_postgresql_uri
    MONGODB_URI=your_mongodb_uri
    ```

5. Start the Flask app:
    ```bash
    flask run
    ```

6. Optionally, use Docker for containerized deployment:
    ```bash
    docker build -t qtell .
    docker run -d -p 5000:5000 qtell
    ```

### Deployment
This project uses **Render.io** for deployment with a CI/CD pipeline managed by **GitHub Actions**:
- On every new commit or tag creation, GitHub Actions triggers the creation of a Docker image.
- The image is pushed to **GitHub Container Registry**.
- The app is automatically deployed to **Render.io** with the latest updates.

### PDF Embeddings
We use **PGVector** in PostgreSQL to store embeddings of user-uploaded PDFs for efficient query processing and contextual retrieval during conversations.

## How It Works
1. **User Authentication**: Secure sign-up and login with **JWT** tokens.
2. **Chatbot Interaction**: Users can ask general questions or upload PDFs for specific queries.
3. **PDF Analysis**: For uploaded PDFs, Qtell uses RAG to extract relevant information based on user input.
4. **Resume Analysis**: Recruiters can upload resumes to receive key qualification summaries.
5. **Continuous Deployment**: CI/CD ensures seamless deployment on each update, with Docker images automatically built and deployed on **Render.io**.

## Use Cases
- **Resume Analysis for Recruiters**: Streamlines hiring by analyzing key qualifications in resumes.
- **Document Analysis**: Summarizes and extracts key information from PDFs.
- **Educational Tool**: Assists students with analyzing lecture notes and study materials.

## Architecture diagram
![Qtell-ad drawio](https://github.com/user-attachments/assets/eee47f2b-18ca-4359-90e0-e2d06d843df0)

  
