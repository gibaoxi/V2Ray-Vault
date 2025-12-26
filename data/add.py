import json
import os
from datetime import datetime, timedelta
import requests
import time

def check_link_exists(url, timeout=5):
    """检查链接是否能正常访问"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False
    except Exception:
        return False

def get_valid_link(max_days_back=7):
    """
    获取有效的链接，最多回溯max_days_back天
    返回: 有效的链接
    """
    base_url = "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v"
    current_date = datetime.now()
    
    print(f"开始检测链接有效性（最多回溯{max_days_back}天）...")
    print(f"当前日期: {current_date.strftime('%Y-%m-%d')}")
    print("-" * 60)
    
    found_url = None
    found_date = None
    
    for i in range(max_days_back):
        # 计算检查的日期
        check_date = current_date - timedelta(days=i)
        date_str = check_date.strftime("%Y%m%d")
        test_url = f"{base_url}{date_str}"
        
        print(f"检查 {check_date.strftime('%Y-%m-%d')} ({date_str}): ", end="")
        
        if check_link_exists(test_url):
            print("✓ 可用")
            found_url = test_url
            found_date = check_date
            break  # 找到后立即停止
        else:
            print("✗ 不可用")
        
        time.sleep(0.5)  # 稍微延迟一下
    
    print("-" * 60)
    
    if found_url:
        print(f"✅ 找到有效链接: {found_url}")
        print(f"📅 链接日期: {found_date.strftime('%Y-%m-%d')}")
        if (current_date - found_date).days > 0:
            print(f"⚠️  注意: 这不是今天的链接，是 {found_date.strftime('%Y-%m-%d')} 的链接")
        return found_url
    else:
        # 如果所有都不可用，使用最后一天的链接
        last_date = current_date - timedelta(days=max_days_back-1)
        last_date_str = last_date.strftime("%Y%m%d")
        fallback_url = f"{base_url}{last_date_str}"
        print(f"⚠️  {max_days_back}天内都未找到有效链接")
        print(f"⚠️  使用最后一天的链接: {fallback_url}")
        return fallback_url

def update_subscription_links():
    """更新订阅链接JSON文件"""
    # 文件路径
    json_file_path = "data/Extract/subscription_link.json"
    
    print("=" * 60)
    print("订阅链接更新工具")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"JSON文件路径: {json_file_path}")
    print("=" * 60)
    
    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"❌ 错误: 文件 {json_file_path} 不存在")
        
        # 尝试自动创建目录和文件
        try:
            os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
            print(f"✅ 已创建新文件: {json_file_path}")
        except Exception as e:
            print(f"❌ 创建文件失败: {e}")
        return
    
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 成功读取JSON文件，包含 {len(data)} 个链接")
        
        # 确保数据是列表类型
        if not isinstance(data, list):
            print("❌ 错误: JSON文件内容不是数组")
            return
        
        # 显示原始链接
        if data:
            print("\n原始链接列表:")
            for i, link in enumerate(data, 1):
                print(f"{i:2d}. {link}")
        else:
            print("\n当前链接列表为空")
        
        # 1. 删除最后一个元素
        if data:
            removed_item = data.pop()
            print(f"\n🗑️ 已删除最后一个链接: {removed_item}")
        else:
            print("\n数组为空，无需删除")
        
        # 2. 生成有效的链接
        new_link = get_valid_link()
        
        # 3. 检查是否已存在相同链接
        if new_link in data:
            print(f"\n⚠️  链接已存在，跳过添加: {new_link}")
        else:
            # 添加新链接到数组末尾
            data.append(new_link)
            print(f"\n✅ 已添加到数组末尾")
        
        # 4. 写回JSON文件
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("更新完成！当前链接列表:")
        for i, link in enumerate(data, 1):
            print(f"{i:2d}. {link}")
        
        print(f"\n✅ 文件已保存: {json_file_path}")
        print(f"✅ 总链接数: {len(data)}")
        print("=" * 60)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        print("请检查JSON文件格式是否正确")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

def test_link_check():
    """测试链接检查功能"""
    print("=" * 60)
    print("链接检查功能测试")
    print("=" * 60)
    
    # 测试一些日期
    test_dates = [
        datetime.now(),
        datetime.now() - timedelta(days=1),
        datetime.now() - timedelta(days=2),
        datetime.now() - timedelta(days=3)
    ]
    
    base_url = "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v1"
    
    for test_date in test_dates:
        date_str = test_date.strftime("%Y%m%d")
        url = f"{base_url}{date_str}"
        exists = check_link_exists(url)
        status = "✓ 可用" if exists else "✗ 不可用"
        print(f"{test_date.strftime('%Y-%m-%d')}: {status} - {url}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_link_check()
    else:
        update_subscription_links()
