#!/usr/bin/env python3
"""
Proxy Validator - Test proxies for YouTube accessibility
"""

import sys
from pathlib import Path
import argparse
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.proxy_rotator import ProxyRotator

def main():
    parser = argparse.ArgumentParser(description='Validate proxies for YouTube')
    parser.add_argument('--input', '-i', default='config/proxies.txt',
                       help='Input proxy file')
    parser.add_argument('--output', '-o', default='data/proxies/working_proxies.txt',
                       help='Output file for working proxies')
    parser.add_argument('--threads', '-t', type=int, default=50,
                       help='Number of threads (default: 50)')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Timeout in seconds (default: 10)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 Proxy Validator for YouTube Human Emulator")
    print("="*60)
    
    # Create rotator
    rotator = ProxyRotator({
        'proxy_file': args.input,
        'test_url': 'https://www.youtube.com',
        'max_failures': 3,
        'timeout': args.timeout
    })
    
    # Load proxies
    proxies = rotator.load_proxies()
    print(f"📊 Loaded {len(proxies)} proxies from {args.input}")
    
    # Validate
    start_time = datetime.now()
    working = rotator.validate_all(max_workers=args.threads)
    elapsed = (datetime.now() - start_time).total_seconds()
    
    # Save working proxies
    with open(args.output, 'w') as f:
        for proxy in working:
            f.write(f"{proxy}\n")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)
    print(f"Total proxies tested: {len(proxies)}")
    print(f"Working proxies: {len(working)}")
    print(f"Success rate: {(len(working)/len(proxies)*100):.1f}%")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print(f"Working proxies saved to: {args.output}")
    print("="*60)

if __name__ == '__main__':
    main()