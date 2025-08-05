import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
import re

class ChartGenerator:
    """
    Generates charts and visualizations from data.
    Supports various chart types based on data characteristics and user requests.
    """
    
    def __init__(self):
        self.chart_types = {
            'bar': self._create_bar_chart,
            'line': self._create_line_chart,
            'pie': self._create_pie_chart,
            'scatter': self._create_scatter_chart,
            'histogram': self._create_histogram,
            'box': self._create_box_plot
        }
    
    def generate_chart(self, 
                      data: pd.DataFrame, 
                      chart_request: str = "",
                      auto_detect: bool = True) -> Optional[go.Figure]:
        """
        Generate a chart from data based on request or auto-detection.
        
        Args:
            data: DataFrame containing the data
            chart_request: User's chart request (e.g., "bar chart", "line graph")
            auto_detect: Whether to auto-detect best chart type
            
        Returns:
            Plotly figure or None if chart cannot be created
        """
        if data.empty:
            return None
        
        # Detect requested chart type
        requested_type = self._detect_chart_type(chart_request)
        
        # If no specific type requested or auto-detect enabled, choose best type
        if not requested_type or auto_detect:
            detected_type = self._auto_detect_chart_type(data)
            chart_type = requested_type or detected_type
        else:
            chart_type = requested_type
        
        # Generate the chart
        try:
            chart_func = self.chart_types.get(chart_type, self._create_bar_chart)
            return chart_func(data, chart_request)
        except Exception as e:
            print(f"Error generating chart: {e}")
            return None
    
    def _detect_chart_type(self, request: str) -> Optional[str]:
        """Detect chart type from user request."""
        request_lower = request.lower()
        
        chart_patterns = {
            'bar': ['bar chart', 'bar graph', 'column chart'],
            'line': ['line chart', 'line graph', 'trend', 'time series'],
            'pie': ['pie chart', 'pie graph', 'donut'],
            'scatter': ['scatter plot', 'scatter chart', 'correlation'],
            'histogram': ['histogram', 'distribution'],
            'box': ['box plot', 'box chart', 'quartile']
        }
        
        for chart_type, patterns in chart_patterns.items():
            for pattern in patterns:
                if pattern in request_lower:
                    return chart_type
        
        return None
    
    def _auto_detect_chart_type(self, data: pd.DataFrame) -> str:
        """Auto-detect the best chart type based on data characteristics."""
        
        # Get numeric and categorical columns
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # If we have time-related columns, prefer line chart
        time_cols = [col for col in data.columns if any(term in col.lower() 
                    for term in ['date', 'time', 'year', 'month', 'day'])]
        
        if time_cols and numeric_cols:
            return 'line'
        
        # If we have one categorical and one numeric, use bar chart
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            # Check if categorical column has reasonable number of categories for pie chart
            if len(categorical_cols) == 1 and len(numeric_cols) == 1:
                unique_categories = data[categorical_cols[0]].nunique()
                if unique_categories <= 8:  # Good for pie chart
                    return 'pie'
            return 'bar'
        
        # If we have two numeric columns, use scatter plot
        if len(numeric_cols) >= 2:
            return 'scatter'
        
        # If we have only one numeric column, use histogram
        if len(numeric_cols) == 1:
            return 'histogram'
        
        # Default to bar chart
        return 'bar'
    
    def _create_bar_chart(self, data: pd.DataFrame, request: str = "") -> go.Figure:
        """Create a bar chart."""
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if not numeric_cols:
            # If no numeric columns, create a count chart
            if categorical_cols:
                col = categorical_cols[0]
                count_data = data[col].value_counts().reset_index()
                count_data.columns = [col, 'count']
                fig = px.bar(count_data, x=col, y='count', 
                           title=f'Count by {col}')
            else:
                # Create a simple count of rows
                fig = go.Figure()
                fig.add_trace(go.Bar(x=['Total'], y=[len(data)]))
                fig.update_layout(title='Total Count')
        else:
            # Use first categorical and first numeric column
            x_col = categorical_cols[0] if categorical_cols else data.index
            y_col = numeric_cols[0]
            
            if categorical_cols:
                # Group by categorical column and sum numeric
                grouped = data.groupby(x_col)[y_col].sum().reset_index()
                fig = px.bar(grouped, x=x_col, y=y_col,
                           title=f'{y_col} by {x_col}')
            else:
                # Just plot the numeric values
                fig = px.bar(data, y=y_col, title=f'{y_col} Values')
        
        fig.update_layout(showlegend=False)
        return fig
    
    def _create_line_chart(self, data: pd.DataFrame, request: str = "") -> go.Figure:
        """Create a line chart."""
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        
        # Look for time-related columns
        time_cols = [col for col in data.columns if any(term in col.lower() 
                    for term in ['date', 'time', 'year', 'month', 'day'])]
        
        if time_cols and numeric_cols:
            x_col = time_cols[0]
            y_col = numeric_cols[0]
            fig = px.line(data, x=x_col, y=y_col,
                         title=f'{y_col} over {x_col}')
        elif len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            fig = px.line(data, x=x_col, y=y_col,
                         title=f'{y_col} vs {x_col}')
        elif numeric_cols:
            y_col = numeric_cols[0]
            fig = px.line(data, y=y_col, title=f'{y_col} Trend')
        else:
            # Fallback to simple line
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=list(range(len(data))), mode='lines'))
            fig.update_layout(title='Data Trend')
        
        return fig
    
    def _create_pie_chart(self, data: pd.DataFrame, request: str = "") -> go.Figure:
        """Create a pie chart."""
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if categorical_cols and numeric_cols:
            # Group by categorical and sum numeric
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            grouped = data.groupby(cat_col)[num_col].sum().reset_index()
            fig = px.pie(grouped, values=num_col, names=cat_col,
                        title=f'{num_col} by {cat_col}')
        elif categorical_cols:
            # Count by categorical
            cat_col = categorical_cols[0]
            count_data = data[cat_col].value_counts().reset_index()
            count_data.columns = [cat_col, 'count']
            fig = px.pie(count_data, values='count', names=cat_col,
                        title=f'Distribution of {cat_col}')
        else:
            # Fallback - not ideal for pie chart
            fig = go.Figure()
            fig.add_trace(go.Pie(values=[len(data)], labels=['Total']))
            fig.update_layout(title='Data Distribution')
        
        return fig
    
    def _create_scatter_chart(self, data: pd.DataFrame, request: str = "") -> go.Figure:
        """Create a scatter plot."""
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            
            # Check if there's a categorical column for color
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
            color_col = categorical_cols[0] if categorical_cols else None
            
            fig = px.scatter(data, x=x_col, y=y_col, color=color_col,
                           title=f'{y_col} vs {x_col}')
        else:
            # Fallback to index vs single numeric column
            y_col = numeric_cols[0] if numeric_cols else data.columns[0]
            fig = px.scatter(data, y=y_col, title=f'{y_col} Distribution')
        
        return fig
    
    def _create_histogram(self, data: pd.DataFrame, request: str = "") -> go.Figure:
        """Create a histogram."""
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            col = numeric_cols[0]
            fig = px.histogram(data, x=col, title=f'Distribution of {col}')
        else:
            # Fallback for non-numeric data
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
            if categorical_cols:
                col = categorical_cols[0]
                fig = px.histogram(data, x=col, title=f'Distribution of {col}')
            else:
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=list(range(len(data)))))
                fig.update_layout(title='Data Distribution')
        
        return fig
    
    def _create_box_plot(self, data: pd.DataFrame, request: str = "") -> go.Figure:
        """Create a box plot."""
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if numeric_cols and categorical_cols:
            # Box plot by category
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
            fig = px.box(data, x=x_col, y=y_col,
                        title=f'{y_col} Distribution by {x_col}')
        elif numeric_cols:
            # Simple box plot
            y_col = numeric_cols[0]
            fig = px.box(data, y=y_col, title=f'{y_col} Distribution')
        else:
            # Fallback
            fig = go.Figure()
            fig.add_trace(go.Box(y=list(range(len(data)))))
            fig.update_layout(title='Data Distribution')
        
        return fig
    
    def suggest_chart_types(self, data: pd.DataFrame) -> List[str]:
        """Suggest appropriate chart types for the given data."""
        if data.empty:
            return []
        
        suggestions = []
        
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        time_cols = [col for col in data.columns if any(term in col.lower() 
                    for term in ['date', 'time', 'year', 'month', 'day'])]
        
        if time_cols and numeric_cols:
            suggestions.append('line')
        
        if categorical_cols and numeric_cols:
            suggestions.extend(['bar', 'pie'])
        
        if len(numeric_cols) >= 2:
            suggestions.append('scatter')
        
        if numeric_cols:
            suggestions.extend(['histogram', 'box'])
        
        return suggestions 