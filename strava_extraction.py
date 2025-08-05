import pandas as pd
from fitparse import FitFile

# --- 1. Definizione del percorso e estrazione dati ---

# Specifica il percorso corretto del file
file_path = "Strava/Brugai_Monte_Parè.fit" 

# Lista per contenere i dati estratti
data = []

# Apre il file .fit
fitfile = FitFile(file_path)

# Itera sui messaggi 'record'
for record in fitfile.get_messages('record'):
    record_data = {}
    for field in record:
        if field.name in ['position_lat', 'position_long']:
            record_data[field.name] = field.value * (180.0 / 2**31) if field.value is not None else None
        else:
            record_data[field.name] = field.value
            
    data.append(record_data)

# --- 2. Creazione e pulizia del DataFrame iniziale ---

# Crea un DataFrame Pandas con i dati estratti
df = pd.DataFrame(data)

# Se non ci sono dati, esce per evitare errori
if df.empty:
    print("Nessun dato di tipo 'record' trovato nel file FIT.")
else:
    # Converte la colonna 'timestamp' in un formato data/ora leggibile
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Ordina i dati in base al timestamp
    df = df.sort_values(by='timestamp').reset_index(drop=True)

    # --- 3. RICAMPIONAMENTO (RESAMPLING) PER MINUTO ---

    # Seleziona solo le colonne numeriche e il timestamp che ci interessano
    columns_to_process = [
        'timestamp', 
        'position_lat', 
        'position_long', 
        'enhanced_altitude',
        'heart_rate',
        'cadence'
    ]
    # Filtra il DataFrame, mantenendo solo le colonne che esistono effettivamente
    existing_columns = [col for col in columns_to_process if col in df.columns]
    df_filtered = df[existing_columns]

    # Imposta il 'timestamp' come indice del DataFrame. È un passo necessario per il resampling.
    df_filtered.set_index('timestamp', inplace=True)

    # Ricampiona i dati su base di 1 minuto ('1T'). 
    # Per ogni minuto, calcola la MEDIA di tutti i valori (altitudine, FC, etc.).
    df_resampled = df_filtered.resample('1T').mean()

    # Rimuove le righe che potrebbero essere state create per minuti senza dati
    df_resampled.dropna(how='all', inplace=True)
    
    # Riporta il timestamp da indice a colonna normale
    df_resampled.reset_index(inplace=True)

    # --- 4. Salvataggio del DataFrame finale ---

    # Rinomina le colonne per una maggiore chiarezza nel file finale
    df_final = df_resampled.rename(columns={
        'position_lat': 'latitude',
        'position_long': 'longitude',
        'enhanced_altitude': 'altitude_m'
    })

    # Salva il DataFrame con i dati aggregati per minuto in un file CSV
    output_filename = "activity_data_per_minute.csv"
    df_final.to_csv(output_filename, index=False, sep=',')

    print(f"Dati aggregati per minuto e salvati con successo nel file: '{output_filename}'")
    print("\nAnteprima delle prime 5 righe del file CSV (una riga per minuto):")
    print(df_final.head())