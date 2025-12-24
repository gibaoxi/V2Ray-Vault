#!/usr/bin/env python3
"""
高速代理连通性测试工具
专注于快速、准确的代理节点测试
"""

import asyncio
import aiohttp
import time
import json
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import base64
import re

@dataclass
class ProxyConfig:
    """代理配置"""
    url: str
    protocol: str
    host: str
    port: int
    name: str = ""
    latency: float = 0.0
    status: str = "pending"
    error: str = ""

class FastProxyTester:
    def __init__(self, max_concurrent=50, timeout=8):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # 测试目标（选择响应快的网站）
        self.test_targets = [
            "http://www.gstatic.com/generate_204",  # Google - 响应快
            "http://connectivitycheck.gstatic.com/generate_204",  # 连通性检查
            "http://cp.cloudflare.com/",  # Cloudflare
            "http://1.1.1.1/",  # Cloudflare DNS
        ]
    
    def parse_proxy_links(self, file_path: str) -> List[ProxyConfig]:
        """从文件解析代理链接"""
        configs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    config = self._parse_single_link(line)
                    if config:
                        configs.append(config)
            
            print(f"✅ 解析完成: {len(configs)} 个代理配置")
            return configs
            
        except Exception as e:
            print(f"❌ 解析文件失败: {e}")
            return []
    
    def _parse_single_link(self, link: str) -> Optional[ProxyConfig]:
        """解析单个代理链接"""
        try:
            if link.startswith('ss://'):
                return self._parse_ss(link)
            elif link.startswith('vmess://'):
                return self._parse_vmess(link)
            elif link.startswith('trojan://'):
                return self._parse_trojan(link)
            elif link.startswith('vless://'):
                return self._parse_vless(link)
            else:
                return None
        except:
            return None
    
    def _parse_ss(self, link: str) -> Optional[ProxyConfig]:
        """解析SS链接"""
        try:
            # ss://method:password@host:port#name
            if '#' in link:
                link, name = link.split('#', 1)
                name = name.strip()
            else:
                name = "SS-Node"
            
            # 提取基础部分
            if '@' in link:
                user_info, server_part = link[5:].split('@', 1)
            else:
                # 处理base64编码的格式
                b64_part = link[5:].split('#')[0]
                decoded = base64.b64decode(b64_part + '==').decode()
                user_info, server_part = decoded.split('@', 1)
            
            host, port = server_part.split(':', 1)
            port = int(port)
            
            return ProxyConfig(
                url=link,
                protocol="ss",
                host=host,
                port=port,
                name=name
            )
        except:
            return None
    
    def _parse_vmess(self, link: str) -> Optional[ProxyConfig]:
        """解析VMess链接"""
        try:
            b64_data = link[8:].split('#')[0]
            decoded = base64.b64decode(b64_data + '==').decode()
            config = json.loads(decoded)
            
            name = config.get('ps', 'VMess-Node')
            host = config.get('add', '')
            port = int(config.get('port', 443))
            
            return ProxyConfig(
                url=link,
                protocol="vmess",
                host=host,
                port=port,
                name=name
            )
        except:
            return None
    
    def _parse_trojan(self, link: str) -> Optional[ProxyConfig]:
        """解析Trojan链接"""
        try:
            parsed = urlparse(link)
            host = parsed.hostname
            port = parsed.port or 443
            name = parsed.fragment or "Trojan-Node"
            
            return ProxyConfig(
                url=link,
                protocol="trojan",
                host=host,
                port=port,
                name=name
            )
        except:
            return None
    
    def _parse_vless(self, link: str) -> Optional[ProxyConfig]:
        """解析VLESS链接"""
        try:
            parsed = urlparse(link)
            host = parsed.hostname
            port = parsed.port or 443
            name = parsed.fragment or "VLESS-Node"
            
            return ProxyConfig(
                url=link,
                protocol="vless",
                host=host,
                port=port,
                name=name
            )
        except:
            return None
    
    async def test_single_proxy(self, config: ProxyConfig) -> ProxyConfig:
        """测试单个代理"""
        async with self.semaphore:
            start_time = time.time()
            
            try:
                # 使用aiohttp测试代理
                async with aiohttp.ClientSession() as session:
                    # 随机选择一个测试目标
                    test_url = random.choice(self.test_targets)
                    
                    proxy_url = self._build_proxy_url(config)
                    
                    async with session.get(
                        test_url,
                        proxy=proxy_url,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                        headers={'User-Agent': 'Mozilla/5.0'}
                    ) as response:
                        if response.status in [200, 204]:
                            latency = (time.time() - start_time) * 1000
                            config.latency = round(latency, 2)
                            config.status = "success"
                        else:
                            config.status = "failed"
                            config.error = f"HTTP {response.status}"
                
            except asyncio.TimeoutError:
                config.status = "timeout"
                config.error = "请求超时"
            except Exception as e:
                config.status = "error"
                config.error = str(e)
            
            return config
    
    def _build_proxy_url(self, config: ProxyConfig) -> str:
        """构建代理URL"""
        if config.protocol == "ss":
            return f"socks5://{config.host}:{config.port}"
        elif config.protocol in ["vmess", "vless", "trojan"]:
            return f"socks5://{config.host}:{config.port}"
        else:
            return f"http://{config.host}:{config.port}"
    
    async def batch_test(self, configs: List[ProxyConfig]) -> List[ProxyConfig]:
        """批量测试代理"""
        print(f"🚀 开始测试 {len(configs)} 个代理节点...")
        print(f"⚡ 并发数: {self.max_concurrent}, 超时: {self.timeout}秒")
        
        tasks = [self.test_single_proxy(config) for config in configs]
        
        # 显示进度
        completed = 0
        total = len(tasks)
        
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            completed += 1
            
            # 每完成10个或最后显示进度
            if completed % 10 == 0 or completed == total:
                success_count = len([c for c in configs if c.status == "success"])
                print(f"📊 进度: {completed}/{total} | 成功: {success_count}")
        
        return configs
    
    def save_results(self, configs: List[ProxyConfig], output_file: str):
        """保存测试结果"""
        # 按延迟排序
        working_configs = [c for c in configs if c.status == "success"]
        working_configs.sort(key=lambda x: x.latency)
        
        failed_configs = [c for c in configs if c.status != "success"]
        
        # 保存可用节点
        with open(f"working_{output_file}", 'w', encoding='utf-8') as f:
            for config in working_configs:
                f.write(f"{config.url} # {config.latency}ms\n")
        
        # 保存全部结果（含统计）
        with open(f"full_{output_file}", 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("代理连通性测试报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总节点数: {len(configs)}\n")
            f.write(f"可用节点: {len(working_configs)}\n")
            f.write(f"失败节点: {len(failed_configs)}\n")
            f.write(f"成功率: {len(working_configs)/len(configs)*100:.1f}%\n\n")
            
            if working_configs:
                f.write("🏆 最快的前10个节点:\n")
                for i, config in enumerate(working_configs[:10], 1):
                    f.write(f"{i:2d}. {config.latency:6.1f}ms - {config.name}\n")
                    f.write(f"    {config.url}\n\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("所有可用节点:\n")
            f.write("=" * 60 + "\n")
            for config in working_configs:
                f.write(f"{config.url} # {config.latency}ms\n")
        
        print(f"✅ 结果已保存:")
        print(f"   📁 可用节点: working_{output_file}")
        print(f"   📊 完整报告: full_{output_file}")
    
    def print_statistics(self, configs: List[ProxyConfig]):
        """打印统计信息"""
        working = [c for c in configs if c.status == "success"]
        failed = [c for c in configs if c.status != "success"]
        
        print("\n" + "=" * 60)
        print("📈 测试统计报告")
        print("=" * 60)
        print(f"总节点数: {len(configs)}")
        print(f"可用节点: {len(working)}")
        print(f"失败节点: {len(failed)}")
        print(f"成功率: {len(working)/len(configs)*100:.1f}%")
        
        if working:
            # 延迟统计
            latencies = [c.latency for c in working]
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            print(f"\n⏱️ 延迟统计:")
            print(f"  平均: {avg_latency:.1f}ms")
            print(f"  最低: {min_latency:.1f}ms")
            print(f"  最高: {max_latency:.1f}ms")
            
            # 按协议统计
            protocol_stats = {}
            for config in working:
                protocol_stats[config.protocol] = protocol_stats.get(config.protocol, 0) + 1
            
            print(f"\n📡 协议分布:")
            for protocol, count in protocol_stats.items():
                percentage = count / len(working) * 100
                print(f"  {protocol.upper():>10}: {count:>3} ({percentage:.1f}%)")
            
            # 显示最快节点
            fastest = sorted(working, key=lambda x: x.latency)[:5]
            print(f"\n🏆 最快的前5个节点:")
            for i, config in enumerate(fastest, 1):
                print(f"  {i}. {config.latency:5.1f}ms - {config.name}")

async def main():
    """主函数"""
    print("🚀 高速代理连通性测试工具")
    print("=" * 50)
    
    # 配置参数
    input_file = "sub.txt"  # 你的代理列表文件
    output_file = "proxy_test_results.txt"
    max_concurrent = 30    # 并发数（可根据网络调整）
    timeout = 6            # 超时时间（秒）
    
    # 创建测试器
    tester = FastProxyTester(max_concurrent=max_concurrent, timeout=timeout)
    
    # 解析代理配置
    configs = tester.parse_proxy_links(input_file)
    if not configs:
        print("❌ 没有找到可用的代理配置")
        return
    
    # 开始测试
    start_time = time.time()
    results = await tester.batch_test(configs)
    end_time = time.time()
    
    # 显示结果
    tester.print_statistics(results)
    
    # 保存结果
    tester.save_results(results, output_file)
    
    # 显示总耗时
    total_time = end_time - start_time
    print(f"\n⏰ 总耗时: {total_time:.1f}秒")
    print(f"📊 测试速度: {len(configs)/total_time:.1f} 节点/秒")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())
