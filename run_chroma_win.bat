@echo off
cd /d C:\Users\genna\repository

call conda activate chromaenv
python src\generate_chroma_motif_scaffolds.py

echo.
echo === CHROMA MOTIF GENERATION FINISHED ===
pause

echo on