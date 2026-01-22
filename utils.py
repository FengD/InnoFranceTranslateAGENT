import json
import re
from typing import Dict, Any, List

def load_input_data(file_path: str) -> Dict[str, Any]:
    """
    加载输入数据文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        解析后的数据字典
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
    # 尝试解析为JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 如果不是有效的JSON，将其作为纯文本处理
        return {"text": content}

def save_output_data(data: str, file_path: str) -> None:
    """
    保存输出数据到文件
    
    Args:
        data: 要保存的数据
        file_path: 文件路径
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)

def validate_input_data(data: Dict[str, Any]) -> bool:
    """
    验证输入数据格式
    
    Args:
        data: 输入数据
        
    Returns:
        是否有效
    """
    # 检查是否为segments格式
    if "segments" in data:
        if not isinstance(data["segments"], list):
            return False
        for segment in data["segments"]:
            if not isinstance(segment, dict):
                return False
            if "text" not in segment or "speaker" not in segment:
                return False
        return True
    
    # 检查是否为纯文本
    if "text" in data:
        return isinstance(data["text"], str)
    
    return False

def format_segments_for_display(segments: List[Dict[str, Any]]) -> str:
    """
    格式化segments用于显示
    
    Args:
        segments: segments列表
        
    Returns:
        格式化后的字符串
    """
    formatted = []
    for segment in segments:
        speaker = segment.get("speaker", "UNKNOWN")
        text = segment.get("text", "")
        formatted.append(f"[{speaker}] {text}")
    return "\n".join(formatted)

def clean_translation_output(output: str) -> str:
    """
    清理翻译输出，移除不必要的部分
    
    Args:
        output: 原始输出
        
    Returns:
        清理后的输出
    """
    # 移除可能的前缀说明
    lines = output.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 跳过空行和说明性文字
        if (line.strip() and 
            not line.startswith("翻译结果") and 
            not line.startswith("以下是") and
            not line.startswith("根据") and
            not line.startswith("注意")):
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def extract_speaker_content(text: str) -> List[Dict[str, str]]:
    """
    从文本中提取说话人内容
    
    Args:
        text: 包含说话人标签的文本
        
    Returns:
        提取的说话人内容列表
    """
    # 匹配[SPEAKERn]格式的说话人标签
    pattern = r'\[(SPEAKER\d+)\]\s*(.*?)(?=\n\[(SPEAKER\d+)\]|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    results = []
    if matches:
        for match in matches:
            speaker = match[0]
            content = match[1].strip()
            if content:
                results.append({"speaker": speaker, "content": content})
    else:
        # 如果没有匹配到说话人标签，将整个文本作为一个条目
        results.append({"speaker": "SPEAKER0", "content": text.strip()})
    
    return results