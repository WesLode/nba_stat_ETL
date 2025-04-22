import pandas as pd
import numpy as np

def pandas_dtype_to_postgres_type(dtype):
    """Maps Pandas/NumPy dtype to a PostgreSQL SQL type string."""
    if pd.api.types.is_integer_dtype(dtype):
    # Use BIGINT for 64-bit integers (common in Pandas)
        if dtype == np.int64:
            return "INTEGER"
        else:
            return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        # Use DOUBLE PRECISION for 64-bit floats (common in Pandas)
        if dtype == np.float64:
             return "DOUBLE PRECISION"
        else:
             return "REAL" # For float32
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
    # TIMESTAMP WITHOUT TIME ZONE is common, use TIMESTAMPTZ if needed
        return "TIMESTAMP"
    elif pd.api.types.is_string_dtype(dtype):
        return "VARCHAR(30)"
    # Check if it is list or dict
    elif pd.api.types.is_object_dtype(dtype) or  isinstance(dtype, pd.CategoricalDtype):
        return "TEXT"
    elif pd.api.types.is_timedelta64_dtype(dtype):
        # Map timedelta to INTERVAL in Postgres
        return "INTERVAL"
    else:
        # Default for unknown types
        print(f"Warning: Unhandled dtype '{dtype}'. Mapping to TEXT. Manual adjustment may be needed.")
        return "TEXT"

def create_postgres_sql_from_pandas(df: pd.DataFrame, table_name: str) -> str:
    """
    Generates a PostgreSQL CREATE TABLE script from a Pandas DataFrame structure.

    Args:
        df: The Pandas DataFrame.
        table_name: The desired name for the PostgreSQL table.

    Returns:
        A string containing the PostgreSQL CREATE TABLE statement.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a Pandas DataFrame")
    if not table_name or not isinstance(table_name, str):
         raise ValueError("Table name must be a non-empty string")

    columns_sql = []
    for column_name, dtype in df.dtypes.items():
        sql_type = pandas_dtype_to_postgres_type(dtype)
        quoted_name = f'"{column_name.lower()}"'
        columns_sql.append(f"  {quoted_name} {sql_type}")

    sql_script = f"CREATE TABLE \"{table_name}\" (\n"
    sql_script += " NOT NULL,\n".join(columns_sql)
    sql_script += ',\n  "creation_timestamp" TIMESTAMPTZ DEFAULT NOW() NOT NULL'
    sql_script += "\n);"

    return sql_script