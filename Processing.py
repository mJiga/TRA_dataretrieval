import os
import pandas as pd

def processing():
    # Specify the directory where the CSV files are downloaded
    download_dir = 'downloads'
    
    # Specify the output folder structure where the final CSV will be saved
    output_dir = os.path.join(download_dir, 'clean')
    
    # Create the directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get a list of all CSV files in the download directory
    csv_files = [f for f in os.listdir(download_dir) if f.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files in {download_dir}")
    
    # Create an empty list to store the dataframes
    dfs = []
    
    # Loop through each CSV file, read it into a dataframe, and append it to the list
    try:
        for csv_file in csv_files:
            file_path = os.path.join(download_dir, csv_file)
            df = pd.read_csv(file_path)
            
            # Keep only the required columns
            df = df[['Organization', 'ID/CDC', 'Administration', 'Tested Grade', 
                    'STAAR - Mathematics|Tests Taken', 'STAAR - Mathematics|Performance Levels|Meets and Above|Count',
                    'STAAR - Mathematics|Performance Levels|Masters|Count', 'STAAR - Reading|Tests Taken',
                    'STAAR - Reading|Performance Levels|Meets and Above|Count', 'STAAR - Reading|Performance Levels|Masters|Count']]
            print(f"Columns in {csv_file}: {', '.join(df.columns)}")
            
            # Append dataframes
            dfs.append(df)
            
            # Generate output filenames based on input filename
            base_name = os.path.splitext(csv_file)[0]  # Remove .csv extension
            math_output_path = os.path.join(output_dir, f'{base_name}_math.csv')
            reading_output_path = os.path.join(output_dir, f'{base_name}_reading.csv')
            
            # Create two separate DataFrames for math and reading data
            math_df = df[['Organization', 'ID/CDC', 'Administration', 'Tested Grade',
                         'STAAR - Mathematics|Tests Taken', 
                         'STAAR - Mathematics|Performance Levels|Meets and Above|Count',
                         'STAAR - Mathematics|Performance Levels|Masters|Count']]
            
            reading_df = df[['Organization', 'ID/CDC', 'Administration', 'Tested Grade',
                           'STAAR - Reading|Tests Taken', 
                           'STAAR - Reading|Performance Levels|Meets and Above|Count',
                           'STAAR - Reading|Performance Levels|Masters|Count']]
            
            # Sort the dataframes by the 'Tested Grade' column
            math_df = math_df.sort_values(by='Tested Grade', ascending=True)
            reading_df = reading_df.sort_values(by='Tested Grade', ascending=True)
            
            # Write the math dataframe to a new CSV file
            math_df.to_csv(math_output_path, index=False)
            print(f"Math data has been saved to {math_output_path}")
            
            # Write the reading dataframe to a new CSV file
            reading_df.to_csv(reading_output_path, index=False)
            print(f"Reading data has been saved to {reading_output_path}")
            
    except Exception as e:
        print(f"An error occurred: {e}")