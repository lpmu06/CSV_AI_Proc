from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal

class CSVInputRow(BaseModel):
    """Model for input CSV row data"""
    referencia: str = Field(..., description="Referência da peça")
    descricao: str = Field(..., description="Descrição da peça")
    quantidade_estoque: int = Field(..., description="Quantidade em estoque")
    preco_venda: str = Field(..., description="Preço de venda")
    preco_custo: str = Field(..., description="Preço de custo")
    sku: str = Field(..., description="SKU do produto")
    ean: str = Field(..., description="Código EAN")
    
    @validator('preco_venda', 'preco_custo')
    def validate_price(cls, v):
        """Validate price format"""
        if not v:
            return "0.00"
        # Clean price string
        cleaned = str(v).replace('R$', '').replace(' ', '').replace(',', '.')
        try:
            float(cleaned)
            return cleaned
        except ValueError:
            return "0.00"

class CSVOutputRow(BaseModel):
    """Model for output CSV row data"""
    id_produto: str = Field(..., alias="ID_produto")
    id_oem: str = Field(..., alias="ID_OEM")
    nome_produto_br: str = Field(..., alias="Nome do Produto (BR)", max_length=60)
    id_fabricante: str = Field(..., alias="ID do Fabricante")
    quantidade_padrao: str = Field(..., alias="Quantidade (Padrão)")
    ean: str = Field(..., alias="EAN")
    sku: str = Field(..., alias="SKU")
    nome_categoria: str = Field(..., alias="Nome da categoria")
    preco_padrao_brl: str = Field(..., alias="Preço (Padrão (BRL))")
    preco_compra: str = Field(..., alias="Preço de Compra")
    custo_medio: str = Field(..., alias="Custo (médio)")
    peso: str = Field(..., alias="Peso")
    descricao_br: str = Field(..., alias="Descrição (BR)")
    descricao_adicional_1: str = Field(..., alias="Descrição adicional 1 (BR)")
    descricao_adicional_2: str = Field(..., alias="Descrição adicional 2 (BR)")
    nome_fabricante: str = Field(..., alias="Nome do fabricante")
    altura: str = Field(..., alias="Altura")
    comprimento: str = Field(..., alias="Comprimento")
    largura: str = Field(..., alias="Largura")
    campo_adicional_tipo_unidade: str = Field(..., alias="Campo adicional - Tipo de unidade")
    tipo_unidade: str = Field(..., alias="Tipo de unidade")
    campo_adicional_codigo_origem: str = Field(..., alias="Campo adicional - Código da origem")
    codigo_origem: str = Field(..., alias="Código da origem")
    campo_adicional_codigo_fabricante: str = Field(..., alias="Campo adicional - Código do fabricante")
    codigo_fabricante: str = Field(..., alias="Código do fabricante")
    parametro_ncm_br: str = Field(..., alias="Parâmetro - NCM (BR)")
    ncm: str = Field(..., alias="NCM")
    parametro_origin_type_br: str = Field(..., alias="Parâmetro - Origin Type (BR)")
    parametro_origin_detail_br: str = Field(..., alias="Parâmetro - Origin Detail (BR)")
    campo_adicional_ncm: str = Field(..., alias="Campo adicional - NCM")
    
    class Config:
        allow_population_by_field_name = True

class ProcessingStatus(BaseModel):
    """Model for processing status"""
    status: str = Field(..., description="Status do processamento")
    message: str = Field(..., description="Mensagem de status")
    processed_rows: Optional[int] = Field(None, description="Número de linhas processadas")
    total_rows: Optional[int] = Field(None, description="Total de linhas")
    output_file: Optional[str] = Field(None, description="Caminho do arquivo de saída")

class EmailProcessingRequest(BaseModel):
    """Model for email processing request"""
    email_subject: Optional[str] = Field(None, description="Assunto do email")
    sender: Optional[str] = Field(None, description="Remetente do email")
    attachment_name: str = Field(..., description="Nome do anexo CSV")
    processing_timestamp: Optional[str] = Field(None, description="Timestamp do processamento")