# Load necessary libraries
library(pdftools)
library(stringr)

# Define the path to your Terms.txt file and PDFs folder
terms_file <- "folder/Terms.txt"
pdf_folder <- "framewoks/Frameworks"

# Function to load themes and synonyms from the Terms.txt file
load_terms <- function(file_path) {
  source(file_path, local = TRUE)
  if (!exists("themes") || !exists("synonyms")) {
    stop("Error: 'themes' or 'synonyms' not found in the Terms.txt file.")
  }
  list(themes = themes, synonyms = synonyms)
}

# Load the themes and synonyms
terms <- load_terms(terms_file)
themes <- terms$themes
synonyms <- terms$synonyms

# Function to extract proximity of terms ensuring full-term match
extract_terms_within_proximity <- function(text, theme_terms, all_synonyms, proximity = 5) {
  results <- list()
  
  # Tokenize the text and clean it
  tokens <- unlist(strsplit(text, "\\s+"))
  
  for (theme_term in theme_terms) {
    # Find positions of theme terms ensuring full-term match
    theme_positions <- which(tokens == theme_term)
    
    for (theme_name in names(all_synonyms)) {
      for (synonym in all_synonyms[[theme_name]]) {
        # Find positions of synonyms ensuring full-term match
        synonym_positions <- which(tokens == synonym)
        
        for (theme_pos in theme_positions) {
          # Check for proximity of the synonyms to the theme terms
          close_terms <- synonym_positions[abs(synonym_positions - theme_pos) <= proximity]
          
          if (length(close_terms) > 0) {
            # Log the result with theme, synonym, and context
            results[[length(results) + 1]] <- list(
              theme_term = theme_term,
              synonym = synonym,
              theme_name = theme_name,
              context = paste(tokens[max(1, theme_pos - proximity):min(length(tokens), theme_pos + proximity)], collapse = " ")
            )
          }
        }
      }
    }
  }
  return(results)
}

# Function to process each PDF and extract relevant terms for all themes
process_pdfs_for_themes <- function(pdf_folder, all_synonyms) {
  pdf_files <- list.files(pdf_folder, pattern = "*.pdf", full.names = TRUE)
  if (length(pdf_files) == 0) {
    stop("Error: No PDF files found in the specified folder.")
  }
  
  all_results <- list()
  
  for (pdf_file in pdf_files) {
    # Extract text from the PDF
    text <- pdf_text(pdf_file)
    
    # For each page of the PDF, extract terms within proximity for all themes
    for (page_text in text) {
      results <- extract_terms_within_proximity(page_text, unlist(synonyms), all_synonyms)
      
      # Add "Framework" (PDF file name) column to results
      if (length(results) > 0) {
        results <- lapply(results, function(res) {
          res$Framework <- basename(pdf_file)  # Add the PDF name as the Framework
          return(res)
        })
      }
      
      all_results <- c(all_results, results)
    }
  }
  return(all_results)
}

# Run the process
results <- process_pdfs_for_themes(pdf_folder, synonyms)

# Display results
if (length(results) > 0) {
  results_df <- do.call(rbind, lapply(results, as.data.frame))
  write.csv(results_df, file = "all_themes_proximity_results.csv", row.names = FALSE)
  print(head(results_df))  # Show a preview of the results
} else {
  message("No matches found in the PDFs.")
}


#-----------------MERGE----
#install.packages("readxl")
library(readxl)

# Define the path to the Excel file
file_path <- "C:/Users/PMPONELA/OneDrive - CGIAR/CIMMYT/SOIL HEALTH WRITESHOP MALAWI 17-20 September/Reading Materials/50integrate/List of frameworks.xlsx"

# Read the specific sheet "AE Indicators"
ae_indicators_data <- read_excel(file_path, sheet = "AE Indicators")

# View the first few rows of the data
head(ae_indicators_data)

# Optionally, print the structure of the data
str(ae_indicators_data)

# Define the folder path
base_folder <- "C:/Users/PMPONELA/OneDrive - CGIAR/CIMMYT/SOIL HEALTH WRITESHOP MALAWI 17-20 September/Reading Materials/50integrate"

# Define the subfolder path
subfolder_path <- file.path(base_folder, "results")

# Define the CSV file name
csv_file_path <- file.path(subfolder_path, "all_themes_proximity_results.csv")

# Read the CSV file
proximity_results <- read.csv(csv_file_path)

# View the first few rows of the data
head(proximity_results)

# Optionally, print the structure of the data
str(proximity_results)

# Assuming ae_indicators_data and proximity_results are already loaded in R

# Merge the datasets based on the "indicator" column
merged_data <- merge(ae_indicators_data, proximity_results, by = "indicator", all = TRUE)

# View the first few rows of the merged data
head(merged_data)

# Optionally, check the structure of the merged data
str(merged_data)

# Define the output file path
output_file_path <- file.path(base_folder, "results", "merged_ae_indicators_proximity_results.csv")

# Save the merged data as a CSV file
write.csv(merged_data, output_file_path, row.names = FALSE)

# Print a confirmation message
cat("Merged data saved as:", output_file_path)

