class PyStatsError(Exception):
    """Base exception for PyStats application"""
    pass

class DataLoadError(PyStatsError):
    """Exception raised when data loading fails"""
    pass

class ModelTrainingError(PyStatsError):
    """Exception raised when model training fails"""
    pass

class RankingCalculationError(PyStatsError):
    """Exception raised when ranking calculation fails"""
    pass