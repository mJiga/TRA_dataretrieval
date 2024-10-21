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
            df = df[['Organization', 'ID/CDC', 'Administration', 'Tested Grade', 'STAAR - Mathematics|Tests Taken', 'STAAR - Mathematics|Performance Levels|Meets and Above|Count', 'STAAR - Mathematics|Performance Levels|Masters|Count', 'STAAR - Reading|Tests Taken', 'STAAR - Reading|Performance Levels|Meets and Above|Count', 'STAAR - Reading|Performance Levels|Masters|Count']]
            print(f"Columns in {csv_file}: {', '.join(df.columns)}")

            # Append dataframes
            dfs.append(df)

    except Exception as e:
        print(f"An error ocurred: {e}")

    # Concatenate all the dataframes into a single dataframe
    combined_df = pd.concat(dfs, ignore_index=True)

    # Specify the full output path for the new CSV file
    output_file_path = os.path.join(output_dir, 'math_reading.csv')

    # Write the combined dataframe to a new CSV file
    combined_df.to_csv(output_file_path, index=False)

    print(f"Combined data has been saved to {output_file_path}")

