# 🔍 Atlan Data Chat Interface

A minimal, clean Streamlit application that integrates with Atlan API and OpenAI to provide intelligent data asset analysis.

## 🚀 Features

- **Atlan Integration**: Search for assets linked to glossary terms
- **OpenAI LLM Analysis**: Get intelligent insights about your data assets
- **Fallback Support**: Uses mock data when APIs are unavailable
- **Clean UI**: Simple, intuitive interface for data exploration

## 📋 Requirements

- Python 3.8+
- Atlan API Token
- OpenAI API Key

## 🛠️ Installation

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd ai-chat
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   Create a `.env` file with:
   ```env
   ATLAN_API_TOKEN=your_atlan_token_here
   OPENAI_API_KEY=your_openai_key_here
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 🎯 Usage

1. **Open the app** at `http://localhost:8501`
2. **Check connection status** - both Atlan and OpenAI APIs should show as connected
3. **Ask questions** about Customer Acquisition Cost (CAC) assets
4. **View results** - see assets found and AI analysis

## 📊 Current Functionality

### Customer Acquisition Cost (CAC) Analysis
The app is currently configured to search for assets related to "Customer Acquisition Cost (CAC)" using:
- **Term GUID**: `af6a32d4-936b-4a59-9917-7082c56ba443`
- **Term Name**: "Customer Acquisition Cost (CAC)"

### Asset Types Supported
- Tables
- Dashboards (Tableau, PowerBI)
- Processes
- Queries
- Collections

### AI Analysis Features
- Asset relationship analysis
- Business context insights
- Usage recommendations
- Data quality assessment

## 🔧 Architecture

```
app.py              # Main Streamlit application
├── atlan_client.py # Atlan API integration
├── llm_service.py  # OpenAI LLM integration
└── requirements.txt # Dependencies
```

### Key Components

1. **AtlanClient**: Handles Atlan API communication
   - Asset search by term GUID
   - Asset search by term name
   - Connection testing

2. **LLMService**: Manages OpenAI integration
   - Asset analysis
   - Query processing
   - Response generation

3. **Mock Data**: Fallback assets for demonstration
   - CAC Dashboard
   - Marketing Spend Table
   - Customer Onboarding Process

## 🚨 Troubleshooting

### Atlan API Issues
- **401 Unauthorized**: Check your `ATLAN_API_TOKEN`
- **500 Server Error**: Atlan service may be down
- **No assets found**: Term may not exist or have no linked assets

### OpenAI API Issues
- **401 Invalid API Key**: Check your `OPENAI_API_KEY`
- **Rate limiting**: Wait and retry
- **Service unavailable**: Check OpenAI status

### App Issues
- **Port conflicts**: Change port in streamlit command
- **Import errors**: Ensure all dependencies are installed
- **Environment variables**: Verify `.env` file exists and is readable

## 🔄 Development

### Adding New Terms
1. Update the term GUID and name in `app.py`
2. Modify search logic in `atlan_client.py` if needed
3. Test with the Atlan API

### Extending Functionality
1. Add new asset types to `atlan_client.py`
2. Enhance LLM prompts in `llm_service.py`
3. Update UI components in `app.py`

## 📁 File Structure

```
ai-chat/
├── app.py                 # Main application
├── atlan_client.py        # Atlan API client
├── llm_service.py         # OpenAI LLM service
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── v1_backup/            # Backup of previous version
└── README.md             # This file
```

## 🎉 Success!

The app is now running with:
- ✅ Clean, minimal codebase
- ✅ Atlan API integration (with fallback)
- ✅ OpenAI LLM analysis
- ✅ Mock data for demonstration
- ✅ Error handling and user feedback

## 🔗 Next Steps

1. **Fix API Keys**: Update `.env` with valid credentials
2. **Test Live Data**: Verify Atlan API connectivity
3. **Extend Functionality**: Add more terms and features
4. **Deploy**: Consider cloud deployment options

---

**Status**: ✅ **WORKING** - Minimal functional app with fallback support 