This repository contains an AWS Lambda-based workflow designed to analyze weekly Spotify listening habits and provide music recommendations. The system integrates Spotify and Last.fm APIs, leveraging serverless AWS services, Docker for containerization, and machine learning for recommendations.

Features

Automated Data Collection: Fetches user's top tracks weekly using Spotify's API.

Data Enrichment: Retrieves detailed track similarity and artist information using Last.fm.

Serverless Architecture: Utilizes AWS Lambda, EventBridge, and S3 for scalable and cost-effective processing.

Dockerized Workflow: Ensures easy deployment and consistent execution across environments.

Machine Learning Recommendations: Implements content-based recommendation models (e.g., cosine similarity, K-Nearest Neighbors) based on artist metadata and track similarity.

Tech Stack

AWS Lambda

AWS S3

AWS EventBridge

Docker

Spotify API (Spotipy)

Last.fm API (pylast)

Python (pandas, boto3)

Setup

Environment Variables

Ensure these variables are defined:

S3_BUCKET

SPOTIPY_CLIENT_ID

SPOTIPY_CLIENT_SECRET

SPOTIFY_REFRESH_TOKEN

LASTFM_API_KEY

LASTFM_API_SECRET

LASTFM_USERNAME

LASTFM_PASSWORD_HASH

Deployment

Deploy using Docker for AWS Lambda or use AWS SAM/Serverless framework.

Usage

Automated via AWS EventBridge triggers weekly. Outputs a CSV file to the designated S3 bucket containing track metadata and recommendations.

