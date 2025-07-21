import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from loguru import logger
from app.core.config import settings
import json
import asyncio

class CSVProcessor:
    """CSV processor with AI enrichment"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Load enrichment prompt
        self.enrichment_prompt = self._load_enrichment_prompt()
    
    def _load_enrichment_prompt(self) -> str:
        """Load the enrichment prompt from our universal template"""
        return """TASK: Enrich vehicle product data from CSV format for API optimization

INPUT: Raw CSV file with semicolon-separated product data
OUTPUT: Enriched CSV maintaining same structure with applied transformations

TRANSFORMATION RULES:

1. PRODUCT_NAME (column 3):
   PATTERN: "ProductName Model Material Brand Genuino/Original"
   
   FROM: "Produto Tipo Genuina/Genuino/Original Marca Modelo/Aplicacao"
   TO: "Produto Modelo Material Marca Genuino/Original"
   
   RULES:
   - Remove redundant words: "fixador", "de cambio", directional terms when contextual
   - Add material from technical description:
     Aco: metallic products (parafusos, porcas, valvulas, engrenagens, molas)
     Aluminio: covers, heads, motor components  
     Plastico: caps, fenders, fairings, covers
   - Reorganize order: base name + model + material + brand + authenticity
   - Replace "/" with spaces
   - Simplify terms by removing redundant words

2. PRICE_FORMAT (column 9):
   Always use 2 decimal places
   9 → 9.00
   199 → 199.00  
   93.66 → 93.66 (preserve existing decimals)

3. ADDITIONAL_DESC_1 (column 14):
   Replace all text with: "incluir texto"

4. DATE_UPDATE (column 15):
   Find existing date patterns in format: "Data: DD/MM/YYYY"
   Replace with current processing date or specified target date
   Preserve all other content in description

5. DATA_CORRECTIONS:
   Apply corrections based on patterns for dimensions and weight consistency

6. HEADER_CLEANUP:
   Remove last duplicate field if present (commonly "NCM")
   Preserve all other fields

CONSTRAINTS:
- Do not alter structural data (IDs, codes, references)
- Maintain system compatibility  
- Ensure valid CSV output
- Apply all rules consistently regardless of brand
- Preserve original brand and authenticity information

Process the CSV data following these exact rules."""

    async def process_file(self, input_path: Path) -> Path:
        """Process CSV file with AI enrichment"""
        try:
            logger.info(f"Starting processing of {input_path}")
            
            # Read CSV
            df = pd.read_csv(input_path, sep=';', encoding='utf-8')
            logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
            
            # Process in batches for large files
            batch_size = 10
            processed_rows = []
            
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                processed_batch = await self._process_batch(batch)
                processed_rows.extend(processed_batch)
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(df)-1)//batch_size + 1}")
            
            # Create output DataFrame
            output_df = pd.DataFrame(processed_rows)
            
            # Generate output path
            output_path = input_path.parent / f"enriched_{input_path.name}"
            
            # Save enriched CSV
            output_df.to_csv(output_path, sep=';', index=False, encoding='utf-8')
            logger.info(f"Saved enriched CSV to {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing file {input_path}: {str(e)}")
            raise
    
    async def _process_batch(self, batch: pd.DataFrame) -> List[Dict]:
        """Process a batch of rows with AI"""
        try:
            # Convert batch to JSON for AI processing
            batch_json = batch.to_json(orient='records', force_ascii=False)
            
            # Prepare prompt
            full_prompt = f"{self.enrichment_prompt}\n\nCSV DATA TO PROCESS:\n{batch_json}\n\nReturn only the processed JSON data with the same structure but enriched according to the rules."
            
            # Call LLM
            response = await asyncio.to_thread(
                self.llm.invoke,
                [HumanMessage(content=full_prompt)]
            )
            
            # Parse response
            try:
                # Try to extract JSON from response
                response_text = response.content.strip()
                if response_text.startswith('```json'):
                    response_text = response_text.split('```json')[1].split('```')[0]
                elif response_text.startswith('```'):
                    response_text = response_text.split('```')[1].split('```')[0]
                
                processed_data = json.loads(response_text)
                
                # Ensure it's a list
                if isinstance(processed_data, dict):
                    processed_data = [processed_data]
                
                return processed_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.error(f"Response was: {response.content}")
                # Fallback: return original data
                return batch.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            # Fallback: return original data
            return batch.to_dict('records')
    
    def validate_output(self, original_df: pd.DataFrame, processed_df: pd.DataFrame) -> bool:
        """Validate processed output"""
        try:
            # Check row count
            if len(original_df) != len(processed_df):
                logger.warning(f"Row count mismatch: {len(original_df)} vs {len(processed_df)}")
                return False
            
            # Check essential columns exist
            required_cols = ['ID_produto', 'Nome do Produto (BR)', 'Preço (Padrão (BRL))']
            missing_cols = [col for col in required_cols if col not in processed_df.columns]
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                return False
            
            logger.info("Output validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False 