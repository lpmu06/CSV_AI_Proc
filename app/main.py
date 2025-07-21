from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path
from loguru import logger
from app.core.config import settings
from app.services.csv_processor import CSVProcessor

# Initialize FastAPI app
app = FastAPI(
    title="CSV Automation API",
    description="API para automação de processamento de dados CSV com IA",
    version="1.0.0"
)

# Initialize CSV processor
csv_processor = CSVProcessor()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting CSV Automation API")
    # Ensure data directories exist
    Path(settings.CSV_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "CSV Automation API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "csv-automation"}

@app.post("/process-csv")
async def process_csv(file: UploadFile = File(...)):
    """Process CSV file with AI enrichment"""
    try:
        # Validate file
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Save uploaded file
        input_path = Path(settings.CSV_STORAGE_PATH) / f"input_{file.filename}"
        
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Processing CSV file: {file.filename}")
        
        # Process CSV with AI
        output_path = await csv_processor.process_file(input_path)
        
        # Return processed file
        return FileResponse(
            path=output_path,
            filename=f"enriched_{file.filename}",
            media_type="text/csv"
        )
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/files")
async def list_files():
    """List available files in storage"""
    try:
        storage_path = Path(settings.CSV_STORAGE_PATH)
        files = [f.name for f in storage_path.glob("*.csv")]
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing files")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT) 