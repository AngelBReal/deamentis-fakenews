from pathlib import Path
import os
import requests
import shutil
import time
from typing import Dict, List, Optional, Union
import typer
import pandas as pd
import re
from datasets import load_dataset
from loguru import logger
from tqdm.auto import tqdm
from de_a_mentis.config import RAW_DATA_DIR, INTERIM_DATA_DIR

app = typer.Typer()

def ensure_dir(path: Path) -> None:
    """Asegura que el directorio existe, creándolo si es necesario."""
    path.parent.mkdir(parents=True, exist_ok=True)

def download_file(url: str, output_path: Path, timeout: int = 30, retries: int = 3, 
                 backoff_factor: float = 0.5) -> bool:
    """
    Descarga un archivo con manejo de errores, reintentos y barra de progreso.
    
    Args:
        url: URL del archivo a descargar
        output_path: Ruta donde guardar el archivo
        timeout: Tiempo máximo de espera para la conexión en segundos
        retries: Número de reintentos en caso de fallo
        backoff_factor: Factor para el tiempo de espera entre reintentos
        
    Returns:
        bool: True si la descarga fue exitosa, False en caso contrario
    """
    ensure_dir(output_path)
    
    # Si el archivo ya existe, no lo descargamos de nuevo
    if output_path.exists():
        logger.info(f"El archivo {output_path} ya existe, omitiendo descarga.")
        return True
    
    for attempt in range(retries):
        try:
            logger.info(f"Descargando {url} a {output_path}")
            
            with requests.get(url, stream=True, timeout=timeout) as response:
                response.raise_for_status()
                
                # Obtener el tamaño total del archivo si está disponible
                total_size = int(response.headers.get('content-length', 0))
                
                with open(output_path, 'wb') as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True, 
                             desc=output_path.name) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
            
            logger.success(f"Archivo descargado correctamente: {output_path}")
            return True
            
        except (requests.exceptions.RequestException, IOError) as e:
            wait_time = backoff_factor * (2 ** attempt)
            logger.warning(f"Intento {attempt + 1}/{retries} falló: {str(e)}. "
                         f"Reintentando en {wait_time:.1f} segundos...")
            
            if attempt < retries - 1:
                time.sleep(wait_time)
            else:
                logger.error(f"No se pudo descargar {url} después de {retries} intentos.")
                return False
    
    return False

def clean_text(text):
    """Limpieza básica de texto"""
    if pd.isna(text):
        return ""
    
    # Convertir a string si no lo es
    if not isinstance(text, str):
        text = str(text)
    
    # Eliminar URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

@app.command()
def download_omdena(
    output_path: Path = RAW_DATA_DIR / "omdena/fake_news_latam_omdena_combined.csv",
    cache_dir: Optional[Path] = None
):
    """
    Descarga el dataset Omdena desde Hugging Face.
    
    Args:
        output_path: Ruta donde guardar el dataset combinado
        cache_dir: Directorio para cachear los datos de Hugging Face
    """
    try:
        logger.info("Descargando dataset Omdena desde Hugging Face...")
        ensure_dir(output_path)
        
        # Configurar opciones de cache_dir si se proporciona
        dataset_kwargs = {}
        if cache_dir:
            dataset_kwargs['cache_dir'] = str(cache_dir)
        
        dataset = load_dataset("IsaacRodgz/Fake-news-latam-omdena", **dataset_kwargs)
        
        # Convertir a dataframe y concatenar
        train_df = dataset['train'].to_pandas()
        test_df = dataset['test'].to_pandas()
        
        # Añadir columna de split para identificar la procedencia
        train_df['split'] = 'train'
        test_df['split'] = 'test'
        
        # Concatenar y guardar
        df = pd.concat([train_df, test_df], ignore_index=True)
        
        # Verificar y normalizar columnas
        df.columns = df.columns.str.strip().str.lower()
        
        # Guardar el dataset
        df.to_csv(output_path, index=False)
        logger.success(f"Dataset Omdena guardado en {output_path}")
        
        # Mostrar estadísticas
        logger.info(f"Estadísticas del dataset: {len(df)} filas, {len(df.columns)} columnas")
        logger.info(f"Distribución de clases (si existe 'label'): {df.get('label', df.get('clase', pd.Series())).value_counts().to_dict()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error al descargar el dataset Omdena: {str(e)}")
        raise

@app.command()
def download_posadas(
    output_dir: Path = RAW_DATA_DIR / "FakeNewsCorpusSpanish",
    output_file: str = "fake_news_corpus_posadas_full.csv",
    keep_excel: bool = False
):
    """
    Descarga los datasets de Posadas desde GitHub.
    
    Args:
        output_dir: Directorio donde guardar los archivos
        output_file: Nombre del archivo CSV combinado final
        keep_excel: Si se deben conservar los archivos Excel originales
    """
    try:
        logger.info("Descargando datasets de Posadas desde GitHub...")
        
        # Asegurar que el directorio existe
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_file
        
        urls = {
            "train": "https://github.com/jpposadas/FakeNewsCorpusSpanish/raw/master/train.xlsx",
            "test": "https://github.com/jpposadas/FakeNewsCorpusSpanish/raw/master/test.xlsx",
            "dev": "https://github.com/jpposadas/FakeNewsCorpusSpanish/raw/master/development.xlsx"
        }
        
        dfs = []
        excel_files = []
        
        for name, url in urls.items():
            excel_path = output_dir / f"{name}.xlsx"
            excel_files.append(excel_path)
            
            # Descargar el archivo Excel
            if not download_file(url, excel_path):
                logger.warning(f"No se pudo descargar {name}, continuando con los demás...")
                continue
            
            try:
                # Leer y procesar el archivo Excel
                logger.info(f"Procesando {name}...")
                df = pd.read_excel(excel_path)
                df.columns = df.columns.str.strip().str.lower()  # Normaliza columnas
                df["split"] = name
                
                # Verificar si hay datos
                if len(df) == 0:
                    logger.warning(f"El dataset {name} está vacío")
                else:
                    dfs.append(df)
                    logger.info(f"Dataset {name} cargado: {len(df)} filas")
                
            except Exception as e:
                logger.error(f"Error al procesar {name}: {str(e)}")
        
        if not dfs:
            logger.error("No se pudo cargar ningún dataset de Posadas")
            return None
        
        # Concatenar todos los dataframes
        df_posadas = pd.concat(dfs, ignore_index=True)
        
        # Guardar el dataset combinado
        df_posadas.to_csv(output_path, index=False)
        logger.success(f"Dataset completo de Posadas guardado en {output_path}")
        
        # Mostrar estadísticas
        logger.info(f"Estadísticas del dataset: {len(df_posadas)} filas, {len(df_posadas.columns)} columnas")
        logger.info(f"Distribución por split: {df_posadas['split'].value_counts().to_dict()}")
        if 'class' in df_posadas.columns or 'clase' in df_posadas.columns:
            class_col = 'class' if 'class' in df_posadas.columns else 'clase'
            logger.info(f"Distribución de clases: {df_posadas[class_col].value_counts().to_dict()}")
        
        # Eliminar archivos Excel si no se desean conservar
        if not keep_excel:
            for excel_file in excel_files:
                if excel_file.exists():
                    excel_file.unlink()
                    logger.info(f"Archivo temporal eliminado: {excel_file}")
        
        return df_posadas
        
    except Exception as e:
        logger.error(f"Error en la descarga de datasets de Posadas: {str(e)}")
        raise

@app.command()
def process_omdena_dataset(input_path: Path = RAW_DATA_DIR/"omdena/fake_news_latam_omdena_combined.csv"):
    """
    Procesa el dataset de Omdena extrayendo solo las columnas relevantes.
    """
    logger.info(f"Procesando dataset Omdena desde {input_path}")
    
    df = pd.read_csv(input_path)
    logger.info(f"Dataset Omdena original: {len(df)} filas")
    
    # Determinar qué columnas están disponibles
    omdena_columns = {}
    
    # Para la etiqueta, preferimos corrected_label pero podemos usar prediction si no está
    if 'corrected_label' in df.columns:
        omdena_columns['corrected_label'] = 'label'
    else:
        omdena_columns['prediction'] = 'label'
    
    # Añadir las otras columnas que nos interesan
    omdena_columns.update({
        'content': 'content',
        'title': 'title',
        'source': 'source'
    })
    
    # Seleccionar solo las columnas disponibles
    available_columns = [col for col in omdena_columns.keys() if col in df.columns]
    df_clean = df[available_columns].rename(columns={col: omdena_columns[col] for col in available_columns})
    
    # Si no hay título pero hay contenido, usar las primeras palabras
    if 'title' not in df_clean.columns and 'content' in df_clean.columns:
        df_clean['title'] = df_clean['content'].apply(
            lambda x: ' '.join(str(x).split()[:8]) + '...' if pd.notna(x) else ""
        )
    
    # Asegurar que todas las columnas existan
    for col in ['content', 'title', 'source', 'label']:
        if col not in df_clean.columns:
            df_clean[col] = ""
    
    # Limpieza básica
    df_clean['content'] = df_clean['content'].apply(clean_text)
    df_clean['title'] = df_clean['title'].apply(clean_text)

    # Manejar valores nulos
    df_clean['title'] = df_clean['title'].fillna("Sin Titulo")
    df_clean['source'] = df_clean['source'].fillna("Sin Source")
    
    # Estandarizar etiquetas (todo en minúsculas)
    df_clean['label'] = df_clean['label'].str.lower()
    
    # Agregar origen del dataset
    df_clean['dataset_source'] = 'omdena'
    
    logger.success(f"Dataset Omdena procesado: {len(df_clean)} filas")
    return df_clean

@app.command()
def process_posadas_dataset(input_path: Path = RAW_DATA_DIR/"FakeNewsCorpusSpanish/fake_news_corpus_posadas_full.csv"):
    """
    Procesa el dataset de Posadas extrayendo solo las columnas relevantes.
    """
    logger.info(f"Procesando dataset Posadas desde {input_path}")
    
    df = pd.read_csv(input_path)
    logger.info(f"Dataset Posadas original: {len(df)} filas")
    
    # Extraer y renombrar solo las columnas que nos interesan
    posadas_columns = {
        'source': 'source',
        'headline': 'title',
        'text': 'content',
        'category': 'label'
    }
    
    df_clean = df[posadas_columns.keys()].rename(columns=posadas_columns)
    
    # Limpieza básica
    df_clean['content'] = df_clean['content'].apply(clean_text)
    df_clean['title'] = df_clean['title'].apply(clean_text)

    # Manejar valores nulos
    df_clean['title'] = df_clean['title'].fillna("Sin Titulo")
    df_clean['source'] = df_clean['source'].fillna("Sin Source")
    
    # Estandarizar etiquetas (todo en minúsculas)
    df_clean['label'] = df_clean['label'].str.lower()
    
    # Unificar "false" y "fake" como una sola categoría
    df_clean['label'] = df_clean['label'].replace({'false': 'fake'})
    
    # Agregar origen del dataset
    df_clean['dataset_source'] = 'posadas'
    
    logger.success(f"Dataset Posadas procesado: {len(df_clean)} filas")
    return df_clean

@app.command()
def merge_datasets(
    posadas_path: Path = RAW_DATA_DIR/"FakeNewsCorpusSpanish/fake_news_corpus_posadas_full.csv",
    omdena_path: Path = RAW_DATA_DIR/"omdena/fake_news_latam_omdena_combined.csv",
    output_path: Path = INTERIM_DATA_DIR/"combined_fakenews_dataset.csv"
):
    """
    Combina los datasets procesados en uno solo con estructura unificada.
    """
    logger.info("Combinando datasets...")
    
    # Procesar cada dataset
    posadas_df = process_posadas_dataset(posadas_path)
    omdena_df = process_omdena_dataset(omdena_path)
    
    # Aseguramos que ambos tengan las mismas columnas
    columns = ['label', 'content', 'title', 'source', 'dataset_source']
    
    # Combinar datasets
    combined_df = pd.concat([posadas_df[columns], omdena_df[columns]], ignore_index=True)
    
    # Verificar que tenemos solo las etiquetas que nos interesan
    if combined_df['label'].nunique() > 2:
        logger.warning(f"Hay más de 2 etiquetas: {combined_df['label'].unique()}")
    
    # Crear ID único
    combined_df['id'] = [f'fn_{i:06d}' for i in range(len(combined_df))]
    
    # Guardar el dataset combinado
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(output_path, index=False)
    
    # Mostrar estadísticas
    logger.info(f"Dataset combinado: {len(combined_df)} filas")
    logger.info(f"Distribución de etiquetas: {combined_df['label'].value_counts().to_dict()}")
    logger.info(f"Distribución por fuente: {combined_df['dataset_source'].value_counts().to_dict()}")
    
    logger.success(f"Dataset combinado guardado en {output_path}")
    return combined_df

@app.command()
def download_all(output_dir: Path = RAW_DATA_DIR):
    """Descarga todos los datasets disponibles."""
    try:
        logger.info("Iniciando descarga de todos los datasets...")
        
        # Descargar Omdena
        omdena_df = download_omdena(output_path=output_dir/"omdena/fake_news_latam_omdena_combined.csv")
        logger.info(f"Dataset Omdena: {len(omdena_df) if omdena_df is not None else 0} filas")
        
        # Descargar Posadas
        posadas_df = download_posadas(output_dir=output_dir/"FakeNewsCorpusSpanish")
        logger.info(f"Dataset Posadas: {len(posadas_df) if posadas_df is not None else 0} filas")
        
        logger.success("Todos los datasets han sido descargados correctamente")
        
    except Exception as e:
        logger.error(f"Error al descargar todos los datasets: {str(e)}")
        raise

@app.command()
def process_all():
    """Procesa y combina todos los datasets disponibles."""
    try:
        logger.info("Iniciando procesamiento y combinación de datasets...")
        
        # Asegurar que existen los directorios
        INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Combinar datasets
        combined_df = merge_datasets()
        
        logger.success(f"Procesamiento completado. Dataset final: {len(combined_df)} filas")
        
    except Exception as e:
        logger.error(f"Error en el procesamiento: {str(e)}")
        raise

if __name__ == "__main__":
    app()