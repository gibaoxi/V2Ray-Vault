import json
import os
from datetime import datetime

def update_subscription_links():
    # 文件路径
    json_file_path = os.path.join("Extract", "subscription_link.json")
    
    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"错误: 文件 {json_file_path} 不存在")
        return
    
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 确保数据是列表类型
        if not isinstance(data, list):
            print("错误: JSON文件内容不是数组")
            return
        
        # 1. 删除最后一个元素
        if data:
            data.pop()
            print("已删除最后一个链接")
        
        # 2. 生成新链接
        today = datetime.now().strftime("%Y%m%d")
        new_link = f"https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v{today}"
        
        # 3. 添加新链接到数组末尾
        data.append(new_link)
        print(f"已添加链接: {new_link}")
        
        # 写回JSON文件
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("文件更新成功!")
        print(f"当前链接数量: {len(data)}")
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

# 运行函数
if __name__ == "__main__":
    update_subscription_links()
