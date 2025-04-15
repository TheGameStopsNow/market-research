# Deployment Guide: TWSCA GME Analysis Dashboard

This guide provides instructions for deploying the Streamlit application located in the `extras/` directory.

## Prerequisites

*   **GitHub Repository:** You need your project code hosted on GitHub (or a similar Git provider).
*   **Data File:** The deployment platform needs access to the required data file (`extras/data_streamlit/combined_weekly_2024_2025.csv`). Since the `extras/data_streamlit/` directory is in `.gitignore`, you have a few options:
    *   **Option A (Small Data): Remove `extras/data_streamlit/` from `.gitignore`**
        *   If your `combined_weekly_2024_2025.csv` file is relatively small (e.g., under 25MB, check platform limits), you can remove the `extras/data_streamlit/` line from your `.gitignore` file, commit the data file (inside the `extras/data_streamlit/` directory), and push it to your repository. The deployment platform can then directly use it.
        *   **Caution:** Be mindful of repository size limits and avoid committing very large files directly to Git.
    *   **Option B (External Hosting): Load Data from URL**
        *   Host your `combined_weekly_2024_2025.csv` file somewhere publicly accessible (e.g., GitHub Gist, AWS S3 public bucket, Google Drive link - check sharing settings).
        *   Modify the `load_data` function in `extras/streamlit-twsca.py` to read the CSV from the URL instead of the local file path.
        ```python
        # Example modification in extras/streamlit-twsca.py
        import pandas as pd
        import streamlit as st
        import os

        @st.cache_data
        def load_data():
            # Replace with the actual URL to your hosted CSV file
            data_url = "YOUR_PUBLIC_CSV_URL_HERE"
            try:
                df = pd.read_csv(data_url)
                df["date"] = pd.to_datetime(df["date"]) # Adjust column name if needed
                return df
            except Exception as e:
                st.error(f"Error loading data from {data_url}: {str(e)}")
                return None
        ```
    *   **Option C (Platform Specific):** Some platforms might offer ways to upload data files separately or mount storage. Consult the specific platform's documentation.

## Deployment Platforms

### Streamlit Community Cloud (Recommended)

Streamlit Community Cloud is a free hosting service specifically for Streamlit apps.

1.  **Ensure Prerequisites:** Make sure your code is on GitHub and you've decided how to handle the data file (see Prerequisites above).
2.  **Sign Up/Log In:** Go to [share.streamlit.io](https://share.streamlit.io/) and sign up or log in using your GitHub account.
3.  **Deploy New App:**
    *   Click "New app".
    *   Choose your GitHub repository.
    *   Select the correct branch.
    *   **Main file path:** Enter `extras/streamlit-twsca.py`.
    *   **App URL:** Choose a URL for your app.
4.  **Advanced Settings (Optional):**
    *   Select the Python version (e.g., 3.9, 3.10, 3.11).
    *   Add any necessary secrets (environment variables) if your app requires them (e.g., API keys for external data sources if you modify the app later).
    *   Include platform-specific configuration files if needed (e.g., `Procfile` for Heroku, `Dockerfile` if using containers). Make sure these files reference the correct paths (e.g., `extras/streamlit-twsca.py`).
    *   Address the data file requirement (see Prerequisites above).
5.  **Deploy:** Click "Deploy!". Streamlit Cloud will build the environment from your `requirements.txt` and deploy the app.

### Other Platforms (General Steps)

Deploying to platforms like Heroku, Railway, Google Cloud Run, AWS App Runner, Azure App Service, etc., generally involves these steps (consult specific platform documentation for details):

1.  **Prepare Repository:**
    *   Ensure your code is on GitHub.
    *   Make sure `requirements.txt` is up-to-date.
    *   Include platform-specific configuration files if needed (e.g., `Procfile` for Heroku, `Dockerfile` if using containers).
    *   Address the data file requirement (see Prerequisites above).

2.  **Platform Setup:**
    *   Create an account on the chosen platform.
    *   Install the platform's CLI tool (e.g., `heroku`, `railway`, `gcloud`, `aws`, `az`) if needed.

3.  **Create App on Platform:** Use the platform's web interface or CLI to create a new application.

4.  **Connect Repository:** Link your GitHub repository to the platform application.

5.  **Configure Build/Start Command:**
    *   The platform needs to know how to install dependencies and run your app.
    *   **Build:** Usually involves `pip install -r requirements.txt`.
    *   **Start Command:** Typically `streamlit run extras/streamlit-twsca.py --server.port $PORT --server.address 0.0.0.0` (The `--server.port $PORT` and `--server.address 0.0.0.0` parts are often required by hosting platforms).
    *   This might be configured via a `Procfile`, `Dockerfile`, or platform settings.
        *   *Example Procfile:* `web: streamlit run extras/streamlit-twsca.py --server.port $PORT --server.address 0.0.0.0`

6.  **Deploy:** Trigger a deployment through the platform's interface or CLI (e.g., `git push heroku main`, `railway up`).

7.  **Set Environment Variables (if needed):** Configure any required secrets or environment variables in the platform's settings.

## Troubleshooting Deployment

*   **Build Errors:** Check the build logs on the platform. Often related to missing dependencies in `requirements.txt` or incompatible Python versions.
*   **Application Errors:** Check the runtime logs. Common issues include:
    *   **Data File Not Found:** Verify the data handling strategy (Prerequisites) is correctly implemented for the platform (looking for data in `extras/data_streamlit/` if using Option A, or checking the URL if using Option B).
    *   **Incorrect Start Command:** Ensure the `streamlit run extras/streamlit-twsca.py` command is correct and includes necessary port/address bindings for the platform.
    *   **Resource Limits:** Free tiers often have memory/CPU limits. Complex analysis might exceed these.
    *   **Missing Environment Variables:** Ensure any required secrets are set.
*   **Platform Documentation:** Always refer to the specific documentation for the hosting platform you are using.

## Environment Variables
For basic functionality of the Streamlit app, no environment variables are strictly required by the current code. If you extend it (e.g., to use Alpha Vantage via the `data_tracker.py` or similar):

- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key (optional)
- Add this to a `.env` file at the project root for local development, or configure as secrets on your deployment platform.

## Custom Domain Setup
Instructions for setting up custom domains on each platform:

### Streamlit Cloud
- Go to your app settings
- Click "Custom Domain"
- Follow the DNS setup instructions

### Heroku
- Go to app settings
- Add your custom domain
- Update DNS records

### Railway
- Go to app settings
- Add custom domain
- Configure DNS settings

## Troubleshooting

### Common Issues

1. **Python Not Found (Deployment)**
   - Usually handled by the platform based on `requirements.txt` or configuration. Check platform build logs.

2. **Missing Dependencies (Deployment)**
   - Ensure `requirements.txt` is complete and committed. Check platform build logs.

3. **Data Not Loading (Deployment)**
   - See Prerequisites section regarding data handling (`.gitignore`, external hosting).
   - Check runtime logs for file path errors or URL loading errors.

4. **Visualization Issues (Deployment)**
   - Usually related to data loading or dependency issues. Check build and runtime logs.

## Environment Variables
For basic functionality, no environment variables are required. For advanced features:

- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key (optional)
- Add this to the `.env` file created during installation

## Custom Domain Setup
Instructions for setting up custom domains on each platform:

### Streamlit Cloud
- Go to your app settings
- Click "Custom Domain"
- Follow the DNS setup instructions

### Heroku
- Go to app settings
- Add your custom domain
- Update DNS records

### Railway
- Go to app settings
- Add custom domain
- Configure DNS settings

## Troubleshooting

### Common Issues

1. **Python Not Found**
   - Make sure Python is installed correctly
   - Try restarting your computer
   - Check if Python is in your PATH

2. **Missing Dependencies**
   - Run the installation script again
   - Check the error messages for specific missing packages

3. **Data Not Loading**
   - Ensure the data download completed successfully
   - Check the data directory structure

4. **Visualization Issues**
   - Ensure plotly is installed: `pip install plotly`
   - Check browser console for JavaScript errors 