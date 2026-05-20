# 1. Pull the master list as before
library(wbstats)
wb_master_glossary <- wb_indicators(lang = "en")

# 2. Identify and flatten list-columns (like 'topics') 
# We use a loop to check each column. If it's a list, we collapse it into a string.
wb_flat_glossary <- wb_master_glossary

for (col_name in names(wb_flat_glossary)) {
  if (is.list(wb_flat_glossary[[col_name]])) {
    
    # We'll collapse the list elements into a single string separated by "; "
    # We use 'sapply' to handle each row's list entry
    wb_flat_glossary[[col_name]] <- sapply(wb_flat_glossary[[col_name]], function(x) {
      if (is.null(x) || length(x) == 0) return(NA)
      
      # If it's a dataframe (common in 'topics'), we extract the topic names
      if (is.data.frame(x)) return(paste(x$value, collapse = "; "))
      
      # Otherwise, just paste the elements together
      return(paste(as.character(x), collapse = "; "))
    })
  }
}

# 3. Now you can save it to CSV without the error!
write.csv(wb_flat_glossary, "World_Bank_Master_Glossary_All_Databases.csv", row.names = FALSE)

print("Success! The master glossary is flattened and saved.")