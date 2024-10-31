import os
import pandas as pd

def processing():
    # Specify the directory where the CSV files are downloaded
    download_dir = 'downloads'
    
    # Specify the output folder structure where the final CSV will be saved
    output_dir = os.path.join(download_dir, 'clean')
    
    # Create the directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define the desired order for Student Groups
    student_group_order = ['All Students', 'Hispanic/Latino', 'Economically Disadvantaged']
    
    # Get a list of all CSV files in the download directory
    csv_files = [f for f in os.listdir(download_dir) if f.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files in {download_dir}")
    
    # Create empty lists to store math and reading dataframes
    math_dfs = []
    reading_dfs = []
    
    try:
        for csv_file in csv_files:
            file_path = os.path.join(download_dir, csv_file)
            
            # Add error handling for reading CSV
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                # Try alternative encoding if UTF-8 fails
                df = pd.read_csv(file_path, encoding='latin1')
            
            print(f"Processing {csv_file}...")
            
            # Keep only the required columns
            try:
                df = df[['Organization', 'ID/CDC', 'Administration', 'Tested Grade', 'Student Group',
                        'STAAR - Mathematics|Tests Taken', 'STAAR - Mathematics|Performance Levels|Meets and Above|Count',
                        'STAAR - Mathematics|Performance Levels|Masters|Count', 'STAAR - Reading|Tests Taken',
                        'STAAR - Reading|Performance Levels|Meets and Above|Count', 'STAAR - Reading|Performance Levels|Masters|Count']]
            except KeyError as e:
                print(f"Warning: Missing columns in {csv_file}: {e}")
                continue
            
            # Filter for specified student groups only
            df = df[df['Student Group'].isin(student_group_order)]
            
            # Create a categorical type for Student Group with custom ordering
            df['Student Group'] = pd.Categorical(df['Student Group'], 
                                               categories=student_group_order, 
                                               ordered=True)
            
            # Create separate DataFrames for math and reading data
            math_df = df[['Organization', 'ID/CDC', 'Administration', 'Tested Grade', 'Student Group',
                         'STAAR - Mathematics|Tests Taken', 
                         'STAAR - Mathematics|Performance Levels|Meets and Above|Count',
                         'STAAR - Mathematics|Performance Levels|Masters|Count']].copy()
            
            reading_df = df[['Organization', 'ID/CDC', 'Administration', 'Tested Grade', 'Student Group',
                           'STAAR - Reading|Tests Taken', 
                           'STAAR - Reading|Performance Levels|Meets and Above|Count',
                           'STAAR - Reading|Performance Levels|Masters|Count']].copy()
            
            # Append to respective lists
            math_dfs.append(math_df)
            reading_dfs.append(reading_df)
        
        # Combine all math dataframes
        if math_dfs:
            combined_math_df = pd.concat(math_dfs, ignore_index=True)
            # Sort the combined math dataframe
            combined_math_df = combined_math_df.sort_values(
                by=['Organization', 'Student Group', 'Tested Grade'],
                ascending=[True, True, True]
            )
            
            # Write math data
            math_output_path = os.path.join(output_dir, 'combined_math.csv')
            combined_math_df.to_csv(math_output_path, index=False, encoding='utf-8')
            
            # Verify the file was written correctly
            try:
                pd.read_csv(math_output_path)
                print(f"Math data successfully saved to {math_output_path}")
            except Exception as e:
                print(f"Error verifying math file: {e}")
        
        # Combine all reading dataframes
        if reading_dfs:
            combined_reading_df = pd.concat(reading_dfs, ignore_index=True)
            # Sort the combined reading dataframe
            combined_reading_df = combined_reading_df.sort_values(
                by=['Organization', 'Student Group', 'Tested Grade'],
                ascending=[True, True, True]
            )
            
            # Write reading data
            reading_output_path = os.path.join(output_dir, 'combined_reading.csv')
            combined_reading_df.to_csv(reading_output_path, index=False, encoding='utf-8')
            
            # Verify the file was written correctly
            try:
                pd.read_csv(reading_output_path)
                print(f"Reading data successfully saved to {reading_output_path}")
            except Exception as e:
                print(f"Error verifying reading file: {e}")
    
    except Exception as e:
        print(f"An error occurred during processing: {e}")

def verify_files(directory):
    """
    Verify that all CSV files in the directory can be opened
    """
    print("\nVerifying files...")
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            try:
                df = pd.read_csv(file_path)
                print(f"✓ {filename} is valid")
            except Exception as e:
                print(f"✗ Error with {filename}: {e}")

# Example usage
if __name__ == "__main__":
    processing()
    # Verify the output files
    verify_files(os.path.join('downloads', 'clean'))