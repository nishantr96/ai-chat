# Atlan Data Chat Interface

A conversational Streamlit application that integrates with Atlan's data catalog to provide intelligent search and exploration of glossary terms, assets, and metadata.

## 🚀 Features

### Core Functionality
- **Intelligent Term Search**: Find and explore glossary terms with natural language queries
- **Rich Metadata Display**: View comprehensive term information including descriptions, categories, owners, and custom metadata
- **Linked Assets Discovery**: Automatically find and display assets related to glossary terms
- **Custom Score Metadata**: Display custom metadata badges (e.g., viewScore) with priority over standard popularity scores
- **Source Information**: Show connection and connector details for linked assets
- **Asset Count Tracking**: Display total count of linked assets for better context

### UI Features
- **Modern Streamlit Interface**: Clean, responsive web interface
- **Rich Markdown Formatting**: Beautifully formatted term and asset information
- **Interactive Tables**: Sortable linked assets table with source information
- **Direct Atlan Links**: Clickable links to view terms directly in Atlan
- **Real-time Search**: Instant search results with comprehensive metadata

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.13+
- **Data Catalog**: Atlan API integration
- **Search**: Atlan DSL (Domain Specific Language) queries
- **Authentication**: Atlan API token-based authentication

## 📋 Prerequisites

- Python 3.13 or higher
- Atlan account with API access
- Valid Atlan API token
- Required Python packages (see requirements.txt)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-chat
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Atlan credentials
   ```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
ATLAN_BASE_URL=https://your-instance.atlan.com
ATLAN_API_TOKEN=your_atlan_api_token
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://your_openai_endpoint
```

### Required Environment Variables:
- `ATLAN_BASE_URL`: Your Atlan instance URL
- `ATLAN_API_TOKEN`: Your Atlan API token for authentication
- `OPENAI_API_KEY`: OpenAI API key for LLM features (optional)
- `OPENAI_BASE_URL`: OpenAI API endpoint (optional)

## 🚀 Usage

### Starting the Application

1. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

2. **Run the Streamlit app**
   ```bash
   streamlit run conversational_atlan_app.py
   ```

3. **Access the application**
   - Open your browser to `http://localhost:8501`
   - The application will be available on your local network

### Using the Application

1. **Search for Terms**: Type queries like:
   - "Define Customer Acquisition Cost"
   - "What is CAC?"
   - "Find assets related to customer data"

2. **Explore Results**: View comprehensive term information including:
   - Term name and description
   - Custom metadata badges (Score, etc.)
   - Categories and tags
   - Owners and certificate status
   - Linked assets with source information

3. **Navigate to Atlan**: Click on term links to view them directly in Atlan

## 📁 Project Structure

```
ai-chat/
├── conversational_atlan_app.py    # Main Streamlit application
├── atlan_client.py                # Atlan API client and search logic
├── llm_service.py                 # LLM integration service
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (not in git)
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
└── v1_backup/                    # Backup files from development
```

## 🔍 Key Components

### `conversational_atlan_app.py`
- Main Streamlit application interface
- Handles user input and intent analysis
- Formats and displays search results
- Manages application state and UI

### `atlan_client.py`
- AtlanSDKClient class for API interactions
- Search functionality for terms and assets
- Data extraction and processing
- Error handling and fallback mechanisms

### `llm_service.py`
- LLM integration for enhanced responses
- Intent analysis and query processing
- Response enhancement capabilities

## 🎯 Features in Detail

### Custom Score Metadata
- Displays custom metadata badges (e.g., `viewScore`) with priority over standard popularity scores
- Shows as "### 📊 Score\n**{value}**" in the UI

### Linked Assets with Count
- Automatically discovers assets related to glossary terms
- Shows total count: "### 📊 Linked Assets ({count} total)"
- Displays source information using connection names

### Enhanced Source Information
- Prioritizes `connectionName` over `connectorName` for better source identification
- Shows source details in linked assets table
- Handles cases where source information might be missing

### Intelligent Search
- Multiple search strategies for comprehensive results
- Fallback mechanisms for different search scenarios
- Optimized queries to avoid API limits and errors

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your Atlan API token is correct
   - Check that your token has the necessary permissions
   - Ensure the Atlan base URL is correct

2. **No Results Found**
   - Check if the term exists in your Atlan instance
   - Verify search permissions for the term
   - Try different search terms or variations

3. **API Rate Limits**
   - The application includes built-in rate limiting
   - Search results are limited to prevent overwhelming the API
   - Consider adjusting search parameters if needed

4. **Missing Environment Variables**
   - Ensure all required environment variables are set in `.env`
   - Check that the `.env` file is in the project root directory

### Debug Mode
Enable debug logging by setting environment variables or modifying the code to include additional print statements for troubleshooting.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the Atlan API documentation
3. Create an issue in the repository

## 🔄 Version History

- **v1**: Initial release with core functionality
  - Custom Score metadata badge support
  - Linked assets with total count
  - Enhanced source information display
  - Comprehensive search capabilities
  - Modern Streamlit UI 