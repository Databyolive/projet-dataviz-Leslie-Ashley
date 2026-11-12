"""Outils du projet pour travailler avec le data lake RustFS (S3) depuis Spark.

Utilisés par tous les notebooks : ils créent la session Spark (Delta + accès S3)
et le bucket. Les adresses et les clés viennent des variables d'environnement du compose.
"""
import glob
import os
import re
import subprocess
import sys

import pyspark
from pyspark.sql import SparkSession

RACINE = "/home/jovyan/work"        # le dépôt, monté dans le conteneur Jupyter
RAW = f"{RACINE}/data/raw"          # données téléchargées par scripts/download_dvf.py
BUCKET = "dvf"
LAKE = f"s3a://{BUCKET}"            # racine du data lake (protocole S3A de Hadoop)

# Paquet Delta compatible avec chaque version de Spark.
DELTA_PAR_SPARK = {
    "4.2": "io.delta:delta-spark_4.2_2.13:4.4.0",
    "4.1": "io.delta:delta-spark_4.1_2.13:4.1.0",
    "4.0": "io.delta:delta-spark_2.13:4.0.0",
}


def _version_hadoop() -> str:
    """Version de Hadoop embarquée dans Spark, lue dans le nom des jars."""
    jars = glob.glob(f"{os.environ.get('SPARK_HOME', '/usr/local/spark')}/jars/hadoop-client-api-*.jar")
    if not jars:
        raise RuntimeError("Jars Hadoop introuvables : impossible de choisir le connecteur S3.")
    return re.search(r"hadoop-client-api-(.+)\.jar", jars[0]).group(1)


def creer_session(nom: str, memoire: str = "4g",paquets_supplementaires=()) -> SparkSession:
    """Crée une session Spark capable d'écrire en Delta et de lire/écrire dans RustFS."""
    spark_version = pyspark.__version__
    cle = ".".join(spark_version.split(".")[:2])
    if cle not in DELTA_PAR_SPARK:
        raise RuntimeError(f"Spark {spark_version} : ajouter son paquet Delta dans DELTA_PAR_SPARK.")
    hadoop = _version_hadoop()
    paquets = ",".join([DELTA_PAR_SPARK[cle], f"org.apache.hadoop:hadoop-aws:{hadoop}", *paquets_supplementaires])
    
    print(f"Spark {spark_version} (Hadoop {hadoop}) + Delta Lake + data lake S3. "
          "Le premier démarrage télécharge des jars : plusieurs minutes.")
    spark = (
        SparkSession.builder.appName(nom)
        .config("spark.jars.packages", paquets)
        # Delta
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        # accès à RustFS 
        .config("spark.hadoop.fs.s3a.endpoint", os.environ["S3_ENDPOINT"])
        .config("spark.hadoop.fs.s3a.access.key", os.environ["S3_ACCESS_KEY"])
        .config("spark.hadoop.fs.s3a.secret.key", os.environ["S3_SECRET_KEY"])
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.endpoint.region", "us-east-1")
        .config("spark.driver.memory", memoire)
        .getOrCreate()
    )
    print("Session prête.")
    return spark


def creer_bucket(nom: str = BUCKET) -> None:
    """Crée le bucket s'il n'existe pas (Spark ne sait pas le faire : on passe par l'API S3)."""
    try:
        import boto3
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "boto3"])
        import boto3

    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ["S3_ENDPOINT"],
        aws_access_key_id=os.environ["S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["S3_SECRET_KEY"],
        region_name="us-east-1",
    )
    if nom in [b["Name"] for b in s3.list_buckets()["Buckets"]]:
        print(f"Bucket « {nom} » déjà présent.")
    else:
        s3.create_bucket(Bucket=nom)
        print(f"Bucket « {nom} » créé.")
