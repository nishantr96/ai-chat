# Data Chat Interface

A Streamlit-based chat interface for interacting with your data catalog using Atlan and LLM-powered reasoning.

## Features

- 🤖 **LLM-Powered Intent Understanding**: Uses LiteLLM Proxy for enhanced query analysis
- 📚 **Glossary Term Search**: Find and define business terms from your data catalog
- 🔍 **Asset Discovery**: Find which assets use specific glossary terms
- 📊 **Analytical Charts**: Generate visualizations based on asset metadata
- 💬 **Natural Language Interface**: Ask questions in plain English
- 🔄 **Context-Aware Conversations**: Maintains conversation context for better follow-ups
- ⚡ **Real-time Atlan Integration**: Direct connection to your Atlan data catalog

## Prerequisites

- Python 3.8+
- Atlan account with API access
- LiteLLM Proxy server (for LLM features)
- Snowflake account (for data querying - coming soon)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-chat
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env_template.txt .env
   # Edit .env with your credentials
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Atlan API Configuration
ATLAN_API_TOKEN=your_atlan_api_token_here
ATLAN_BASE_URL=https://home.atlan.com

# Snowflake Configuration (for future data querying)
SNOWFLAKE_ACCOUNT=your_snowflake_account_here
SNOWFLAKE_USER=your_snowflake_user_here
SNOWFLAKE_PASSWORD=your_snowflake_password_here
SNOWFLAKE_WAREHOUSE=your_snowflake_warehouse_here
SNOWFLAKE_DATABASE=your_snowflake_database_here
SNOWFLAKE_SCHEMA=your_snowflake_schema_here
SNOWFLAKE_ROLE=your_snowflake_role_here

# LiteLLM Proxy Configuration
OPENAI_API_KEY=your_litellm_proxy_api_key_here
LITELLM_PROXY_URL=http://localhost:4000
```

### Setting up LiteLLM Proxy

The application uses LiteLLM Proxy for LLM features. You have several options:

#### Option 1: Use a hosted LiteLLM Proxy service
If you have access to a hosted LiteLLM Proxy service, update the `LITELLM_PROXY_URL` in your `.env` file.

#### Option 2: Run LiteLLM Proxy locally
1. **Install LiteLLM:**
   ```bash
   pip install litellm
   ```

2. **Start the proxy server:**
   ```bash
   litellm --model gpt-4 --api-key your_openai_api_key
   ```

3. **Or use a config file:**
   Create a `config.yaml` file:
   ```yaml
   model_list:
   - model_name: gpt-4
     litellm_params:
       model: gpt-4
       api_key: your_openai_api_key
   ```

   Then start with:
   ```bash
   litellm --config config.yaml
   ```

#### Option 3: Run without LLM features
The application works perfectly without LLM features using pattern-based intent detection. Simply leave the LLM configuration empty or set `LITELLM_PROXY_URL` to an invalid URL.

## Usage

### Starting the Application

1. **Activate your virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run the application:**
   ```bash
   streamlit run app.py
   ```

3. **Or use the convenience script:**
   ```bash
   python run.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:8501`

### Example Queries

- **Glossary Terms:**
  - "Define Customer Acquisition Cost"
  - "What is Annual Revenue?"
  - "What glossary terms do you have?"

- **Asset Discovery:**
  - "Which assets use Customer Acquisition Cost?"
  - "What uses Annual Revenue?"
  - "Find assets with Net Collection Rate"

- **Analytical Charts:**
  - "Give me a bar chart by connector type of assets that use Customer Acquisition Cost"
  - "Show me a pie chart by asset type of assets that use Annual Revenue"

- **Data Queries (Coming Soon):**
  - "Tell me the annual revenue from last year"
  - "What's our customer acquisition cost trend?"

## Workflow

1. **Ask a Question**: Type your question in natural language
2. **Intent Clarification**: The system may ask for clarification if needed
3. **Get Results**: Receive definitions, asset lists, or charts
4. **Follow-up**: Ask related questions for deeper insights

## Architecture

### Components

- **`app.py`**: Main Streamlit application with chat interface
- **`atlan_client.py`**: Atlan API integration for data catalog access
- **`query_processor.py`**: Intent detection and query routing with optional LLM enhancement
- **`llm_service.py`**: LiteLLM Proxy integration for advanced reasoning
- **`chart_generator.py`**: Interactive chart generation using Plotly
- **`snowflake_client.py`**: Snowflake integration for data querying (coming soon)

### LLM Integration

The application uses LiteLLM Proxy for:
- **Intent Analysis**: Understanding user queries and extracting terms
- **Response Enhancement**: Making responses more helpful and clear
- **Clarification Questions**: Generating specific questions when intent is unclear
- **Follow-up Suggestions**: Suggesting relevant next questions

### Fallback Mechanism

If LLM services are unavailable, the application gracefully falls back to:
- Pattern-based intent detection
- Basic response formatting
- Standard clarification prompts

## Supported Chart Types

- **Bar Charts**: For comparing categories
- **Line Charts**: For trends over time
- **Pie Charts**: For proportions
- **Scatter Plots**: For correlations
- **Histograms**: For distributions
- **Box Plots**: For statistical summaries

## Query Types

### Currently Supported
- ✅ Glossary term definitions
- ✅ Asset discovery by term
- ✅ Analytical charts by metadata
- ✅ List all glossary terms
- ✅ Intent clarification

### Coming Soon
- 🔄 Data querying from Snowflake
- 🔄 Semantic model creation
- 🔄 Advanced visualizations
- 🔄 Multi-step workflows

## Development

### Project Structure
```
ai-chat/
├── app.py                 # Main Streamlit application
├── atlan_client.py        # Atlan API client
├── query_processor.py     # Query processing and routing
├── llm_service.py         # LLM integration
├── chart_generator.py     # Chart generation
├── snowflake_client.py    # Snowflake integration
├── requirements.txt       # Python dependencies
├── env_template.txt       # Environment variables template
├── README.md             # This file
└── test_llm.py           # LLM testing script
```

### Testing

Test the LLM integration:
```bash
python test_llm.py
```

### Adding New Features

1. **New Query Types**: Add patterns to `query_processor.py`
2. **New Chart Types**: Extend `chart_generator.py`
3. **New Data Sources**: Create new client modules
4. **UI Enhancements**: Modify `app.py`

## Troubleshooting

### Common Issues

1. **"LLM Service Unavailable"**
   - Check your LiteLLM Proxy configuration
   - Verify the proxy server is running
   - The app works without LLM features

2. **"Connection to Atlan Failed"**
   - Verify your Atlan API token
   - Check network connectivity
   - Ensure the Atlan URL is correct

3. **"No glossary terms found"**
   - Check your Atlan permissions
   - Verify the glossary exists
   - Try different search terms

4. **Port already in use**
   - Use a different port: `streamlit run app.py --server.port 8502`
   - Kill existing processes: `pkill -f streamlit`

### Debug Mode

Enable debug logging by setting environment variables:
```bash
export STREAMLIT_LOG_LEVEL=debug
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the Atlan and LiteLLM documentation
3. Open an issue on GitHub

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Atlan](https://atlan.com/) data catalog
- Enhanced with [LiteLLM](https://github.com/BerriAI/litellm) Proxy
- Charts generated with [Plotly](https://plotly.com/) 