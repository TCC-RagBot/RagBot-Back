"""
Configurações compartilhadas para os testes
"""
import os
import sys
from pathlib import Path
import pytest # type: ignore
from unittest.mock import MagicMock

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configurações de teste
TEST_PDF_PATH = project_root / "pdf-test.pdf"
MOCK_DATABASE = True

@pytest.fixture
def test_pdf_path():
    """Fixture que retorna o caminho para o PDF de teste"""
    return str(TEST_PDF_PATH)

@pytest.fixture
def mock_database():
    """Fixture para mockar operações de banco de dados durante os testes"""
    return MagicMock()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup global para os testes"""
    # Configurar variáveis de ambiente para teste
    os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
    os.environ.setdefault("GOOGLE_API_KEY", "test-key")