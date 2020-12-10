args <- commandArgs(TRUE)
PDF_text_sentences <- oddpub::pdf_load(args[1])
open_data_results <- oddpub::open_data_search(PDF_text_sentences)
write.table(open_data_results, file=args[2])