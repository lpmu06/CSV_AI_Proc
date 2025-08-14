from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import Dict, Any, Optional
from loguru import logger
from app.core.config import settings
from datetime import datetime
import json
import re



class AIProductEnrichmentAgent:
    """AI Agent for automotive parts data enrichment using LangChain"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name="gpt-4o-mini",
            temperature=0.1,
            max_tokens=4000
        )
        
        # Set up the output parser
        self.parser = StrOutputParser()
        
        # Create the prompt template
        self.prompt = self._create_prompt_template()
        
        # Create the processing chain
        self.chain = self._create_processing_chain()
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template for data enrichment"""
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        system_message = f"""
        Você é um especialista em peças automotivas Honda. Siga EXATAMENTE as regras de negócio abaixo:

        REGRAS DE ENRIQUECIMENTO:
        1. Nome da categoria: Categorize corretamente (ex: Parafusos Moto, Kit Revisão Moto, Carroceria Moto)
        2. Peso: Estime peso realista em kg baseado no tipo de peça
        3. Dimensões: Altura, Comprimento, Largura em cm - valores realistas
        4. NCM: Use código fiscal correto:
           - Parafusos: 7318.15.00
           - Porcas: 7318.16.00  
           - Arruelas: 7318.22.00
           - Válvulas motor: 8409.91.90
           - Peças moto gerais: 8714.19.00
           - Espelhos: 7009.10.00
           - Engrenagens: 8483.40.10
           - Peças plásticas: 3926.90.90

        TEMPLATE DESCRIÇÃO ADICIONAL 2 (uma linha única):
        "Descrição do Produto: [descrição limpa] Aplicação (Compatibilidade de Modelos e Ano): [modelos Honda] Descrição Técnica: [especificações] Marca: Honda Garantia: 3 meses Data: {current_date} Conteúdo da Embalagem: 1 UND de [produto] Dimensões em cm (Altura x Comprimento x Largura): [A]x[C]x[L] Peso (kg): [peso] Código SKU: [sku] Código do Fabricante/Referência: [ref] NCM: [ncm] Descrição NCM: [desc_ncm] Op: LK"

        IMPORTANTE: 
        - Retorne APENAS JSON válido
        - Descrição adicional 2 deve ser UMA LINHA única
        - Use categorias específicas, não genéricas
        - Dimensões e peso devem ser realistas para o tipo de peça
        """
        
        human_message = """
        Enriqueça os seguintes dados de peça automotiva Honda:

        Referência: {referencia}
        Descrição: {descricao}
        Quantidade Estoque: {quantidade}
        Preço de Venda: {preco_venda}
        Preço de Custo: {preco_custo}
        SKU: {sku}
        EAN: {ean}

        Retorne um JSON válido com esta estrutura exata:
        {{
            "nome_categoria": "categoria específica (ex: Peças de Freio Moto, Fixação Moto, Parafusos Moto)",
            "peso": "peso estimado em kg",
            "altura": "altura em cm",
            "comprimento": "comprimento em cm", 
            "largura": "largura em cm",
            "ncm": "código NCM apropriado",
            "descricao_adicional_2": "template completo em UMA LINHA SEM quebras - substitua \\n por espaços"
        }}
        
        IMPORTANTE: 
        - A descrição_adicional_2 deve estar em UMA LINHA ÚNICA
        - Substitua todas as quebras de linha por espaços
        - Use categorias específicas baseadas no tipo de peça
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    def _create_processing_chain(self):
        """Create the LangChain processing chain"""
        return (
            RunnablePassthrough()
            | self.prompt
            | self.llm
            | self.parser
        )
    
    async def enrich_product_data(self, product_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Enrich product data using AI
        
        Args:
            product_data: Dictionary with keys: referencia, descricao, quantidade, 
                         preco_venda, preco_custo, sku, ean
        
        Returns:
            Dictionary with enriched product data
        """
        try:
            logger.info(f"Enriching product data for SKU: {product_data.get('sku', 'Unknown')}")
            
            # Clean and prepare input data
            cleaned_data = self._clean_input_data(product_data)
            
            # Process with AI
            result = await self.chain.ainvoke(cleaned_data)
            
            # Parse AI response
            ai_data = self._parse_ai_response(result)
            
            # Convert to final CSV format
            csv_data = self._convert_to_csv_format(ai_data, cleaned_data)
            
            logger.info(f"Successfully enriched data for SKU: {cleaned_data.get('sku', 'Unknown')}")
            return csv_data
            
        except Exception as e:
            logger.error(f"Error enriching product data: {str(e)}")
            # Return fallback data
            return self._create_fallback_data(product_data)
    
    def _clean_input_data(self, data: Dict[str, str]) -> Dict[str, str]:
        """Clean and validate input data"""
        cleaned = {}
        
        for key, value in data.items():
            if value is None:
                cleaned[key] = ""
            else:
                cleaned[key] = str(value).strip()
        
        # Clean price formats
        for price_field in ['preco_venda', 'preco_custo']:
            if price_field in cleaned:
                cleaned[price_field] = self._clean_price(cleaned[price_field])
        
        return cleaned
    
    def _clean_price(self, price_str: str) -> str:
        """Clean price string to decimal format"""
        if not price_str:
            return "0.00"
        
        # Remove R$, spaces, and convert comma to dot
        cleaned = price_str.replace('R$', '').replace(' ', '').replace(',', '.')
        
        try:
            float_price = float(cleaned)
            return f"{float_price:.2f}"
        except ValueError:
            return "0.00"
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON data"""
        try:
            # Clean response - remove markdown formatting if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            parsed_data = json.loads(cleaned_response)
            return parsed_data
            
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse AI response as JSON: {str(e)}")
            logger.debug(f"Raw response: {response}")
            return {}
    
    def _convert_to_csv_format(self, enriched_data: Dict, original_data: Dict) -> Dict[str, Any]:
        """Convert enriched data to CSV format with all required fields"""
        
        # Base data combining original + AI enrichment
        csv_data = {
            "ID_produto": original_data.get("sku", ""),
            "ID_OEM": original_data.get("referencia", ""),
            "Nome do Produto (BR)": self._create_product_name(original_data.get('descricao', ''))[:60],
            "ID do Fabricante": original_data.get("referencia", ""),
            "Quantidade (Padrão)": original_data.get("quantidade", ""),
            "EAN": original_data.get("ean", ""),
            "SKU": original_data.get("sku", ""),
            "Nome da categoria": enriched_data.get("nome_categoria", "Peças Automotivas"),
            "Preço (Padrão (BRL))": self._clean_price(original_data.get("preco_venda", "0")),
            "Preço de Compra": self._clean_price(original_data.get("preco_custo", "0")),
            "Custo (médio)": self._clean_price(original_data.get("preco_custo", "0")),
            "Peso": enriched_data.get("peso", "0.10"),
            "Descrição (BR)": f"{original_data.get('descricao', '')} SKU: LK {original_data.get('sku', '')}",
            "Descrição adicional 1 (BR)": "incluir texto",
            "Descrição adicional 2 (BR)": self._clean_description_2(enriched_data.get("descricao_adicional_2", self._create_default_description_2(original_data))),
            "Nome do fabricante": "Honda",
            "Altura": enriched_data.get("altura", "5.0"),
            "Comprimento": enriched_data.get("comprimento", "10.0"),
            "Largura": enriched_data.get("largura", "5.0"),
        }
        
        # Add fixed fields
        fixed_fields = {
            "Campo adicional - Tipo de unidade": "un",
            "Tipo de unidade": "un",
            "Campo adicional - Código da origem": "0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8",
            "Código da origem": "0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8",
            "Campo adicional - Código do fabricante": original_data.get("referencia", ""),
            "Código do fabricante": original_data.get("referencia", ""),
            "Parâmetro - NCM (BR)": enriched_data.get("ncm", "8714.19.00"),
            "NCM": enriched_data.get("ncm", "8714.19.00"),
            "Parâmetro - Origin Type (BR)": "0",
            "Parâmetro - Origin Detail (BR)": "Reseller",
            "Campo adicional - NCM": enriched_data.get("ncm", "8714.19.00")
        }
        
        csv_data.update(fixed_fields)
        
        return csv_data
    
    def _create_default_description_2(self, original_data: Dict) -> str:
        """Create default description 2 template in single line"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Create template following EXACT business rules format
        desc_clean = self._extract_product_description(original_data.get('descricao', ''))
        
        template = f"Descrição do Produto: {desc_clean} " \
                  f"Aplicação (Compatibilidade de Modelos e Ano): Modelos Honda compatíveis " \
                  f"Descrição Técnica: Peça original Honda de alta qualidade " \
                  f"Marca: Honda " \
                  f"Garantia: 3 meses " \
                  f"Data: {current_date} " \
                  f"Conteúdo da Embalagem: 1 UND de {desc_clean} " \
                  f"Dimensões em cm (Altura x Comprimento x Largura): 5.0x10.0x5.0 " \
                  f"Peso (kg): 0.10 " \
                  f"Código SKU: {original_data.get('sku', '')} " \
                  f"Código do Fabricante/Referência: {original_data.get('referencia', '')} " \
                  f"NCM: 8714.19.00 " \
                  f"Descrição NCM: Partes e acessórios de motocicletas " \
                  f"Op: LK"
        
        return template
    
    def _extract_product_description(self, description: str) -> str:
        """Extract clean product description removing reference numbers"""
        import re
        
        # Remove reference number if description starts with it
        match = re.match(r'^[\d\w]+\s+(.+)$', description)
        if match:
            return match.group(1)
        
        return description
    
    def _clean_description_2(self, description: str) -> str:
        """Clean description 2 to ensure single line"""
        if not description:
            return ""
        
        # Replace all line breaks with spaces
        cleaned = description.replace('\n', ' ').replace('\r', ' ')
        
        # Replace multiple spaces with single space
        import re
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Strip leading/trailing spaces
        return cleaned.strip()
    
    def _create_product_name(self, description: str) -> str:
        """Create product name following business rules"""
        # Remove reference number from description if present
        desc_clean = description
        
        # Extract the actual product description (remove reference if it starts with numbers)
        import re
        match = re.match(r'^[\d\w]+\s+(.+)$', desc_clean)
        if match:
            desc_clean = match.group(1)
        
        # Format: Product description + "Honda Genuíno"
        return f"{desc_clean} Honda Genuíno"
    
    def _create_fallback_data(self, original_data: Dict) -> Dict[str, Any]:
        """Create fallback data when AI processing fails"""
        logger.warning(f"Creating fallback data for SKU: {original_data.get('sku', 'Unknown')}")
        
        return {
            "ID_produto": original_data.get("sku", ""),
            "ID_OEM": original_data.get("referencia", ""),
            "Nome do Produto (BR)": f"{original_data.get('descricao', '')} Honda Genuíno"[:60],
            "ID do Fabricante": original_data.get("referencia", ""),
            "Quantidade (Padrão)": original_data.get("quantidade", "0"),
            "EAN": original_data.get("ean", ""),
            "SKU": original_data.get("sku", ""),
            "Nome da categoria": "Peças Automotivas",
            "Preço (Padrão (BRL))": self._clean_price(original_data.get("preco_venda", "0")),
            "Preço de Compra": self._clean_price(original_data.get("preco_custo", "0")),
            "Custo (médio)": self._clean_price(original_data.get("preco_custo", "0")),
            "Peso": "0.10",
            "Descrição (BR)": f"{original_data.get('descricao', '')} SKU: LK {original_data.get('sku', '')}",
            "Descrição adicional 1 (BR)": "incluir texto",
            "Descrição adicional 2 (BR)": self._create_default_description_2(original_data),
            "Nome do fabricante": "Honda",
            "Altura": "5.0",
            "Comprimento": "10.0",
            "Largura": "5.0",
            "Campo adicional - Tipo de unidade": "un",
            "Tipo de unidade": "un",
            "Campo adicional - Código da origem": "0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8",
            "Código da origem": "0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8",
            "Campo adicional - Código do fabricante": original_data.get("referencia", ""),
            "Código do fabricante": original_data.get("referencia", ""),
            "Parâmetro - NCM (BR)": "8714.19.00",
            "NCM": "8714.19.00",
            "Parâmetro - Origin Type (BR)": "0",
            "Parâmetro - Origin Detail (BR)": "Reseller",
            "Campo adicional - NCM": "8714.19.00"
        }