#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - EXNESS DATA DOWNLOADER 💎🌟⚡

Downloads tick data from Exness and converts to Parquet
"Capturing light from the markets..."
"""

import sys
import argparse
import zipfile
import urllib.request
import socket
import shutil
from pathlib import Path

import pandas as pd

# Configuration
BASE_URL = "https://ticks.ex2archive.com/ticks/{pair}_Zero_Spread/{year}/Exness_{pair}_Zero_Spread_{year}.zip"
ALL_PAIRS = [
    # Majors (7)
    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD',
    
    # Crosses (10)
    'EURJPY', 'EURGBP', 'GBPJPY', 'AUDJPY', 'NZDJPY', 'CADJPY', 'CHFJPY',
    'EURAUD', 'GBPAUD', 'EURCHF',
    
    # Precious Metals (4)
    'XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD',
    
    # Industrial Metals (3)
    'XCUUSD', 'XALUSD', 'XNIUSD',
    
    # Exotics (5)
    'USDMXN', 'USDZAR', 'USDTRY', 'EURNOK', 'USDSEK',
    
    # Index (1)
    'DXY',
]
ALL_YEARS = [2025]
OUTPUT_DIR = Path("data/parquet")
TEMP_DIR = Path("data/temp")


def format_size(bytes_size):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.0f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.0f} TB"


def process_file(pair, year, current, total, force=False):
    """
    Process a single pair/year file: download, extract, validate, convert, cleanup
    
    Args:
        pair: Currency pair (e.g., 'EURUSD')
        year: Year (e.g., 2023)
        current: Current file number
        total: Total number of files
        force: Force redownload even if parquet exists
    """
    # File paths
    output_parquet = OUTPUT_DIR / f"{pair}_{year}.parquet"
    zip_file = TEMP_DIR / f"{pair}_{year}.zip"
    csv_file = TEMP_DIR / f"Exness_{pair}_Zero_Spread_{year}.csv"
    
    # Check if already processed
    if output_parquet.exists() and not force:
        print(f"⏭️  [{current}/{total}] {pair}_{year} já existe, pulando...")
        return
    
    # Build URL
    url = BASE_URL.format(pair=pair, year=year)
    
    try:
        # 1. DOWNLOAD
        print(f"\n📥 [{current}/{total}] Baixando {pair}_{year}...")
        
        def download_progress(block_num, block_size, total_size):
            """Show download progress"""
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                size_str = format_size(downloaded)
                total_str = format_size(total_size)
                print(f"\r   Progresso: {percent:.1f}% ({size_str}/{total_str})", end='', flush=True)
        
        # Set timeout for download
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(300)  # 5 minutes timeout
        try:
            urllib.request.urlretrieve(url, zip_file, reporthook=download_progress)
        finally:
            socket.setdefaulttimeout(old_timeout)
        
        file_size = zip_file.stat().st_size
        print(f"\n   ✓ Download: {format_size(file_size)}")
        
        # 2. EXTRACT
        print(f"📦 Extraindo...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # Find the CSV file in the ZIP
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            if not csv_files:
                raise ValueError(f"Nenhum arquivo CSV encontrado no ZIP")
            
            # Extract the first CSV file
            zip_ref.extract(csv_files[0], TEMP_DIR)
            extracted_csv = TEMP_DIR / csv_files[0]
            
            # Rename if necessary
            if extracted_csv != csv_file:
                extracted_csv.rename(csv_file)
        
        print(f"   ✓ CSV: {csv_file.name}")
        
        # 3. VALIDATE AND READ
        print(f"📊 Validando...")
        
        # Read CSV with proper column names
        # Format: Exness,EURUSD,2023-01-02 00:00:00.123,1.06721,1.06723
        df = pd.read_csv(
            csv_file,
            skiprows=1,  # Skip header
            names=['broker', 'symbol', 'timestamp', 'bid', 'ask'],
            parse_dates=['timestamp']
        )
        
        # Validate data structure
        if len(df.columns) != 5:
            raise ValueError(f"CSV deve ter 5 colunas, encontrado {len(df.columns)}")
        
        if df.empty:
            raise ValueError("CSV está vazio")
        
        # Validate data
        num_ticks = len(df)
        print(f"   ✓ Ticks: {num_ticks:,}")
        
        # Period
        period_start = df['timestamp'].min()
        period_end = df['timestamp'].max()
        print(f"   ✓ Período: {period_start.strftime('%Y-%m-%d')} → {period_end.strftime('%Y-%m-%d')}")
        
        # Bid/Ask range
        bid_min = df['bid'].min()
        bid_max = df['bid'].max()
        ask_min = df['ask'].min()
        ask_max = df['ask'].max()
        print(f"   ✓ Bid: {bid_min:.5f} - {bid_max:.5f}")
        print(f"   ✓ Ask: {ask_min:.5f} - {ask_max:.5f}")
        
        # File size
        csv_size = csv_file.stat().st_size
        print(f"   ✓ Tamanho CSV: {format_size(csv_size)}")
        
        # 4. CONVERT TO PARQUET
        print(f"💎 Convertendo para Parquet...")
        df.to_parquet(
            output_parquet,
            engine='pyarrow',
            compression='snappy',
            index=False
        )
        
        parquet_size = output_parquet.stat().st_size
        print(f"   ✓ Salvo: {output_parquet} ({format_size(parquet_size)})")
        
        # 5. CLEANUP
        print(f"🧹 Limpando temporários...")
        if zip_file.exists():
            zip_file.unlink()
            print(f"   ✓ Deletado: {zip_file.name}")
        if csv_file.exists():
            csv_file.unlink()
            print(f"   ✓ Deletado: {csv_file.name}")
        
        # 6. DONE
        print(f"✅ {pair}_{year} concluído!")
        
    except urllib.error.HTTPError as e:
        print(f"\n❌ Erro HTTP {e.code}: {url}")
        print(f"   O arquivo pode não estar disponível para {pair} {year}")
    except urllib.error.URLError as e:
        print(f"\n❌ Erro de conexão: {e.reason}")
        print(f"   Verifique sua conexão com a internet")
    except zipfile.BadZipFile:
        print(f"\n❌ Arquivo ZIP corrompido para {pair}_{year}")
        if zip_file.exists():
            zip_file.unlink()
    except Exception as e:
        print(f"\n❌ Erro ao processar {pair}_{year}: {e}")
        # Cleanup on error
        for temp_file in [zip_file, csv_file]:
            if temp_file.exists():
                temp_file.unlink()


def consolidate_pair(pair, years):
    """
    Consolidate multiple years into a single 3Y parquet file
    
    Args:
        pair: Currency pair (e.g., 'EURUSD')
        years: List of years to consolidate
    """
    print(f"\n🔗 Consolidando {pair} ({len(years)} anos)...")
    
    # Find existing parquet files
    parquet_files = []
    for year in years:
        parquet_file = OUTPUT_DIR / f"{pair}_{year}.parquet"
        if parquet_file.exists():
            parquet_files.append(parquet_file)
    
    if not parquet_files:
        print(f"   ⚠️  Nenhum arquivo parquet encontrado para {pair}")
        return
    
    if len(parquet_files) < len(years):
        print(f"   ⚠️  Apenas {len(parquet_files)}/{len(years)} anos disponíveis")
    
    try:
        # Read and concatenate all years
        dfs = []
        total_ticks = 0
        
        for pf in parquet_files:
            df = pd.read_parquet(pf)
            dfs.append(df)
            total_ticks += len(df)
            print(f"   ✓ Carregado: {pf.name} ({len(df):,} ticks)")
        
        # Concatenate
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Sort by timestamp
        combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
        
        # Save consolidated file
        output_file = OUTPUT_DIR / f"{pair}_3Y.parquet"
        combined_df.to_parquet(
            output_file,
            engine='pyarrow',
            compression='snappy',
            index=False
        )
        
        output_size = output_file.stat().st_size
        print(f"   💎 Consolidado: {output_file.name}")
        print(f"   ✓ Total ticks: {total_ticks:,}")
        print(f"   ✓ Tamanho: {format_size(output_size)}")
        print(f"   ✓ Período: {combined_df['timestamp'].min().strftime('%Y-%m-%d')} → {combined_df['timestamp'].max().strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"   ❌ Erro ao consolidar {pair}: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Download Exness tick data",
        epilog="""
Exemplos:
  python download_exness_data.py                    # Baixar tudo
  python download_exness_data.py --pairs EURUSD    # Apenas um par
  python download_exness_data.py --years 2024,2025  # Anos específicos
  python download_exness_data.py --force            # Forçar redownload
  python download_exness_data.py --consolidate      # Consolidar anos
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--pairs", type=str, help="Comma-separated pairs (e.g., EURUSD,GBPJPY)")
    parser.add_argument("--years", type=str, help="Comma-separated years (e.g., 2024,2025)")
    parser.add_argument("--force", action="store_true", help="Force redownload")
    parser.add_argument("--consolidate", action="store_true", help="Consolidate years into 3Y file")
    args = parser.parse_args()
    
    # Parse pairs and years
    pairs = args.pairs.split(",") if args.pairs else ALL_PAIRS
    
    # Parse years with error handling
    if args.years:
        try:
            years = [int(y.strip()) for y in args.years.split(",")]
        except ValueError as e:
            print(f"❌ Erro: Anos inválidos '{args.years}'. Use números separados por vírgula (ex: 2023,2024)")
            sys.exit(1)
    else:
        years = ALL_YEARS
    
    # Validate pairs
    for pair in pairs:
        if pair not in ALL_PAIRS:
            print(f"⚠️  Aviso: {pair} não está na lista de pares padrão")
    
    # Create directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Display header
    print("⚡🌟💎 ULTRA NECROZMA - EXNESS DATA DOWNLOADER 💎🌟⚡")
    print(f"\nPares: {', '.join(pairs)}")
    print(f"Anos: {', '.join(map(str, years))}")
    print(f"Modo: {'FORCE' if args.force else 'RESUME'}")
    print(f"Consolidar: {'SIM' if args.consolidate else 'NÃO'}")
    
    # Process each pair/year
    total = len(pairs) * len(years)
    current = 0
    
    for pair in pairs:
        for year in years:
            current += 1
            process_file(pair, year, current, total, args.force)
        
        if args.consolidate:
            consolidate_pair(pair, years)
    
    # Cleanup temp directory
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    
    print(f"\n✅ Download completo!")
    print(f"📁 Arquivos salvos em: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    main()
