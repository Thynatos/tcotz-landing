"""
Input validation for production planning data.
"""
from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    
    def __bool__(self):
        return self.is_valid


class DataValidator:
    """Validates input data for the production planner."""
    
    # Parameter ranges
    PARAM_RANGES = {
        'line1_capacity': (100, 10000),
        'line2_capacity': (100, 5000),
        'holding_cost': (0.01, 1000),
        'backlog_cost': (1, 100000),
        'b12_penalty': (100, 100000),
        'horizon_days': (40, 365),
    }
    
    # Required columns in demand data
    REQUIRED_COLUMNS = {'product', 'demand'}
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_demand_file(self, df: pd.DataFrame) -> ValidationResult:
        """
        Validate uploaded demand DataFrame.
        
        Args:
            df: DataFrame with demand data
            
        Returns:
            ValidationResult with errors and warnings
        """
        self.errors = []
        self.warnings = []
        
        # Check required columns
        lower_cols = set(df.columns.str.lower())
        missing_cols = self.REQUIRED_COLUMNS - lower_cols
        if missing_cols or ('day' not in lower_cols and 'date' not in lower_cols):
            self.errors.append(
                f"Missing required columns: {', '.join(missing_cols) if missing_cols else ''}. "
                f"Required: product, demand, AND either 'day' or 'date'"
            )
            return ValidationResult(False, self.errors, self.warnings)
        
        # Normalize column names
        df.columns = df.columns.str.lower()
        
        # Check for empty data
        if df.empty:
            self.errors.append("Uploaded file contains no data rows.")
            return ValidationResult(False, self.errors, self.warnings)
        
        has_day = 'day' in df.columns
        has_date = 'date' in df.columns

        # Check time column type rules
        if has_day and not pd.api.types.is_numeric_dtype(df['day']):
            self.errors.append("Column 'day' must contain numeric values when provided.")

        if has_date:
            parsed_dates = pd.to_datetime(df['date'], errors='coerce')
            if parsed_dates.isna().all():
                self.errors.append("Column 'date' does not contain any parseable dates.")
        
        if not pd.api.types.is_numeric_dtype(df['demand']):
            non_numeric = df[~df['demand'].apply(
                lambda x: isinstance(x, (int, float))
            )].index.tolist()
            self.errors.append(
                f"Column 'demand' has non-numeric values at rows: {non_numeric[:5]}"
            )
        
        # Check for negative demand
        if 'demand' in df.columns and pd.api.types.is_numeric_dtype(df['demand']):
            negative_rows = df[df['demand'] < 0]
            if not negative_rows.empty:
                ref_col = 'day' if 'day' in negative_rows.columns else ('date' if 'date' in negative_rows.columns else None)
                refs = negative_rows[ref_col].tolist()[:5] if ref_col else negative_rows.index.tolist()[:5]
                self.errors.append(
                    f"Negative demand values found at rows/time refs: {refs}"
                )
        
        # Check product IDs
        if 'product' in df.columns:
            valid_products = {1, 2, 3, 4}
            invalid_products = set(df['product'].unique()) - valid_products
            if invalid_products:
                self.errors.append(
                    f"Invalid product IDs: {invalid_products}. Valid: 1, 2, 3, 4"
                )
        
        # Warnings for unusual values
        if 'demand' in df.columns and pd.api.types.is_numeric_dtype(df['demand']):
            mean_demand = df['demand'].mean()
            extreme = df[df['demand'] > mean_demand * 10]
            if not extreme.empty and mean_demand > 0:
                ref_col = 'day' if 'day' in extreme.columns else ('date' if 'date' in extreme.columns else None)
                refs = extreme[ref_col].tolist()[:3] if ref_col else extreme.index.tolist()[:3]
                self.warnings.append(
                    f"Unusually high demand values at rows/time refs: {refs}. Please verify."
                )
        
        # Check day range
        if 'day' in df.columns and pd.api.types.is_numeric_dtype(df['day']):
            min_day = df['day'].min()
            max_day = df['day'].max()
            if min_day < 1:
                self.errors.append(f"Day values must start from 1, found: {min_day}")
            if max_day > 365:
                self.warnings.append(
                    f"Day values exceed 365 (max: {max_day}). "
                    "Ensure this matches your planning horizon."
                )
        
        is_valid = len(self.errors) == 0
        return ValidationResult(is_valid, self.errors, self.warnings)
    
    def validate_parameters(self, params: dict) -> ValidationResult:
        """
        Validate model parameters.
        
        Args:
            params: Dictionary of parameter name -> value
            
        Returns:
            ValidationResult with errors and warnings
        """
        self.errors = []
        self.warnings = []
        
        for param_name, value in params.items():
            if param_name in self.PARAM_RANGES:
                min_val, max_val = self.PARAM_RANGES[param_name]
                if value < min_val or value > max_val:
                    self.errors.append(
                        f"Parameter '{param_name}' value {value} "
                        f"is outside valid range [{min_val}, {max_val}]"
                    )
        
        # Cross-parameter validation
        if 'off_season_end' in params and 'horizon_days' in params:
            if params['off_season_end'] >= params['horizon_days']:
                self.errors.append(
                    f"Off-season end day ({params['off_season_end']}) "
                    f"must be less than horizon ({params['horizon_days']})"
                )
        
        is_valid = len(self.errors) == 0
        return ValidationResult(is_valid, self.errors, self.warnings)
