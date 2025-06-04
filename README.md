# HackAttack Preliminary Round Prototype

## Overview

This project is a prototype for the HackAttack Preliminary Round. It features a multi-company job board and applicant dashboard built with Python and Streamlit.

### Prerequisites

* Python 3.7 or higher
* Virtual environment tool (`venv` recommended)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/Tan051107/HackAttack-Preliminary-Round-Prototype.git](https://github.com/Tan051107/HackAttack-Preliminary-Round-Prototype.git)
    cd HackAttack-Preliminary-Round-Prototype
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv .venv
    ```

    * **On Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

3.  **Install dependencies:**

    Ensure you are in the project's root directory where `requirements.txt` is located, then run:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### To run the Recruiter Interface:
```bash
streamlit run recruiter_interface.py
```
### To run the Applicant Interface:
```bash
streamlit run applicant_interface.py
```

## Managing Secrets

This project uses Streamlit’s `secrets.toml` file to store sender's email address and app password

Add your secret keys in this format:

   ```toml
   
   SENDER_EMAIL_ADDRESS = "your email address"
   SENDER_EMAIL_PASSWORD = "your app password"
  ```





