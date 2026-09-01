"""
Módulo de exportação de dados.
Exporta dados para XLSX com formatação e CSV com separador ponto-e-vírgula.
"""

import logging
from typing import List, Dict
from pathlib import Path

try:
    import pandas as pd
    from openpyxl import load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:
    pd = None
    load_workbook = None
    PatternFill = None
    Font = None
    Alignment = None
    DataValidation = None


logger = logging.getLogger(__name__)


class ExportHandler:
    """Exporta dados para XLSX e CSV."""
    
    # Ordem das colunas na exportação
    COLUNAS_PRINCIPAIS = ['MUNICIPIO', 'CPF', 'NIS', 'NOME', 'MOTIVO']
    COLUNAS_AUDITORIA = ['ARQUIVO_ORIGEM', 'STATUS_EXTRACAO']
    
    def export_xlsx(self, dados: List[Dict], output_path: str) -> None:
        """
        Exporta dados para XLSX com formatação.
        
        - Cabeçalho congelado
        - Filtro automático
        - CPF e NIS como texto
        - Largura otimizada de colunas
        
        Args:
            dados: Lista de dicionários com os dados
            output_path: Caminho do arquivo de saída
        """
        
        if not pd:
            logger.error("pandas não está instalado. Não é possível exportar para XLSX.")
            raise ImportError("pandas é necessário para exportar XLSX")
        
        # Preparar DataFrame
        df = self._prepare_dataframe(dados, include_audit=True)
        
        # Salvar em XLSX
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Escrever em Excel
            df.to_excel(output_path, index=False, sheet_name='Desligamentos', engine='openpyxl')
            
            # Formatar arquivo
            self._format_xlsx(str(output_path), df)
            
            logger.info(f"XLSX exportado com sucesso: {output_path}")
        
        except Exception as e:
            logger.error(f"Erro ao exportar XLSX: {str(e)}")
            raise
    
    def export_csv(self, dados: List[Dict], output_path: str) -> None:
        """
        Exporta dados para CSV com separador ponto-e-vírgula e encoding UTF-8.
        
        Args:
            dados: Lista de dicionários com os dados
            output_path: Caminho do arquivo de saída
        """
        
        if not pd:
            logger.error("pandas não está instalado. Não é possível exportar para CSV.")
            raise ImportError("pandas é necessário para exportar CSV")
        
        # Preparar DataFrame (sem colunas de auditoria no CSV final)
        df = self._prepare_dataframe(dados, include_audit=False)
        
        # Salvar em CSV
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            df.to_csv(
                output_path,
                sep=';',
                encoding='utf-8',
                index=False,
                quoting=1  # QUOTE_ALL - aspas em todos os campos
            )
            
            logger.info(f"CSV exportado com sucesso: {output_path}")
        
        except Exception as e:
            logger.error(f"Erro ao exportar CSV: {str(e)}")
            raise
    
    def _prepare_dataframe(self, dados: List[Dict], include_audit: bool = False) -> 'pd.DataFrame':
        """
        Prepara DataFrame com formatação apropriada.
        
        Args:
            dados: Lista de dicionários
            include_audit: Incluir colunas de auditoria
            
        Returns:
            DataFrame formatado
        """
        
        # Definir ordem das colunas
        if include_audit:
            colunas = self.COLUNAS_PRINCIPAIS + self.COLUNAS_AUDITORIA
        else:
            colunas = self.COLUNAS_PRINCIPAIS
        
        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        # Garantir que todas as colunas existem (com valores vazios se necessário)
        for col in colunas:
            if col not in df.columns:
                df[col] = ""
        
        # Reordenar colunas
        df = df[colunas]
        
        # Converter CPF e NIS para texto (preservar zeros à esquerda)
        if 'CPF' in df.columns:
            df['CPF'] = df['CPF'].astype(str)
        if 'NIS' in df.columns:
            df['NIS'] = df['NIS'].astype(str)
        
        return df
    
    @staticmethod
    def _format_xlsx(file_path: str, df: 'pd.DataFrame') -> None:
        """
        Formata arquivo XLSX com:
        - Cabeçalho congelado
        - Filtro automático
        - Largura otimizada de colunas
        - Formatação de cells como texto para CPF/NIS
        
        Args:
            file_path: Caminho do arquivo XLSX
            df: DataFrame com os dados
        """
        
        if not load_workbook or not PatternFill or not Font or not Alignment:
            logger.warning("openpyxl não está instalado. Formatação XLSX limitada.")
            return
        
        try:
            workbook = load_workbook(file_path)
            worksheet = workbook.active
            
            # Congelar linha de cabeçalho
            worksheet.freeze_panes = 'A2'
            
            # Adicionar filtro automático
            worksheet.auto_filter.ref = f"A1:{chr(64 + len(df.columns))}{len(df) + 1}"
            
            # Formatar cabeçalho
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            
            for cell in worksheet[1]:
                if cell.value:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Ajustar largura das colunas
            for col_num, col_title in enumerate(df.columns, 1):
                col_letter = chr(64 + col_num)
                max_length = len(str(col_title))
                
                # Verificar tamanho do conteúdo
                for row in worksheet.iter_rows(min_row=2, max_row=len(df) + 1, min_col=col_num, max_col=col_num):
                    for cell in row:
                        try:
                            max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                
                # Definir largura (com margem)
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[col_letter].width = adjusted_width
            
            # Formatar CPF e NIS como texto
            for row_num, row in enumerate(worksheet.iter_rows(min_row=2, max_row=len(df) + 1), 1):
                for col_num, cell in enumerate(row, 1):
                    col_title = df.columns[col_num - 1]
                    
                    # Formatar como texto para CPF e NIS
                    if col_title in ['CPF', 'NIS']:
                        cell.number_format = '@'  # Formato de texto
            
            # Salvar arquivo formatado
            workbook.save(file_path)
            logger.debug(f"Arquivo XLSX formatado: {file_path}")
        
        except Exception as e:
            logger.warning(f"Erro ao formatar XLSX: {str(e)}. Arquivo salvo sem formatação completa.")
