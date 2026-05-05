"""Constants for ai-multitool configuration."""

# Memory limits
DEFAULT_MAX_METRICS = 10000
DEFAULT_MAX_CHUNKS = 10000
DEFAULT_CACHE_MAX_SIZE = 1000
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds

# LLM configuration
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 120  # seconds
DEFAULT_MODEL = "claude-3-sonnet-20240229"

# RAG configuration
DEFAULT_EMBEDDING_DIMENSION = 1536
DEFAULT_TOP_K = 5
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

# Rate limiting
DEFAULT_RATE_LIMIT = 60  # requests per minute
DEFAULT_RATE_LIMIT_PER = 60.0  # seconds

# Validation limits
MAX_TOKENS_LIMIT = 100000
MAX_TIMEOUT_LIMIT = 600  # seconds
MIN_API_KEY_LENGTH = 10
TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 2.0

# File patterns
DEFAULT_FILE_PATTERN = "*.md"
DEFAULT_CODE_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.c', '.cpp', '.go', '.rs'}

# API providers
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_OPENAI = "openai"
PROVIDER_LITELLM = "litellm"

# Tool categories
TOOL_CATEGORY_CODE_ANALYSIS = "code_analysis"
TOOL_CATEGORY_RAG = "rag"
TOOL_CATEGORY_GIT = "git"
TOOL_CATEGORY_FILE_OPERATIONS = "file_operations"
TOOL_CATEGORY_GENERAL = "general"

# Status codes
STATUS_SUCCESS = "success"
STATUS_PARTIAL = "partial"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"

# Error messages
ERROR_API_KEY_REQUIRED = "API key is required"
ERROR_MESSAGES_EMPTY = "Messages list cannot be empty"
ERROR_PATH_EMPTY = "Path cannot be empty"
ERROR_QUERY_EMPTY = "Query cannot be empty"

# Log levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"
