library(tidyverse)
library(xml2)

run_trial_identifier_search <- function(folder, save_file) {
    
    if ( ! file.exists(save_file) ) {
        
        # The following will print out a CSV with one row per
        # clinical trial identifier found.
        
        # The first column of the output CSV contains the DOI
        # of the paper in which the identifier was found.
        
        # The second column indicates the type of identifier
        # e.g. NCT or ISRCTN. (More may be added)
        
        # The third column contains the identifier that was
        # found
        
        # The fourth column indicates whether the NCT number
        # corresponds to a legitimate record on
        # clinicaltrials.gov. 1 means yes, 0 means no, and
        # NA means that it is not an NCT number.
        
        # NOTE: The script checks whether an NCT number is
        # legit by connecting to the ClinicalTrials.gov API
        # so you will need an internet connexion for this to
        # work.
        
        # If you want to add new identifiers to be searched
        # Add them to this list
        identifiers <- list(
            c("NCT", "NCT[0-9 -]+[0-9]"),
            c("ISRCTN", "ISRCTN[0-9 -]+[0-9]")
        )
        # End of list of identifiers to search for
        
        print("Identifying trials ...")
        
        text_list <- paste0(folder, list.files(folder))
        
        new_row <- data.frame("doi", "type", "identifier")
        write_csv(new_row, save_file, append=TRUE)
        
        for ( identifier in identifiers ) {
            
            print(paste("Searching for", identifier[1], "identifiers"))
            
            for(filename in text_list) {

                file_doi <- str_replace(
                    str_replace(
                        strsplit(filename, "/")[[1]][length(strsplit(filename, "/")[[1]])],
                        ".txt", ""
                    ),
                    "\\+", "\\/"
                )
                
                text <- readChar(filename, file.info(filename)$size)
                
                idmatches <- regmatches(text, gregexpr(identifier[2], text))
                
                if (length(idmatches[[1]]) > 0) {
                    
                    # Remove the spaces and hyphens from matches
                    
                    cleaned_matches <- c()
                    
                    print(file_doi)
                    
                    for (idmatch in idmatches[[1]]) {
                        
                        idmatch <- str_remove_all(idmatch, " ")
                        idmatch <- str_remove_all(idmatch, "-")
                        
                        cleaned_matches <- c(cleaned_matches, idmatch)
                        
                    }
                    
                    cleaned_matches <- unique(cleaned_matches)
                    
                    for (idmatch in cleaned_matches) {
                        new_row <- data.frame(file_doi, identifier[1], idmatch)
                        write_csv(new_row, save_file, append=TRUE)
                    }
                    
                }
                
            }
            
        }
        
        # At this point, all the Identifiers have been written to a CSV.
        # Now, we check the NCT's for whether they're on CT dot gov.
        
        # The batch size must be 100 or fewer.
        batch_size <- 100
        
        found_ncts <- read_csv(save_file) %>%
            filter(type == "NCT")
        found_ncts$doi <- NULL
        found_ncts$type <- NULL
        found_ncts$`clinicaltrials.gov` <- ""
        
        while ( nrow(filter(found_ncts, `clinicaltrials.gov` == "")) > 0 ) {
            
            ncts_to_check <- found_ncts %>%
                filter(`clinicaltrials.gov` == "") %>%
                select(identifier) %>%
                head(n=batch_size)
            
            temp <- tempfile()
            
            download.file(
                paste0(
                    "https://clinicaltrials.gov/api/query/full_studies?min_rnk=1&max_rnk=",
                    batch_size,
                    "&expr=",
                    URLencode(
                        paste(ncts_to_check$identifier, collapse = " OR ")
                    )
                ),
                temp
            )
            
            xml <- read_xml(temp)
            
            unlink(temp)
            
            dl_trials <- xml_find_all(xml, "/FullStudiesResponse/FullStudyList/FullStudy")
    
            # Extract some trial data from the downloaded record
            
            for (dl_trial in dl_trials) {
                
                dl_trial_nct <- xml_text(xml_find_all(dl_trial, "Struct[contains(@Name, 'Study')]/Struct[contains(@Name, 'ProtocolSection')]/Struct[contains(@Name, 'IdentificationModule')]/Field[contains(@Name, 'NCTId')]"))
                
                dl_trial_title <- xml_text(xml_find_all(dl_trial, "Struct[contains(@Name, 'Study')]/Struct[contains(@Name, 'ProtocolSection')]/Struct[contains(@Name, 'IdentificationModule')]/Field[contains(@Name, 'BriefTitle')]"))
                
                found_ncts[found_ncts$identifier == dl_trial_nct, "title"] <- dl_trial_title
                
                if (length(xml_find_all(dl_trial, "Struct[contains(@Name, 'Study')]/Struct[contains(@Name, 'ProtocolSection')]/Struct[contains(@Name, 'DesignModule')]/List[contains(@Name, 'PhaseList')]")) > 0) {
                    dl_trial_phase <- xml_text(xml_find_all(dl_trial, "Struct[contains(@Name, 'Study')]/Struct[contains(@Name, 'ProtocolSection')]/Struct[contains(@Name, 'DesignModule')]/List[contains(@Name, 'PhaseList')]"))
                } else {
                    dl_trial_phase <- ""
                }
                
                found_ncts[found_ncts$identifier == dl_trial_nct, "phase"] <- dl_trial_phase
            
                dl_trial_overall_status <- xml_text(xml_find_all(dl_trial, "Struct[contains(@Name, 'Study')]/Struct[contains(@Name, 'ProtocolSection')]/Struct[contains(@Name, 'StatusModule')]/Field[contains(@Name, 'OverallStatus')]"))
                
                found_ncts[found_ncts$identifier == dl_trial_nct, "overall_status"] <- dl_trial_overall_status
                
                dl_trial_primary_completion <- paste(xml_text(xml_find_first(dl_trial, "Struct[contains(@Name, 'Study')]/Struct[contains(@Name, 'ProtocolSection')]/Struct[contains(@Name, 'StatusModule')]/Struct[contains(@Name, 'PrimaryCompletionDateStruct')]/Field[contains(@Name, 'PrimaryCompletionDate')]")))
                
                found_ncts[found_ncts$identifier == dl_trial_nct, "primary_completion"] <- dl_trial_primary_completion
                
                dl_trial_first_posted <- paste(xml_text(xml_find_first(dl_trial, "Struct[contains(@Name, 'Study')]/Struct[contains(@Name, 'ProtocolSection')]/Struct[contains(@Name, 'StatusModule')]/Struct[contains(@Name, 'StudyFirstPostDateStruct')]/Field[contains(@Name, 'StudyFirstPostDate')]")))
                
                found_ncts[found_ncts$identifier == dl_trial_nct, "first_posted"] <- dl_trial_first_posted
                
            }
            
            dl_trials_ncts <- xml_text(xml_find_all(xml, "/FullStudiesResponse/FullStudyList/FullStudy/Struct[contains(@Name, 'Study')]/Struct[contains(@Name, 'ProtocolSection')]/Struct[contains(@Name, 'IdentificationModule')]/Field[contains(@Name, 'NCTId')]"))
            
            for (nct in ncts_to_check$identifier) {
                
                found_ncts[found_ncts$identifier == nct, "clinicaltrials.gov"] <- as.character(nct %in% dl_trials_ncts)
                
            }
            
        }
        
        # Now found_ncts contains all the unique NCT numbers and whether
        # they correspond to a registry entry on clinicaltrials.gov.
        # The following joins these results to the previously saved CSV
        # and over-writes the CSV.
        
        found_identifiers <- read_csv(save_file) %>%
            left_join(found_ncts, by = "identifier")
        
        write_csv(found_identifiers, save_file, append=FALSE)
        
    } else { # Print out an error because the save_file already exists
        
        print (paste("Error:", save_file, "already exists"))
    }
    
}


run_trial_identifier_search('temp/all_text/', 'temp/trials.csv')