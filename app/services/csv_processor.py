import pandas as pd
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger
from app.core.config import settings
from app.services.ai_agent import AIProductEnrichmentAgent
from datetime import datetime

class CSVProcessor:
    """CSV processing service with AI enrichment using LangChain"""
    
    def __init__(self):
        self.ai_agent = AIProductEnrichmentAgent()
    

    
    async def process_file(self, input_path: Path) -> Path:
        """Process CSV file with AI enrichment"""
        try:
            logger.info(f"Starting processing of file: {input_path}")
            
            # Read input CSV
            df = pd.read_csv(input_path)
            logger.info(f"Loaded {len(df)} rows from CSV")
            
            # Process each row
            enriched_rows = []
            for index, row in df.iterrows():
                logger.info(f"Processing row {index + 1}/{len(df)}")
                enriched_data = await self._enrich_row(row)
                if enriched_data:
                    enriched_rows.append(enriched_data)
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            
            # Create output CSV
            output_path = self._create_output_csv(enriched_rows, input_path)
            logger.info(f"Successfully created enriched CSV: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing file {input_path}: {str(e)}")
            raise
    
    async def _enrich_row(self, row: pd.Series) -> Dict[str, Any]:
        """Enrich a single row of data using AI"""
        try:
            # Prepare input data
            input_data = {
                "referencia": str(row.get('Referencia', '')),
                "descricao": str(row.get('Descricao', '')),
                "quantidade": str(row.get('Quantidade Estoque', '')),
                "preco_venda": str(row.get('Preço de Venda', '')),
                "preco_custo": str(row.get('Preço de Custo', '')),
                "sku": str(row.get('SKU', '')),
                "ean": str(row.get('EAN', ''))
            }
            
            # Process with AI agent
            enriched_data = await self.ai_agent.enrich_product_data(input_data)
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Error enriching row: {str(e)}")
            # Return fallback data
            return self._create_fallback_data(row)
    

    
    def _create_fallback_data(self, row_data) -> Dict[str, Any]:
        """Create fallback data when AI processing fails"""
        if isinstance(row_data, pd.Series):
            original_data = {
                "referencia": str(row_data.get('Referencia', '')),
                "descricao": str(row_data.get('Descricao', '')),
                "quantidade": str(row_data.get('Quantidade Estoque', '')),
                "preco_venda": str(row_data.get('Preço de Venda', '')),
                "preco_custo": str(row_data.get('Preço de Custo', '')),
                "sku": str(row_data.get('SKU', '')),
                "ean": str(row_data.get('EAN', ''))
            }
        else:
            original_data = row_data
        
        # Use AI agent fallback method
        return self.ai_agent._create_fallback_data(original_data)
    
    def _create_output_csv(self, enriched_rows: List[Dict], input_path: Path) -> Path:
        """Create output CSV file with enriched data"""
        if not enriched_rows:
            raise ValueError("No enriched data to write")
        
        # Create DataFrame
        df = pd.DataFrame(enriched_rows)
        
        # Define output path
        output_path = input_path.parent / f"enriched_{input_path.name}"
        
        # Write CSV with proper formatting - no quotes on headers, minimal quoting
        df.to_csv(
            output_path,
            sep=';',
            index=False,
            encoding='utf-8',
            quoting=0,  # No quoting
            lineterminator='\n'  # Ensure proper line endings
        )
        
        return output_path