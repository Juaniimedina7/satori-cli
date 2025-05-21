import random
import os
from argparse import ArgumentParser
from typing import Optional, List
from pathlib import Path
import ipaddress


from satoricli.cli.commands.base import BaseCommand
from satoricli.cli.utils import console, error_console


class ShardsCommand(BaseCommand):
    
    name = "shards"
    
    def register_args(self, parser: ArgumentParser):
        parser.add_argument("--shard", required=True, help="Current shard and total (X/Y format)")
        parser.add_argument("--seed", type=int, required=True, help="Seed for pseudorandom permutation")
        parser.add_argument("--input", dest="input_file", required=True, help="Input file with addresses (any path)")
        parser.add_argument("--blacklist", dest="exclude_file", help="File with addresses to exclude (any path)")
        parser.add_argument("--results", dest="results_file", help="Save results to text file (must have .txt extension or no extension; default is .txt)")
    
    def read_file_addresses(self, file_path: str) -> List[str]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        addresses = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    entry = line.strip()
                    if not entry:
                        continue
                    try:
                        if '/' in entry:
                            # Es un rango CIDR: expandir todas las IPs
                            net = ipaddress.IPv4Network(entry, strict=False)
                            addresses.extend([str(ip) for ip in net])
                        else:
                            # Es una IP suelta
                            addresses.append(entry)
                    except ValueError:
                        error_console.print(f"[warning]Skipping invalid address or range: {entry}")
        except Exception as e:
            raise ValueError(f"Error reading {file_path}: {str(e)}")
        
        return addresses
            
    def __call__(self, **kwargs):
        shard = kwargs["shard"]
        seed = kwargs["seed"]
        input_file = kwargs["input_file"]
        exclude_file = kwargs.get("exclude_file")
        results_file = kwargs.get("results_file")

        try:
            x_str, y_str = shard.split("/")
            X = int(x_str)
            Y = int(y_str)
        except ValueError:
            error_console.print("[error]ERROR:[/] Invalid format for --shard. Use X/Y")
            return 1
        
        if Y < 1 or X < 1 or X > Y:
            error_console.print(f"[error]ERROR:[/] Invalid shard value: {X}/{Y}")
            return 1
        
        try:
            addresses = self.read_file_addresses(input_file)
            if not addresses:
                error_console.print(f"[error]ERROR:[/] No valid addresses found in: {input_file}")
                return 1
        except FileNotFoundError:
            error_console.print(f"[error]ERROR:[/] Input file not found: {input_file}")
            return 1
        except ValueError as e:
            error_console.print(f"[error]ERROR:[/] {str(e)}")
            return 1
        
        # Apply exclude list if provided
        exclude_set = set()
        if exclude_file:
            try:
                exclude_addresses = self.read_file_addresses(exclude_file)
                for addr in exclude_addresses:
                    exclude_set.add(addr)
                    if ":" not in addr:
                        exclude_set.add(addr + ":")
            except FileNotFoundError:
                error_console.print(f"[error]ERROR:[/] Exclude file not found: {exclude_file}")
                return 1
            except ValueError as e:
                error_console.print(f"[error]ERROR:[/] Error in exclude file: {str(e)}")
                return 1
        
        filtered_addresses = []
        for addr in addresses:
            if addr in exclude_set:
                continue
            ip_part = addr.split(":")[0] if ":" in addr else addr
            if ip_part + ":" in exclude_set:
                continue
            filtered_addresses.append(addr)
        
        rnd = random.Random(seed)
        rnd.shuffle(filtered_addresses)
        
        shard_addresses = [addr for index, addr in enumerate(filtered_addresses) if index % Y == (X-1)]
        
        if results_file:
            try:
                output_path = Path(results_file)
                extension = output_path.suffix.lower()
                if not extension:
                    output_path = Path(str(output_path) + '.txt')
                    console.print(f"No extension provided, using: {output_path}")
                elif extension != '.txt':
                    error_console.print(f"[error]ERROR:[/] Unsupported file extension: {extension}. Only .txt format is supported.")
                    return 1
                
                os.makedirs(output_path.parent, exist_ok=True)
                with open(output_path, 'w') as f:
                    for addr in shard_addresses:
                        f.write(f"{addr}\n")
                console.print(f"Results saved to {output_path}")
            except Exception as e:
                error_console.print(f"[error]ERROR:[/] Failed to write to output file: {str(e)}")
                return 1
        else:
            for addr in shard_addresses:
                console.print(addr)
            
        return 0
