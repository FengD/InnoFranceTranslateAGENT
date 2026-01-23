import json
import re
from typing import Dict, Any, List

def load_input_data(file_path: str) -> Dict[str, Any]:
    """
    Load input data file
    
    Args:
        file_path: File path
        
    Returns:
        Parsed data dictionary
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
    # Try to parse as JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # If not valid JSON, treat as plain text
        return {"text": content}

def save_output_data(data: str, file_path: str) -> None:
    """
    Save output data to file
    
    Args:
        data: Data to save
        file_path: File path
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)

def validate_input_data(data: Dict[str, Any]) -> bool:
    """
    Validate input data format
    
    Args:
        data: Input data
        
    Returns:
        Whether it is valid
    """
    # Check if it's segments format
    if "segments" in data:
        if not isinstance(data["segments"], list):
            return False
        for segment in data["segments"]:
            if not isinstance(segment, dict):
                return False
            if "text" not in segment or "speaker" not in segment:
                return False
        return True
    
    # Check if it's plain text
    if "text" in data:
        return isinstance(data["text"], str)
    
    return False

def format_segments_for_display(segments: List[Dict[str, Any]]) -> str:
    """
    Format segments for display
    
    Args:
        segments: Segments list
        
    Returns:
        Formatted string
    """
    formatted = []
    for segment in segments:
        speaker = segment.get("speaker", "UNKNOWN")
        text = segment.get("text", "")
        formatted.append(f"[{speaker}] {text}")
    return "\n".join(formatted)

def clean_translation_output(output: str) -> str:
    """
    Clean translation output, removing unnecessary parts
    
    Args:
        output: Raw output
        
    Returns:
        Cleaned output
    """
    # Remove possible prefix explanations
    lines = output.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip empty lines and explanatory text
        if (line.strip() and
            not line.startswith("Translation result") and
            not line.startswith("The following is") and
            not line.startswith("According to") and
            not line.startswith("Note")):
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def extract_speaker_content(text: str) -> List[Dict[str, str]]:
    """
    Extract speaker content from text
    
    Args:
        text: Text containing speaker tags
        
    Returns:
        Extracted speaker content list
    """
    # Match speaker tags in [SPEAKERn] format
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
        # If no speaker tags are matched, treat the entire text as one entry
        results.append({"speaker": "SPEAKER0", "content": text.strip()})
    
    return results