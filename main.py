from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import subprocess
import tempfile
import os
import uuid
import atexit

app = FastAPI(title="LinearDesign API", description="mRNA序列优化设计服务")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LinearDesignRequest(BaseModel):
    sequence: Optional[str] = None
    lambda_param: float = 0.0
    codon_usage: str = "codon_usage_freq_table_human.csv"

@app.post("/tools/linearDesign", 
    summary="蛋白质序列转mRNA序列优化",
    description="将单个蛋白质序列或FASTA文件转换为优化的mRNA序列，支持自定义密码子表和lambda参数调节"
)
async def linear_design(
    sequence: Optional[str] = Form(None, description="单个蛋白质序列字符串，如'MNDTEAI'，与file参数二选一"),
    file: Optional[UploadFile] = File(None, description="FASTA格式蛋白质序列文件，支持多序列，与sequence参数二选一"),
    lambda_param: float = Form(0.0, description="平衡MFE和CAI的超参数，默认0.0，建议范围0.0-10.0"),
    codon_usage: Optional[UploadFile] = File(None, description="自定义密码子使用频率表文件（CSV格式），可选")
):
    """
    LinearDesign API端点 - 将蛋白质序列转换为优化的mRNA序列
    
    ## 参数说明
    - **sequence**: 单个蛋白质序列字符串 (与file参数二选一)
    - **file**: FASTA格式蛋白质序列文件 (与sequence参数二选一)
    - **lambda_param**: 平衡MFE和CAI的超参数，默认0.0
    - **codon_usage**: 自定义密码子使用频率表文件，可选
    
    ## 返回结果
    返回包含优化mRNA序列、结构、自由能和CAI的JSON对象
    
    ## 错误代码
    - 400: 参数验证失败
    - 500: 服务器内部错误或程序执行失败
    """
    
    # 验证输入
    if not sequence and not file:
        return JSONResponse(
            status_code=400,
            content={"error": "必须提供sequence参数或file参数"}
        )
    
    if sequence and file:
        return JSONResponse(
            status_code=400,
            content={"error": "只能提供sequence参数或file参数中的一个"}
        )
    
    try:
        # 准备输入数据
        input_data = ""
        
        if sequence:
            # 处理单个序列
            input_data = sequence
        else:
            # 处理文件上传
            content = await file.read()
            input_data = content.decode('utf-8')
        
        # 处理密码子使用频率表文件
        codon_table_path = "./codon_usage_freq_table_human.csv"  # 默认文件
        temp_codon_file = None
        
        if codon_usage:
            # 如果用户上传了密码子表文件，保存并使用
            codon_content = await codon_usage.read()
            codon_filename = f"temp_codon_table_{uuid.uuid4().hex}.csv"
            codon_table_path = f"./{codon_filename}"
            temp_codon_file = codon_table_path
            
            with open(codon_table_path, 'wb') as f:
                f.write(codon_content)
        
        # 构建命令行参数 (lambda需要乘以100)
        cmd = [
            "./bin/LinearDesign_2D",
            str(lambda_param),  # lambda不需要乘以100，程序内部会处理
            "0",  # verbose设置为False
            codon_table_path
        ]
        
        # 执行LinearDesign程序
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "LinearDesign执行失败",
                    "stderr": result.stderr
                }
            )
        
        # 解析输出结果 - 过滤调试信息行
        output_lines = result.stdout.strip().split('\n')
        results = []
        current_result = {}
        
        for line in output_lines:
            # 跳过调试信息行 (j=0, j=1, ...)
            if line.startswith('j='):
                continue
                
            if line.startswith('>'):
                if current_result:
                    results.append(current_result)
                current_result = {"sequence_name": line[1:].strip()}
            elif line.startswith('mRNA sequence:'):
                current_result["mrna_sequence"] = line.split(':', 1)[1].strip()
            elif line.startswith('mRNA structure:'):
                current_result["mrna_structure"] = line.split(':', 1)[1].strip()
            elif line.startswith('mRNA folding free energy:'):
                parts = line.split(';')
                energy_part = parts[0].split(':')
                cai_part = parts[1].split(':')
                
                current_result["folding_free_energy"] = float(energy_part[1].split()[0])
                current_result["cai"] = float(cai_part[1].strip())
        
        if current_result:
            results.append(current_result)
        
        # 如果没有序列名称，则为单个序列结果
        if len(results) == 1 and "sequence_name" not in results[0]:
            results[0]["sequence_name"] = "single_sequence"
        
        # 清理临时文件
        if temp_codon_file and os.path.exists(temp_codon_file):
            os.remove(temp_codon_file)
        
        return {
            "status": "success",
            "lambda_parameter": lambda_param,
            "codon_usage_table": "custom_uploaded" if codon_usage else "codon_usage_freq_table_human.csv",
            "results": results
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"处理请求时发生错误: {str(e)}"}
        )

@app.get("/")
async def root():
    return {"message": "LinearDesign API服务运行中", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)