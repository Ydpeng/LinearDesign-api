#!/usr/bin/env python3
"""
LinearDesign API 测试脚本
"""
import requests
import json
import time
import os

def test_single_sequence():
    """测试单个序列"""
    print("=== 测试单个序列 ===")
    
    url = 'http://localhost:8000/tools/linearDesign'
    data = {
        'sequence': 'MNDTEAI',
        'lambda_param': 0.0,
        'codon_usage': 'codon_usage_freq_table_human.csv'
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ 单个序列测试成功")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_file_upload():
    """测试文件上传"""
    print("\n=== 测试文件上传 ===")
    
    url = 'http://localhost:8000/tools/linearDesign'
    
    # 创建测试文件
    test_content = ">seq1\nMPNTLACP\n>seq2\nMLDQVNKLKYPEVSLT*"
    
    files = {'file': ('test.fasta', test_content, 'text/plain')}
    data = {
        'lambda_param': 3.0,
        'codon_usage': 'codon_usage_freq_table_human.csv'
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ 文件上传测试成功")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_different_lambda():
    """测试不同lambda参数"""
    print("\n=== 测试不同lambda参数 ===")
    
    url = 'http://localhost:8000/tools/linearDesign'
    
    for lambda_val in [0.0, 1.0, 2.0]:
        print(f"\n测试 lambda={lambda_val}")
        data = {
            'sequence': 'MNDTEAI',
            'lambda_param': lambda_val,
            'codon_usage': 'codon_usage_freq_table_human.csv'
        }
        
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print(f"✅ lambda={lambda_val} 测试成功")
            else:
                print(f"❌ lambda={lambda_val} 测试失败")
        except Exception as e:
            print(f"❌ lambda={lambda_val} 请求异常: {str(e)}")

def main():
    """主测试函数"""
    print("LinearDesign API 测试开始...")
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(5)
    
    # 测试根路径
    try:
        response = requests.get('http://localhost:8000/')
        print(f"根路径测试: {response.status_code}")
        if response.status_code == 200:
            print("✅ 服务运行正常")
    except:
        print("❌ 服务未启动，请先启动服务")
        return
    
    # 执行测试
    success_count = 0
    total_tests = 3
    
    if test_single_sequence():
        success_count += 1
    
    if test_file_upload():
        success_count += 1
    
    test_different_lambda()
    
    print(f"\n=== 测试总结 ===")
    print(f"成功测试: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查服务配置")

if __name__ == "__main__":
    main()