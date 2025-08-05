import os
import snowflake.connector
import pandas as pd
from typing import Dict, Any, List, Optional
import yaml
import json
from dotenv import load_dotenv

load_dotenv()

class SnowflakeClient:
    """
    Client for connecting to Snowflake and executing queries.
    Handles both direct queries and semantic model creation.
    """
    
    def __init__(self):
        self.account = os.getenv('SNOWFLAKE_ACCOUNT')
        self.user = os.getenv('SNOWFLAKE_USER')
        self.password = os.getenv('SNOWFLAKE_PASSWORD')
        self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
        self.role = os.getenv('SNOWFLAKE_ROLE')
        self.database = os.getenv('SNOWFLAKE_DATABASE')
        
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Snowflake."""
        try:
            self.connection = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                warehouse=self.warehouse,
                role=self.role,
                database=self.database
            )
        except Exception as e:
            print(f"Failed to connect to Snowflake: {e}")
            self.connection = None
    
    def is_connected(self) -> bool:
        """Check if connected to Snowflake."""
        return self.connection is not None
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.
        
        Args:
            query: SQL query to execute
            
        Returns:
            DataFrame with query results
        """
        if not self.connection:
            raise Exception("Not connected to Snowflake")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch results
            results = cursor.fetchall()
            
            # Create DataFrame
            df = pd.DataFrame(results, columns=columns)
            
            cursor.close()
            return df
            
        except Exception as e:
            raise Exception(f"Error executing query: {e}")
    
    def get_table_schema(self, table_qualified_name: str) -> List[Dict[str, Any]]:
        """
        Get schema information for a table.
        
        Args:
            table_qualified_name: Fully qualified table name
            
        Returns:
            List of column information
        """
        try:
            # Parse qualified name to extract database, schema, table
            parts = table_qualified_name.split('.')
            if len(parts) >= 3:
                database, schema, table = parts[-3], parts[-2], parts[-1]
            else:
                raise Exception("Invalid table qualified name format")
            
            query = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COMMENT
            FROM {database}.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' 
            AND TABLE_NAME = '{table}'
            ORDER BY ORDINAL_POSITION
            """
            
            df = self.execute_query(query)
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Error getting table schema: {e}")
            return []
    
    def create_semantic_model(self, 
                            table_info: Dict[str, Any], 
                            model_name: str,
                            columns: List[Dict[str, Any]]) -> bool:
        """
        Create a semantic model in Cortex Analyst.
        
        Args:
            table_info: Information about the table
            model_name: Name for the semantic model
            columns: Column information from Atlan
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create semantic model YAML
            semantic_model = self._build_semantic_model_yaml(table_info, model_name, columns)
            
            # Save to stage in Snowflake
            stage_name = f"SEMANTIC_MODELS"
            file_name = f"{model_name.lower()}_semantic_model.yaml"
            
            # Create stage if it doesn't exist
            self._create_stage_if_not_exists(stage_name)
            
            # Upload semantic model
            return self._upload_semantic_model(stage_name, file_name, semantic_model)
            
        except Exception as e:
            print(f"Error creating semantic model: {e}")
            return False
    
    def _build_semantic_model_yaml(self, 
                                 table_info: Dict[str, Any], 
                                 model_name: str,
                                 columns: List[Dict[str, Any]]) -> str:
        """Build semantic model YAML content."""
        
        qualified_name = table_info.get('qualified_name', '')
        description = table_info.get('description', table_info.get('user_description', ''))
        
        # Build dimensions and measures from columns
        dimensions = []
        measures = []
        
        for col in columns:
            col_name = col.get('name', '')
            col_type = col.get('data_type', '').upper()
            col_desc = col.get('description', col.get('user_description', ''))
            
            if col_type in ['NUMBER', 'INTEGER', 'FLOAT', 'DECIMAL', 'NUMERIC']:
                # Numeric columns can be measures
                measures.append({
                    'name': col_name.lower(),
                    'expr': col_name,
                    'description': col_desc,
                    'data_type': 'NUMBER'
                })
            else:
                # Non-numeric columns are dimensions
                dimensions.append({
                    'name': col_name.lower(),
                    'expr': col_name,
                    'description': col_desc,
                    'data_type': 'TEXT'
                })
        
        # Build semantic model structure
        semantic_model = {
            'name': model_name,
            'description': f"Semantic model for {table_info.get('name', 'table')}",
            'tables': [{
                'name': table_info.get('name', 'main_table'),
                'description': description,
                'base_table': {
                    'database': qualified_name.split('.')[0] if '.' in qualified_name else self.database,
                    'schema': qualified_name.split('.')[1] if qualified_name.count('.') >= 1 else 'PUBLIC',
                    'table': qualified_name.split('.')[-1] if '.' in qualified_name else qualified_name
                },
                'dimensions': dimensions[:20],  # Limit to avoid too large models
                'measures': measures[:20]
            }],
            'verified_queries': [
                {
                    'name': 'sample_query',
                    'question': f"What is the total for {table_info.get('name', 'this table')}?",
                    'sql': f"SELECT COUNT(*) as total_rows FROM {qualified_name}",
                    'verified_at': '2024-01-01T00:00:00Z',
                    'verified_by': 'system'
                }
            ]
        }
        
        return yaml.dump(semantic_model, default_flow_style=False)
    
    def _create_stage_if_not_exists(self, stage_name: str):
        """Create stage if it doesn't exist."""
        try:
            query = f"CREATE STAGE IF NOT EXISTS {stage_name}"
            cursor = self.connection.cursor()
            cursor.execute(query)
            cursor.close()
        except Exception as e:
            print(f"Error creating stage: {e}")
    
    def _upload_semantic_model(self, stage_name: str, file_name: str, content: str) -> bool:
        """Upload semantic model to Snowflake stage."""
        try:
            # For this demo, we'll just print the semantic model
            # In a real implementation, you'd upload to the stage
            print(f"Semantic model content for {file_name}:")
            print(content)
            print(f"Would upload to stage: {stage_name}")
            return True
        except Exception as e:
            print(f"Error uploading semantic model: {e}")
            return False
    
    def generate_query_for_request(self, 
                                 request: str, 
                                 table_info: Dict[str, Any], 
                                 columns: List[Dict[str, Any]]) -> str:
        """
        Generate a SQL query based on natural language request.
        
        Args:
            request: Natural language request
            table_info: Table information
            columns: Column information
            
        Returns:
            Generated SQL query
        """
        qualified_name = table_info.get('qualified_name', '')
        
        # Simple query generation logic
        # In a real implementation, you'd use more sophisticated NLP
        
        request_lower = request.lower()
        
        if 'count' in request_lower or 'total' in request_lower:
            return f"SELECT COUNT(*) as total_count FROM {qualified_name}"
        
        elif 'revenue' in request_lower:
            # Look for revenue-like columns
            revenue_cols = [col['name'] for col in columns 
                          if 'revenue' in col.get('name', '').lower() 
                          or 'sales' in col.get('name', '').lower()
                          or 'amount' in col.get('name', '').lower()]
            
            if revenue_cols:
                return f"SELECT SUM({revenue_cols[0]}) as total_revenue FROM {qualified_name}"
        
        elif 'average' in request_lower or 'avg' in request_lower:
            numeric_cols = [col['name'] for col in columns 
                          if col.get('data_type', '').upper() in ['NUMBER', 'INTEGER', 'FLOAT', 'DECIMAL']]
            
            if numeric_cols:
                return f"SELECT AVG({numeric_cols[0]}) as average_value FROM {qualified_name}"
        
        # Default query
        return f"SELECT * FROM {qualified_name} LIMIT 10"
    
    def close(self):
        """Close Snowflake connection."""
        if self.connection:
            self.connection.close()
            self.connection = None 