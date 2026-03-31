#!/usr/bin/env python3
"""
Data Processing Skill - 核心处理脚本
负责：文件读取、SQL查询、统计摘要、数据导出
"""

import argparse
import json
import os
import sys
from pathlib import Path
import duckdb
import pandas as pd

# 缓存目录
CACHE_BASE = "/mnt/user-data/workspace/.analysis-cache"

def ensure_cache_dir(session_id):
    """确保缓存目录存在"""
    cache_dir = os.path.join(CACHE_BASE, session_id)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def inspect_files(files):
    """检查文件结构"""
    results = []
    
    for file_path in files:
        file_path = file_path.strip()
        if not os.path.exists(file_path):
            results.append({"error": f"文件不存在: {file_path}"})
            continue
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.xlsx', '.xls']:
            # Excel 文件
            try:
                xl = pd.ExcelFile(file_path)
                sheets = xl.sheet_names
                
                for sheet in sheets:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    results.append({
                        "file": file_path,
                        "sheet": sheet,
                        "columns": list(df.columns),
                        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                        "row_count": len(df),
                        "null_counts": {col: int(df[col].isna().sum()) for col in df.columns},
                        "sample": df.head(5).to_dict(orient='records')
                    })
            except Exception as e:
                results.append({"error": f"读取失败: {file_path}, {str(e)}"})
        
        elif ext == '.csv':
            # CSV 文件
            try:
                df = pd.read_csv(file_path)
                results.append({
                    "file": file_path,
                    "sheet": os.path.basename(file_path).replace('.csv', ''),
                    "columns": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "row_count": len(df),
                    "null_counts": {col: int(df[col].isna().sum()) for col in df.columns},
                    "sample": df.head(5).to_dict(orient='records')
                })
            except Exception as e:
                results.append({"error": f"读取失败: {file_path}, {str(e)}"})
        
        else:
            results.append({"error": f"不支持的文件格式: {ext}"})
    
    return results

def execute_query(files, sql, session_id, query_id):
    """执行SQL查询"""
    cache_dir = ensure_cache_dir(session_id)
    
    # 创建内存数据库
    conn = duckdb.connect()
    
    try:
        # 加载所有文件
        for file_path in files:
            file_path = file_path.strip()
            if not os.path.exists(file_path):
                continue
            
            ext = os.path.splitext(file_path)[1].lower()
            table_name = os.path.basename(file_path).replace('.', '_').replace('-', '_')
            
            if ext in ['.xlsx', '.xls']:
                xl = pd.ExcelFile(file_path)
                for sheet in xl.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    sheet_name = f"{table_name}_{sheet}".replace(' ', '_')
                    conn.register(f'"{sheet_name}"', df)
            
            elif ext == '.csv':
                df = pd.read_csv(file_path)
                conn.register(f'"{table_name}"', df)
        
        # 执行查询
        result = conn.execute(sql).fetchdf()
        
        # 转换为字典
        data = result.to_dict(orient='records')
        
        # 关键指标摘要
        summary = {}
        for col in result.columns:
            if pd.api.types.is_numeric_dtype(result[col]):
                summary[col] = {
                    "sum": float(result[col].sum()) if not result[col].isna().all() else None,
                    "mean": float(result[col].mean()) if not result[col].isna().all() else None,
                    "count": int(result[col].count()),
                    "null_count": int(result[col].isna().sum())
                }
        
        output = {
            "query_id": query_id,
            "sql": sql,
            "row_count": len(data),
            "columns": list(result.columns),
            "data": data[:100],  # 限制返回行数
            "summary": summary
        }
        
        # 写入缓存
        output_file = os.path.join(cache_dir, f"query_{query_id}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, default=str)
        
        return output
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

def generate_summary(files, table_name, session_id):
    """生成统计摘要"""
    cache_dir = ensure_cache_dir(session_id)
    
    conn = duckdb.connect()
    
    try:
        # 加载文件
        target_df = None
        
        for file_path in files:
            file_path = file_path.strip()
            if not os.path.exists(file_path):
                continue
            
            ext = os.path.splitext(file_path)[1].lower()
            table_base = os.path.basename(file_path).replace('.', '_').replace('-', '_')
            
            if ext in ['.xlsx', '.xls']:
                xl = pd.ExcelFile(file_path)
                for sheet in xl.sheet_names:
                    sheet_table = f"{table_base}_{sheet}".replace(' ', '_')
                    if sheet_table == table_name or sheet == table_name:
                        target_df = pd.read_excel(file_path, sheet_name=sheet)
                        break
            
            elif ext == '.csv:
                if table_base == table_name:
                    target_df = pd.read_csv(file_path)
        
        if target_df is None:
            return {"error": f"表 {table_name} 不存在"}
        
        # 生成统计
        metrics = {}
        
        for col in target_df.columns:
            if pd.api.types.is_numeric_dtype(target_df[col]):
                metrics[col] = {
                    "type": "numeric",
                    "count": int(target_df[col].count()),
                    "mean": float(target_df[col].mean()),
                    "std": float(target_df[col].std()),
                    "min": float(target_df[col].min()),
                    "25%": float(target_df[col].quantile(0.25)),
                    "50%": float(target_df[col].quantile(0.5)),
                    "75%": float(target_df[col].quantile(0.75)),
                    "max": float(target_df[col].max()),
                    "null_count": int(target_df[col].isna().sum())
                }
            else:
                value_counts = target_df[col].value_counts()
                metrics[col] = {
                    "type": "string",
                    "count": int(target_df[col].count()),
                    "unique": int(target_df[col].nunique()),
                    "top": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                    "top_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    "null_count": int(target_df[col].isna().sum())
                }
        
        output = {
            "table": table_name,
            "row_count": len(target_df),
            "column_count": len(target_df.columns),
            "metrics": metrics
        }
        
        # 写入缓存
        output_file = os.path.join(cache_dir, f"summary_{table_name}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, default=str)
        
        return output
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

def export_data(files, sql, output_file):
    """导出数据到文件"""
    conn = duckdb.connect()
    
    try:
        # 加载文件
        for file_path in files:
            file_path = file_path.strip()
            if not os.path.exists(file_path):
                continue
            
            ext = os.path.splitext(file_path)[1].lower()
            table_name = os.path.basename(file_path).replace('.', '_').replace('-', '_')
            
            if ext in ['.xlsx', '.xls']:
                xl = pd.ExcelFile(file_path)
                for sheet in xl.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    sheet_name = f"{table_name}_{sheet}".replace(' ', '_')
                    conn.register(f'"{sheet_name}"', df)
            
            elif ext == '.csv':
                df = pd.read_csv(file_path)
                conn.register(f'"{table_name}"', df)
        
        # 执行查询
        result = conn.execute(sql).fetchdf()
        
        # 导出
        if output_file.endswith('.csv'):
            result.to_csv(output_file, index=False)
        elif output_file.endswith('.json'):
            result.to_json(output_file, orient='records', force_ascii=False, indent=2)
        elif output_file.endswith('.xlsx'):
            result.to_excel(output_file, index=False)
        
        return {"success": True, "output_file": output_file, "row_count": len(result)}
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='Data Processing Script')
    parser.add_argument('--files', required=True, help='文件路径（空格分隔）')
    parser.add_argument('--action', required=True, choices=['inspect', 'query', 'summary', 'export'])
    parser.add_argument('--sql', help='SQL查询语句')
    parser.add_argument('--table', help='表名（用于summary）')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--session-id', default='default', help='会话ID')
    parser.add_argument('--query-id', default='01', help='查询ID')
    
    args = parser.parse_args()
    
    files = args.files.split()
    
    if args.action == 'inspect':
        result = inspect_files(files)
    
    elif args.action == 'query':
        result = execute_query(files, args.sql, args.session_id, args.query_id)
    
    elif args.action == 'summary':
        result = generate_summary(files, args.table, args.session_id)
    
    elif args.action == 'export':
        result = export_data(files, args.sql, args.output)
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, default=str))

if __name__ == '__main__':
    main()