# dataset.py
from pathlib import Path
from loguru import logger
import typer
import pandas as pd
from datasets import load_dataset
from de_a_mentis.config import RAW_DATA_DIR

app = typer.Typer()

@app.command()
def download_omdena(output_path: Path = RAW_DATA_DIR / "omdena/fake_news_latam_omdena_combined.csv"):
    logger.info("Downloading Omdena dataset from Hugging Face...")
    dataset = load_dataset("IsaacRodgz/Fake-news-latam-omdena")
    df = pd.concat([
        dataset['train'].to_pandas(),
        dataset['test'].to_pandas()
    ])
    df.to_csv(output_path, index=False)
    logger.success(f"Saved combined Omdena dataset to {output_path}")

@app.command()
def download_posadas():
    logger.info("Downloading Posadas datasets from GitHub...")

    urls = {
        "train": "https://github.com/jpposadas/FakeNewsCorpusSpanish/raw/master/train.xlsx",
        "test": "https://github.com/jpposadas/FakeNewsCorpusSpanish/raw/master/test.xlsx",
        "dev": "https://github.com/jpposadas/FakeNewsCorpusSpanish/raw/master/development.xlsx"
    }

    dfs = []
    for name, url in urls.items():
        logger.info(f"Downloading {name} set...")
        df = pd.read_excel(url)
        df.columns = df.columns.str.strip().str.lower()  # ← Normaliza columnas
        df["split"] = name
        dfs.append(df)

    df_posadas = pd.concat(dfs, ignore_index=True)
    output_path = RAW_DATA_DIR / "FakeNewsCorpusSpanish/fake_news_corpus_posadas_full.csv"
    df_posadas.to_csv(output_path, index=False)
    logger.success(f"Saved full Posadas dataset to {output_path}")

if __name__ == "__main__":
    app()
