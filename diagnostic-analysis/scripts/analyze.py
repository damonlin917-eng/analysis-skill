#!/usr/bin/env python3
"""
Diagnostic Analysis Skill - 核心分析脚本
负责：业务理解、归因分析、异常检测、对比分析、行动建议
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# 缓存目录
CACHE_BASE = "/mnt/user-data/workspace/.analysis-cache"

def load_cache(cache_dir):
    """加载缓存数据"""
    if not os.path.exists(cache_dir):
        return {}
    
    data = {}
    for file in os.listdir(cache_dir):
        if file.endswith('.json'):
            with open(os.path.join(cache_dir, file), 'r', encoding='utf-8') as f:
                data[file] = json.load(f)
    return data

def semantic_understanding(columns):
    """业务语义理解"""
    # 常见业务术语映射
    term_mapping = {
        'sales': {'type': '金额', 'meaning': '销售收入'},
        'revenue': {'type': '金额', 'meaning': '营业收入'},
        'amount': {'type': '金额', 'meaning': '金额'},
        'quantity': {'type': '数量', 'meaning': '数量'},
        'qty': {'type': '数量', 'meaning': '数量'},
        'count': {'type': '数量', 'meaning': '数量'},
        'region': {'type': '区域', 'meaning': '销售区域'},
        'area': {'type': '区域', 'meaning': '区域'},
        'province': {'type': '区域', 'meaning': '省份'},
        'city': {'type': '区域', 'meaning': '城市'},
        'period': {'type': '时间', 'meaning': '统计周期'},
        'date': {'type': '时间', 'meaning': '日期'},
        'month': {'type': '时间', 'meaning': '月份'},
        'quarter': {'type': '时间', 'meaning': '季度'},
        'year': {'type': '时间', 'meaning': '年份'},
        'product': {'type': '产品', 'meaning': '产品'},
        'category': {'type': '分类', 'meaning': '类别'},
        'customer': {'type': '客户', 'meaning': '客户'},
        'customer_type': {'type': '分类', 'meaning': '客户类型'},
        'channel': {'type': '渠道', 'meaning': '销售渠道'},
        'profit': {'type': '金额', 'meaning': '利润'},
        'cost': {'type': '金额', 'meaning': '成本'},
    }
    
    result = {}
    for col in columns:
        col_lower = col.lower()
        matched = False
        
        for key, value in term_mapping.items():
            if key in col_lower:
                result[col] = value
                matched = True
                break
        
        if not matched:
            result[col] = {'type': '未知', 'meaning': col}
    
    return result

def detect_anomalies(data):
    """异常检测"""
    anomalies = []
    
    # 查找数值列
    numeric_cols = []
    for col in data.get('columns', []):
        # 检查数据中的值
        values = [row.get(col) for row in data.get('data', []) if row.get(col) is not None]
        if values and all(isinstance(v, (int, float)) for v in values):
            numeric_cols.append(col)
    
    for col in numeric_cols:
        values = [row[col] for row in data['data'] if row.get(col) is not None]
        if len(values) < 3:
            continue
        
        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)
        
        # 3σ 异常
        if std > 0:
            for i, val in enumerate(values):
                if abs(val - mean) > 3 * std:
                    anomalies.append({
                        'type': '数值异常',
                        'column': col,
                        'value': float(val),
                        'mean': float(mean),
                        'deviation': f'{abs(val - mean) / std:.1f}σ',
                        'severity': '高' if abs(val - mean) > 4 * std else '中'
                    })
    
    return anomalies

def compare_periods(data, current_period, baseline_period):
    """对比分析（简化版：与上期/同期对比）"""
    comparisons = []
    
    # 尝试提取数值列进行对比
    numeric_cols = []
    for col in data.get('columns', []):
        values = [row.get(col) for row in data.get('data', []) if row.get(col) is not None]
        if values and all(isinstance(v, (int, float)) for v in values):
            numeric_cols.append(col)
    
    if not numeric_cols:
        return comparisons
    
    # 模拟对比（实际应该从缓存中读取对比数据）
    # 这里返回对比框架，实际数据需要通过 Data Processing 获取
    for col in numeric_cols[:3]:  # 取前3个数值列
        comparisons.append({
            'column': col,
            'type': '趋势对比',
            'note': '需要额外数据处理才能完成对比'
        })
    
    return comparisons

def causal_analysis(data, goal, business_knowledge=None):
    """归因分析（简化版）"""
    
    # 解析目标
    # 例如："华东区Q3销量下降原因" -> 目标:销量, 维度:华东区, 时间:Q3
    
    findings = []
    
    # 基础统计
    if 'summary' in data:
        for col, stats in data.get('summary', {}).items():
            if isinstance(stats, dict) and 'sum' in stats:
                findings.append({
                    'factor': col,
                    'metric': '总和',
                    'value': stats.get('sum'),
                    'note': '基础指标'
                })
    
    # 异常分析
    anomalies = detect_anomalies(data)
    if anomalies:
        findings.append({
            'type': '异常点',
            'count': len(anomalies),
            'items': anomalies[:3]
        })
    
    return {
        'analysis_type': '归因分析',
        'target': goal,
        'findings': findings,
        'note': '需要更多维度数据才能深入归因'
    }

def generate_recommendations(causal_result, business_knowledge=None):
    """生成行动建议"""
    
    recommendations = []
    
    # 基于归因结果生成建议
    if causal_result.get('findings'):
        recommendations.append({
            'priority': '高',
            'horizon': '短期',
            'action': '进一步收集维度数据',
            'detail': '当前分析基于聚合数据，建议按维度拆分（如地区/产品/客户）进行深入分析',
            'expected_impact': '更精确的归因'
        })
    
    # 通用建议
    recommendations.extend([
        {
            'priority': '中',
            'horizon': '中期',
            'action': '建立数据监控体系',
            'detail': '设置关键指标预警阈值，及早发现异常',
            'expected_impact': '提前预警，快速响应'
        },
        {
            'priority': '低',
            'horizon': '长期',
            'action': '完善数据采集',
            'detail': '丰富维度数据，为深度分析提供基础',
            'expected_impact': '支持更精准的决策'
        }
    ])
    
    return recommendations

def analyze(cache_dir, goal, business_knowledge=None):
    """主分析函数"""
    
    # 加载缓存数据
    cache_data = load_cache(cache_dir)
    
    if not cache_data:
        return {
            'error': '缓存目录为空或不存在',
            'hint': '请先调用 Data Processing 生成缓存数据'
        }
    
    # 合并所有缓存数据
    all_data = {'columns': [], 'data': [], 'summary': {}}
    
    for filename, content in cache_data.items():
        if filename.startswith('query_'):
            if 'columns' in content and content['columns']:
                all_data['columns'].extend([c for c in content['columns'] if c not in all_data['columns']])
                all_data['data'].extend(content.get('data', [])[:50])  # 限制数据量
            if 'summary' in content:
                all_data['summary'].update(content['summary'])
        elif filename.startswith('summary_'):
            if 'metrics' in content:
                all_data['summary'].update(content['metrics'])
    
    # 1. 语义理解
    semantic = semantic_understanding(all_data.get('columns', []))
    
    # 2. 异常检测
    anomalies = detect_anomalies(all_data)
    
    # 3. 归因分析
    causal = causal_analysis(all_data, goal, business_knowledge)
    
    # 4. 对比分析（框架）
    comparisons = compare_periods(all_data, None, None)
    
    # 5. 行动建议
    recommendations = generate_recommendations(causal, business_knowledge)
    
    # 输出结果
    result = {
        'analysis_id': f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'goal': goal,
        'timestamp': datetime.now().isoformat(),
        
        'semantic_understanding': semantic,
        
        'anomalies': anomalies,
        
        'causal_analysis': causal,
        
        'comparisons': comparisons,
        
        'recommendations': recommendations,
        
        'data_sources': list(cache_data.keys()),
        'data_summary': {
            'total_records': len(all_data.get('data', [])),
            'total_columns': len(all_data.get('columns', []))
        }
    }
    
    # 写入缓存
    output_file = os.path.join(cache_dir, 'diagnostic_result.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, default=str)
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Diagnostic Analysis Script')
    parser.add_argument('--cache-dir', required=True, help='缓存目录路径')
    parser.add_argument('--goal', required=True, help='分析目标/问题')
    parser.add_argument('--business-knowledge', help='企业知识（JSON字符串）')
    
    args = parser.parse_args()
    
    # 解析企业知识
    business_knowledge = None
    if args.business_knowledge:
        try:
            business_knowledge = json.loads(args.business_knowledge)
        except:
            pass
    
    # 执行分析
    result = analyze(args.cache_dir, args.goal, business_knowledge)
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, default=str))

if __name__ == '__main__':
    main()