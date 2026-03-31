#!/usr/bin/env python3
"""
Data Analysis Main Skill - 主控脚本
负责：理解需求、调度子 Skill、验收结果、清理缓存
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime

# 缓存目录
CACHE_BASE = "/mnt/user-data/workspace/.analysis-cache"

# SKILL 脚本路径
DATA_PROCESSING_SCRIPT = "/mnt/skills/public/data-processing/scripts/process.py"
DIAGNOSTIC_SCRIPT = "/mnt/skills/public/diagnostic-analysis/scripts/analyze.py"

def parse_goal(user_input):
    """解析用户目标，判断需要什么处理"""
    
    # 关键词判断
    data_keywords = ['多少', '占比', '统计', '查询', '数据', '销量', '销售额', '数量']
    analysis_keywords = ['为什么', '原因', '分析', '怎么办', '建议', '下降', '上升', '增长']
    
    needs_data = any(kw in user_input for kw in data_keywords)
    needs_analysis = any(kw in user_input for kw in analysis_keywords)
    
    # 提取关键实体
    entities = {
        'region': None,  # 区域
        'period': None,  # 时间周期
        'product': None, # 产品
        'metric': None   # 指标
    }
    
    # 区域识别
    regions = ['华东', '华南', '华北', '华中', '西南', '西北', '东北', '全国']
    for r in regions:
        if r in user_input:
            entities['region'] = r
            break
    
    # 时间识别
    periods = ['Q1', 'Q2', 'Q3', 'Q4', '1月', '2月', '3月', '上半年', '下半年', '全年']
    for p in periods:
        if p in user_input:
            entities['period'] = p
            break
    
    return {
        'needs_data': needs_data,
        'needs_analysis': needs_analysis,
        'entities': entities,
        'original_input': user_input
    }

def create_session():
    """创建新的分析会话"""
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_dir = os.path.join(CACHE_BASE, session_id)
    os.makedirs(session_dir, exist_ok=True)
    return session_id, session_dir

def call_data_processing(files, action, sql=None, table=None, session_id='default'):
    """调用 Data Processing Skill"""
    
    cmd = [
        'python', DATA_PROCESSING_SCRIPT,
        '--files', files,
        '--action', action,
        '--session-id', session_id
    ]
    
    if sql:
        cmd.extend(['--sql', sql])
    if table:
        cmd.extend(['--table', table])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {'error': result.stderr}
    except Exception as e:
        return {'error': str(e)}

def call_diagnostic(cache_dir, goal, business_knowledge=None):
    """调用 Diagnostic Skill"""
    
    cmd = [
        'python', DIAGNOSTIC_SCRIPT,
        '--cache-dir', cache_dir,
        '--goal', goal
    ]
    
    if business_knowledge:
        cmd.extend(['--business-knowledge', json.dumps(business_knowledge)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {'error': result.stderr}
    except Exception as e:
        return {'error': str(e)}

def evaluate_analysis(result, user_input):
    """评估分析结果是否到位"""
    
    if 'error' in result:
        return False, f"分析出错: {result.get('error')}"
    
    # 检查必要字段
    required = ['causal_analysis', 'recommendations']
    missing = [f for f in required if f not in result]
    
    if missing:
        return False, f"缺少关键字段: {missing}"
    
    # 检查归因是否有实质内容
    causal = result.get('causal_analysis', {})
    if not causal.get('findings'):
        return False, "归因分析缺乏实质发现"
    
    # 检查建议是否具体
    recommendations = result.get('recommendations', [])
    if not recommendations:
        return False, "没有行动建议"
    
    return True, "分析到位"

def format_output(result):
    """格式化输出给用户"""
    
    output = []
    
    # 归因分析
    if 'causal_analysis' in result:
        causal = result['causal_analysis']
        output.append("## 分析结论\n")
        if 'findings' in causal:
            for f in causal['findings'][:3]:
                output.append(f"- {f}")
        output.append("")
    
    # 建议
    if 'recommendations' in result:
        output.append("## 行动建议\n")
        for rec in result['recommendations'][:3]:
            priority_emoji = "🔴" if rec.get('priority') == '高' else "🟡" if rec.get('priority') == '中' else "🟢"
            output.append(f"{priority_emoji} [{rec.get('horizon', '未知')}] {rec.get('action', '')}")
        output.append("")
    
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description='Data Analysis Main Coordinator')
    parser.add_argument('--user-input', required=True, help='用户输入')
    parser.add_argument('--data-files', help='数据文件路径')
    parser.add_argument('--business-knowledge', help='企业知识（JSON）')
    parser.add_argument('--create-session', action='store_true', help='创建新会话')
    
    args = parser.parse_args()
    
    # 1. 解析目标
    parsed = parse_goal(args.user_input)
    print(f"解析结果: 需要数据={parsed['needs_data']}, 需要分析={parsed['needs_analysis']}")
    print(f"识别实体: {parsed['entities']}")
    
    # 2. 创建会话
    if args.create_session:
        session_id, session_dir = create_session()
    else:
        session_id = 'default'
        session_dir = os.path.join(CACHE_BASE, session_id)
        os.makedirs(session_dir, exist_ok=True)
    
    print(f"会话目录: {session_dir}")
    
    results = {}
    
    # 3. 如果需要数据，调用 Data Processing
    if parsed['needs_data'] and args.data_files:
        print("\n=== 调用 Data Processing ===")
        
        # 构建查询
        entities = parsed['entities']
        
        # 简单示例：根据实体构建 SQL
        if entities['region']:
            sql = f"SELECT region, SUM(sales) as total_sales FROM orders WHERE region='{entities['region']}' GROUP BY region"
        else:
            sql = "SELECT region, SUM(sales) as total_sales FROM orders GROUP BY region"
        
        dp_result = call_data_processing(args.data_files, 'query', sql=sql, session_id=session_id)
        results['data_processing'] = dp_result
        print(f"数据处理结果: {json.dumps(dp_result, ensure_ascii=False)[:200]}...")
    
    # 4. 如果需要分析，调用 Diagnostic
    if parsed['needs_analysis']:
        print("\n=== 调用 Diagnostic ===")
        
        diagnostic_result = call_diagnostic(session_dir, args.user_input)
        results['diagnostic'] = diagnostic_result
        
        # 评估结果
        is_enough, message = evaluate_analysis(diagnostic_result, args.user_input)
        print(f"评估结果: {message}")
        
        # 格式化输出
        output = format_output(diagnostic_result)
        print("\n=== 最终输出 ===")
        print(output)
    
    # 5. 写入会话结果
    result_file = os.path.join(session_dir, 'session_result.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, default=str)
    
    print(f"\n结果已保存到: {result_file}")

if __name__ == '__main__':
    main()