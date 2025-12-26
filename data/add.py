import json
import os
from datetime import datetime

def update_subscription_links():
    """更新订阅链接JSON文件"""
    # 当前脚本在data文件夹下，Extract也在data文件夹下
    json_file_path = "Extract/subscription_link.json"
    
    print(f"当前工作目录: {os.getcwd()}")
    print(f"JSON文件路径: {json_file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"错误: 文件 {json_file_path} 不存在")
        
        # 尝试列出当前目录内容
        print("\n当前目录结构:")
        for item in os.listdir('.'):
            if os.path.isdir(item):
                print(f"[目录] {item}/")
                # 如果是Extract目录，列出里面的内容
                if item == "Extract":
                    for sub_item in os.listdir(item):
                        print(f"  ├─ {sub_item}")
            else:
                print(f"[文件] {item}")
        
        return
    
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"成功读取JSON文件，包含 {len(data)} 个链接")
        
        # 确保数据是列表类型
        if not isinstance(data, list):
            print("错误: JSON文件内容不是数组")
            return
        
        # 显示原始链接
        print("\n原始链接列表:")
        for i, link in enumerate(data, 1):
            print(f"{i}. {link}")
        
        # 1. 删除最后一个元素
        if data:
            removed_item = data.pop()
            print(f"\n已删除最后一个链接: {removed_item}")
        else:
            print("\n数组为空，无需删除")
        
        # 2. 生成新链接
        today = datetime.now().strftime("%Y%m%d")
        new_link = f"https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v{today}"
        print(f"生成今日链接: {new_link}")
        
        # 3. 添加新链接到数组末尾
        data.append(new_link)
        print(f"已添加到数组末尾")
        
        # 4. 写回JSON文件
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("\n更新完成！当前链接列表:")
        for i, link in enumerate(data, 1):
            print(f"{i}. {link}")
        
        print(f"\n✓ 文件已保存到: {json_file_path}")
        print(f"✓ 总链接数: {len(data)}")
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print("请检查JSON文件格式是否正确")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始更新订阅链接...")
    print("=" * 50)
    update_subscription_links()
    print("=" * 50)
    print("更新完成！")
