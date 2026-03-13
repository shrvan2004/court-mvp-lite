# Bengaluru Court Cause List Dashboard

This is a Streamlit-based web application that provides an interactive dashboard for browsing and searching Bengaluru Court cause lists. The application allows users to filter cases by date, court, and perform text-based searches on case numbers, parties, advocates, or stages.

## Features

- **Database Summary**: Displays total cases, complexes, and courts in the dataset.
- **Filtering Options**:
  - Date selection
  - Court selection
  - Text search across case details
- **Results Table**: Interactive table showing filtered cases.
- **Download Options**: Export filtered results to CSV or Excel.
- **AI Legal Assistant**: Ask natural language questions about the database using Google's Gemini AI.
- **AI Case Explanation**: Get simplified explanations of individual cases using AI.

## Data

The application uses JSON data files containing court case information including:
- Case numbers
- Parties involved
- Advocates or stages
- Court details
- Scrape dates

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/court-mvp-lite.git
   cd court-mvp-lite
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your Google Gemini API key: `GEMINI_API_KEY=your_api_key_here`

4. Run the application:
   ```bash
   streamlit run app1.py
   ```

## Usage

- Open the Streamlit app in your browser.
- Use the filters to narrow down cases.
- Enter search terms to find specific cases.
- Ask questions in the AI Legal Assistant chat.
- Select a row number to get an AI-generated explanation of a case.

## Technologies Used

- **Streamlit**: For the web interface
- **Pandas**: For data manipulation
- **Google Generative AI (Gemini)**: For AI-powered features
- **Python**: Core programming language

## Contributing

Feel free to submit issues and enhancement requests.

## License

This project is open source and available under the [MIT License](LICENSE).